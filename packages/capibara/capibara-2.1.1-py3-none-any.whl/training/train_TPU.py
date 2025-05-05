"""Entrenamiento TPU con Distribución Unificada."""

import jax #type: ignore
import jax.numpy as jnp #type: ignore
import optax #type: ignore
from flax.training import train_state #type: ignore
import logging
from typing import Dict, Any, Callable, Tuple, Optional
from functools import partial

from capibara_model.core.distribution_config import (
    distributed_jit,
    model_sharded_jit,
    batch_sharded_jit,
    create_unified_mesh,
    BATCH_SHARDING,
    MODEL_SHARDING,
    HYBRID_SHARDING,
    TPU_DTYPE
)
from capibara_model.core.model import CapibaraModel
from capibara_model.data.dataset import CapibaraDataset
from capibara_model.utils.checkpoint_manager import CapibaraCheckpointManager

logger = logging.getLogger(__name__)

def normalize_batch(batch: Dict[str, jnp.ndarray]) -> Dict[str, jnp.ndarray]:
    """Normaliza el batch para TPU.
    
    Args:
        batch: Batch de datos
        
    Returns:
        Batch normalizado y convertido a tipos TPU
    """
    def normalize_tensor(x: jnp.ndarray) -> jnp.ndarray:
        if x.dtype == jnp.uint8:
            # Convertir uint8 a float32 normalizado [0,1]
            x = x.astype(jnp.float32) / 255.0
        if x.dtype == jnp.float32:
            # Convertir a bfloat16 para TPU
            x = x.astype(TPU_DTYPE)
        return x
        
    return jax.tree_map(normalize_tensor, batch)

@distributed_jit
def train_step_tpu(
    state: train_state.TrainState,
    batch: Dict[str, jnp.ndarray],
    loss_fn: Callable
) -> Tuple[train_state.TrainState, float]:
    """Paso de entrenamiento TPU distribuido unificado."""
    def loss_fn_step(params):
        # Normalizar y convertir tipos para TPU
        batch_tpu = normalize_batch(batch)
        
        outputs = state.apply_fn(
            {'params': params},
            batch_tpu['inputs'],
            training=True
        )
        loss = loss_fn(outputs, batch_tpu['targets'])
        return loss, outputs

    grad_fn = jax.value_and_grad(loss_fn_step, has_aux=True)
    (loss, _), grads = grad_fn(state.params)
    
    # Promedio de gradientes a través de dispositivos TPU
    grads = jax.lax.pmean(grads, axis_name='batch')
    
    # Aplicar actualizaciones
    new_state = state.apply_gradients(grads=grads)
    return new_state, loss

@model_sharded_jit
def validate_step_tpu(
    state: train_state.TrainState,
    batch: Dict[str, jnp.ndarray],
    loss_fn: Callable
) -> float:
    """Paso de validación TPU distribuido unificado."""
    # Normalizar y convertir tipos para TPU
    batch_tpu = normalize_batch(batch)
    
    # Aplicar modelo con sharding
    outputs = state.apply_fn(
        {'params': state.params},
        batch_tpu['inputs'],
        training=False
    )
    
    # Calcular pérdida con reducción distribuida
    loss = loss_fn(outputs, batch_tpu['targets'])
    return jax.lax.pmean(loss, axis_name='batch')

def validate_model_tpu(
    state: train_state.TrainState,
    val_dataset: CapibaraDataset,
    loss_fn: Callable,
    num_batches: Optional[int] = None
) -> float:
    """Validación distribuida optimizada para TPU.
    
    Args:
        state: Estado del modelo
        val_dataset: Dataset de validación
        loss_fn: Función de pérdida
        num_batches: Número de batches a procesar (opcional)
        
    Returns:
        Pérdida promedio de validación
    """
    # Acumulación de pérdidas en paralelo
    val_losses = []
    batch_count = 0
    
    for val_batch in val_dataset:
        if num_batches is not None and batch_count >= num_batches:
            break
            
        # Aplicar paso de validación distribuido
        batch_loss = validate_step_tpu(state, val_batch, loss_fn)
        val_losses.append(batch_loss)
        batch_count += 1
    
    # Promedio de pérdidas con reducción distribuida
    return jax.lax.pmean(jnp.mean(jnp.array(val_losses)), axis_name='batch')

def train_model_tpu(
    model: CapibaraModel,
    train_dataset: CapibaraDataset,
    val_dataset: CapibaraDataset,
    config: Dict[str, Any],
    num_epochs: int
) -> train_state.TrainState:
    """Entrenamiento TPU principal con distribución unificada."""
    # Inicializar estado
    key = jax.random.PRNGKey(0)
    
    # Crear dummy batch con tipos correctos
    dummy_batch = {
        'inputs': jnp.ones((1, config['seq_len']), dtype=jnp.uint8),
        'targets': jnp.ones((1, config['seq_len']), dtype=jnp.uint8)
    }
    
    # Crear estado con sharding TPU
    state = train_state.TrainState.create(
        apply_fn=model.apply,
        params=model.init(key, dummy_batch, training=False)['params'],
        tx=optax.adam(config['learning_rate'])
    )
    
    # Sharding de parámetros para TPU
    mesh = create_unified_mesh()
    state = jax.device_put_sharded(
        mesh.local_devices,
        [state] * len(mesh.local_devices)
    )
    
    # Función de pérdida optimizada para TPU
    def loss_fn(logits: jnp.ndarray, targets: jnp.ndarray) -> float:
        # Asegurar que targets estén en int32 para cross-entropy
        targets = targets.astype(jnp.int32)
        return optax.softmax_cross_entropy_with_integer_labels(
            logits, targets
        ).mean()
    
    # Inicializar gestor de checkpoints para TPU
    checkpoint_manager = CapibaraCheckpointManager(
        checkpoint_dir=config.get('checkpoint_dir', 'checkpoints'),
        max_to_keep=config.get('max_checkpoints', 5),
        save_interval=config.get('checkpoint_interval', 1000),
        use_async=True,
        sharding=BATCH_SHARDING
    )
    
    # Restaurar checkpoint si existe
    latest_step = checkpoint_manager.get_latest_step()
    if latest_step is not None:
        state = checkpoint_manager.restore(step=latest_step, state=state)
        logger.info(f"Checkpoint restaurado del paso {latest_step}")
    
    # Bucle de entrenamiento TPU
    for epoch in range(num_epochs):
        # Entrenamiento
        for step, batch in enumerate(train_dataset):
            state, loss = train_step_tpu(state, batch, loss_fn)
            
            # Logging
            if step % 100 == 0:
                logger.info(f"Epoch {epoch}, Step {step}, Loss: {loss}")
                
            # Checkpointing
            if step % config.get('checkpoint_interval', 1000) == 0:
                metrics = {'loss': float(loss)}
                checkpoint_manager.save(
                    step=step,
                    state=state,
                    metrics=metrics
                )
        
        # Validación distribuida
        val_loss = validate_model_tpu(
            state=state,
            val_dataset=val_dataset,
            loss_fn=loss_fn,
            num_batches=config.get('validation_steps', None)
        )
        
        logger.info(f"Epoch {epoch}, Validation Loss: {val_loss}")
        
        # Guardar checkpoint final del epoch
        metrics = {
            'loss': float(loss),
            'val_loss': float(val_loss)
        }
        checkpoint_manager.save(
            step=epoch,
            state=state,
            metrics=metrics,
            force=True
        )
    
    # Cerrar gestor de checkpoints
    checkpoint_manager.close()
    return state