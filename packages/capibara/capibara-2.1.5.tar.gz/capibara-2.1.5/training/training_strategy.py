"""Entrenamiento Distribuido CapibaraGPT para TPU v4-32 (v3.1)"""

import jax 
import jax.numpy as jnp 
import flax.linen as nn 
import optax 
from flax.training import train_state 
from jax.experimental import mesh_utils, shard_map 
from jax.sharding import PartitionSpec as P 
import orbax.checkpoint as ocp #type: ignore
import tensorflow as tf 
import numpy as np #type: ignore
import logging
import os
from datetime import datetime
from functools import partial
from typing import Any, Dict, Iterator, Tuple, cast
from dataclasses import dataclass
from capibara.core.model import DynamicCapibaraModel as BaseCapibaraModel
from capibara.layers.embedding import CapibaraEmbedding
from capibara.config.distribution_config import create_unified_mesh, TPU_DTYPE

# Configuración Global
logger = logging.getLogger(__name__)
jax.config.update('jax_threefry_partitionable', True)

# 1. Configuración de Hardware
TPU_MESH = None  # Will be initialized in setup
BATCH_SHARDING = P('batch')
MODEL_SHARDING = P('model')
DTYPE = jnp.float32
SAVE_INTERVAL = 1000  # Pasos entre checkpoints

@dataclass(frozen=True)
class TrainingConfig:
    # Hiperparámetros
    batch_size: int = 131072       # 128k muestras por paso
    seq_length: int = 2048
    hidden_size: int = 8192
    num_layers: int = 24
    learning_rate: float = 3e-4
    warmup_steps: int = 10000
    dropout: float = 0.1
    weight_decay: float = 0.01
    grad_clip: float = 1.0

    # Configuración de datos
    data_path: str = "gs://capibara-bucket/tpu_optimized"
    cache_dir: str = "/tpu_cache"
    num_train_samples: int = int(1e9)

class TPUCapibaraModel(BaseCapibaraModel):
    """Arquitectura Principal con Sharding Automático para TPU"""
    
    def setup(self) -> None:
        """Initialize TPU-specific components and call parent setup."""
        super().setup()
        
        # Configuración TPU
        self.mesh = create_unified_mesh()
        self.dtype = TPU_DTYPE
        
        # Componentes con sharding
        self.embedding = CapibaraEmbedding(
            vocab_size=self.config.vocab_size,
            hidden_size=self.config.hidden_size,
            max_length=self.config.max_length,
            dtype=self.dtype
        )
        
        # Transformer blocks con sharding
        self.transformer_blocks = [
            TransformerBlock(
                config=self.config,
                name=f'transformer_block_{i}'
            ) for i in range(self.config.num_layers)
        ]
        
        # Normalización y dropout
        self.norm = nn.LayerNorm(
            epsilon=self.config.dropout_rate,
            dtype=self.dtype
        )
        self.dropout = nn.Dropout(
            rate=self.config.dropout_rate,
            dtype=self.dtype
        )

    @nn.compact  # type: ignore
    def __call__(self, inputs: jnp.ndarray, training: bool = False) -> jnp.ndarray:
        """
        Forward pass con sharding automático para TPU.
        
        Args:
            inputs: Tensor de entrada (batch, seq_len, hidden_size)
            training: Si estamos en modo entrenamiento
            
        Returns:
            Tensor de salida con la misma forma que la entrada
        """
        # Aplicar sharding a los embeddings
        x = shard_map(
            lambda x: nn.Dense(
                self.hidden_size,
                kernel_init=nn.initializers.lecun_normal(),
                dtype=DTYPE
            )(x),
            mesh=TPU_MESH,
            in_specs=BATCH_SHARDING,
            out_specs=BATCH_SHARDING,
            check_rep=False
        )(inputs)
        
        # Procesar con la implementación base
        outputs = super().__call__(x, training=training)
        
        # Si estamos monitoreando métricas, devolver el diccionario completo
        if isinstance(outputs, dict):
            return outputs
            
        # Si no, aplicar sharding a la capa final
        return shard_map(  # type: ignore
            lambda x: nn.Dense(
                self.hidden_size,
                kernel_init=nn.initializers.zeros,
                dtype=DTYPE
            )(x),
            mesh=TPU_MESH,
            in_specs=BATCH_SHARDING,
            out_specs=BATCH_SHARDING,
            check_rep=False
        )(outputs)

class TransformerBlock(nn.Module):
    """Bloque Transformer Optimizado para TPU"""
    
    config: TrainingConfig

    @nn.compact  # type: ignore
    def __call__(self, x: jnp.ndarray, training: bool) -> jnp.ndarray:
        # Atención
        attn_out = shard_map(
            lambda x: nn.SelfAttention(
                num_heads=32,
                dropout_rate=self.config.dropout,
                dtype=DTYPE
            )(x, deterministic=not training),
            mesh=TPU_MESH,
            in_specs=BATCH_SHARDING,
            out_specs=BATCH_SHARDING,
            check_rep=False
        )
        
        x = x + attn_out
        
        # FFN
        ffn_out = shard_map(
            lambda x: nn.Sequential([
                nn.Dense(4*self.config.hidden_size, dtype=DTYPE),
                nn.gelu,
                nn.Dropout(self.config.dropout, deterministic=not training),
                nn.Dense(self.config.hidden_size, dtype=DTYPE)
            ])(x),
            mesh=TPU_MESH,
            in_specs=BATCH_SHARDING,
            out_specs=BATCH_SHARDING,
            check_rep=False
        )
        
        return x + ffn_out

class TPUDataLoader:
    """Cargador de datos optimizado para TPU"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self._build_pipelines()

    def _build_pipelines(self) -> None:
        """Construye pipelines de datos optimizados"""
        train_files = tf.io.gfile.glob(f"{self.config.data_path}/train/*.tfrecord")
        val_files = tf.io.gfile.glob(f"{self.config.data_path}/val/*.tfrecord")
        
        self.train_dataset = self._create_dataset(train_files, is_train=True)
        self.val_dataset = self._create_dataset(val_files, is_train=False)

    def _create_dataset(self, files: list, is_train: bool) -> tf.data.Dataset:
        """Crea dataset optimizado para TPU"""
        dataset = tf.data.TFRecordDataset(files)
        dataset = dataset.map(self._parse_example, num_parallel_calls=tf.data.AUTOTUNE)
        dataset = dataset.batch(self.config.batch_size)
        dataset = dataset.prefetch(tf.data.AUTOTUNE)
        return dataset

    def _parse_example(self, example: tf.Tensor) -> Dict[str, tf.Tensor]:
        """Parsea ejemplos y aplica procesamiento de bytes optimizado"""
        feature_description = {
            'input_bytes': tf.io.FixedLenFeature([], tf.string),
            'target_bytes': tf.io.FixedLenFeature([], tf.string)
        }
        parsed = tf.io.parse_single_example(example, feature_description)
        
        # Convertir texto a bytes
        input_data = tf.strings.unicode_decode(
            parsed['input_bytes'],
            'UTF-8'
        ).to_tensor(shape=[self.config.seq_length])
        
        target_data = tf.strings.unicode_decode(
            parsed['target_bytes'],
            'UTF-8'
        ).to_tensor(shape=[self.config.seq_length])
        
        # Generar máscara de atención
        attention_mask = tf.ones_like(input_data, dtype=tf.int32)
        
        return {
            'inputs': input_data,
            'targets': target_data,
            'attention_mask': attention_mask
        }

    def train_batches(self) -> Iterator[jnp.ndarray]:
        """Genera batches de entrenamiento optimizados"""
        for batch in self.train_dataset:
            yield self._convert_batch(batch)

    def val_batches(self) -> Iterator[jnp.ndarray]:
        """Genera batches de validación optimizados"""
        for batch in self.val_dataset:
            yield self._convert_batch(batch)

    def _convert_batch(self, batch: Dict) -> Dict[str, jnp.ndarray]:
        """Convierte batch a formato JAX optimizado"""
        return {
            'inputs': jnp.array(batch['inputs']),
            'targets': jnp.array(batch['targets']),
            'attention_mask': jnp.array(batch['attention_mask'])
        }

def create_train_state(config: TrainingConfig) -> train_state.TrainState:
    """Inicializa el estado de entrenamiento distribuido"""
    model = TPUCapibaraModel(config)
    key = jax.random.PRNGKey(0)
    
    # Inicialización de parámetros
    params = model.init(
        key,
        jnp.ones((config.batch_size, config.seq_length), DTYPE)
    )
    
    # Sharding automático
    params = jax.device_put(
        params,
        jax.sharding.NamedSharding(TPU_MESH, BATCH_SHARDING)
    )

    # Optimizador con escalado de aprendizaje
    lr_schedule = optax.warmup_cosine_decay_schedule(
        init_value=0.0,
        peak_value=config.learning_rate,
        warmup_steps=config.warmup_steps,
        decay_steps=config.num_train_samples // config.batch_size
    )
    
    optimizer = optax.chain(
        optax.clip_by_global_norm(config.grad_clip),
        optax.adamw(
            learning_rate=lr_schedule,
            weight_decay=config.weight_decay
        ),
        optax.apply_every(4)  # Actualización cada 4 pasos
    )

    return train_state.TrainState.create(
        apply_fn=model.apply,
        params=params,
        tx=optimizer
    )

def train_step(state: train_state.TrainState, batch: Dict[str, Any]) -> Tuple[train_state.TrainState, float]:
    """Paso de entrenamiento distribuido JIT-compilado"""
    def loss_fn(params: Dict[str, Any]) -> float:
        logits = state.apply_fn(
            params,
            batch['inputs'],
            training=True
        )
        loss = optax.softmax_cross_entropy_with_integer_labels(
            logits,
            batch['targets']
        ).mean()
        return cast(float, loss * jax.lax.rsqrt(jax.device_count()))

    grad_fn = jax.value_and_grad(loss_fn)
    loss, grads = grad_fn(state.params)
    grads = jax.lax.pmean(grads, axis_name='batch')
    return state.apply_gradients(grads=grads), loss

def main(config: TrainingConfig) -> None:
    """Flujo Principal de Entrenamiento"""
    # 1. Inicialización
    logger.info("Inicializando entrenamiento...")
    state = create_train_state(config)
    data_loader = TPUDataLoader(config)
    checkpointer = ocp.CheckpointManager(
        'checkpoints',
        ocp.PyTreeCheckpointer(),
        options=ocp.CheckpointManagerOptions(
            max_to_keep=5,
            sharding=BATCH_SHARDING
        )
    )

    # 2. Restaurar checkpoint si existe
    if checkpointer.latest_step() is not None:
        state = checkpointer.restore(checkpointer.latest_step(), state)
        logger.info(f"Checkpoint restaurado: paso {checkpointer.latest_step()}")

    # 3. Bucle de Entrenamiento
    logger.info("Iniciando entrenamiento...")
    for step, batch in enumerate(data_loader.train_batches()):
        state, loss = train_step(state, batch)
        
        # Logging
        if step % 100 == 0:
            logger.info(f"Paso {step}: Loss={loss:.4f}")
            # Agregar métricas a WandB/TensorBoard aquí
        
        # Checkpointing
        if step % SAVE_INTERVAL == 0:
            checkpointer.save(step, items=state)
            logger.info(f"Checkpoint guardado en paso {step}")

        # Validación
        if step % 5000 == 0:
            avg_val_loss = validate(state, data_loader)
            logger.info(f"Validación paso {step}: Loss={avg_val_loss:.4f}")

def validate(state: train_state.TrainState, data_loader: TPUDataLoader) -> float:
    """Ejecuta validación distribuida con JIT y sharding para TPU"""
    @partial(jax.jit, static_argnums=(1,))  
    @partial(shard_map, mesh=TPU_MESH, in_specs=BATCH_SHARDING) 
    def val_step(params: Dict[str, Any], batch: Dict[str, Any]) -> float:
        logits = state.apply_fn(params, batch['inputs'], training=False)
        loss = optax.softmax_cross_entropy_with_integer_labels(
            logits,
            batch['targets']
        ).mean()
        return cast(float, loss * jax.lax.rsqrt(jax.device_count()))
    
    # Acumulación de pérdidas en paralelo
    losses = []
    for val_batch in data_loader.val_batches():
        batch_loss = val_step(state.params, val_batch)
        losses.append(batch_loss)
    
    # Promedio de pérdidas
    return cast(float, jnp.mean(jnp.array(losses)))

if __name__ == "__main__":
    # Configuración
    config = TrainingConfig(
        batch_size=131072,
        seq_length=2048,
        hidden_size=8192,
        num_layers=24,
        num_train_samples=int(1e9)
    )
    
    # Ejecución
    logging.basicConfig(level=logging.INFO)
    main(config)