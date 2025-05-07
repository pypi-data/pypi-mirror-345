"""Entrenamiento unificado de CapibaraGPT con soporte TPU y optimizaciones avanzadas."""

import jax 
import jax.numpy as jnp 
import optax 
from flax.training import train_state 
import wandb #type: ignore
import logging
import time
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, Callable, Union, cast, Iterator, TypeVar
from dataclasses import dataclass
from functools import partial

from capibara.core.config import CapibaraConfig, load_config
from capibara.core.model import DynamicCapibaraModel
from capibara.data.dataset import CapibaraDataset
from capibara.config.distribution_config import (
    distributed_jit,
    model_sharded_jit,
    batch_sharded_jit,
    create_unified_mesh,
    BATCH_SHARDING,
    MODEL_SHARDING,
    HYBRID_SHARDING,
    TPU_DTYPE
)
from capibara.utils.monitoring import RealTimeMonitor
from capibara.core.optimizer import create_optimizer_from_capibara_config
from capibara.utils.checkpointing import CheckpointManager

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class TrainingState:
    """Estado de entrenamiento unificado."""
    model: DynamicCapibaraModel
    optimizer: optax.GradientTransformation
    params: Dict[str, Any]
    opt_state: optax.OptState
    step: int = 0
    best_val_loss: float = float('inf')
    no_improvement_count: int = 0

def train_step_jit(
    state: TrainingState,
    batch: Dict[str, jnp.ndarray],
    loss_fn: Callable[[jnp.ndarray, jnp.ndarray], float]
) -> Tuple[TrainingState, Dict[str, float]]:
    """Paso de entrenamiento distribuido optimizado."""
    def loss_fn_step(params: Dict[str, Any]) -> Tuple[float, jnp.ndarray]:
        outputs = state.model.apply(
            {'params': params},
            batch['inputs'],
            training=True
        )
        loss = loss_fn(outputs, batch['targets'])
        return loss, outputs

    grad_fn = jax.value_and_grad(loss_fn_step, has_aux=True)
    (loss, outputs), grads = grad_fn(state.params)
    
    # Promedio de gradientes a través de dispositivos
    grads = jax.lax.pmean(grads, axis_name='batch')
    
    # Actualizar parámetros
    updates, new_opt_state = state.optimizer.update(grads, state.opt_state, state.params)
    new_params = optax.apply_updates(state.params, updates)
    
    # Métricas
    metrics: Dict[str, float] = {
        'loss': float(loss),
        'perplexity': float(jnp.exp(loss))
    }
    
    new_state = TrainingState(
        model=state.model,
        optimizer=state.optimizer,
        params=new_params,
        opt_state=new_opt_state,
        step=state.step + 1,
        best_val_loss=state.best_val_loss,
        no_improvement_count=state.no_improvement_count
    )
    
    return new_state, metrics

train_step = distributed_jit(train_step_jit)

def validate_step_jit(
    state: TrainingState,
    batch: Dict[str, jnp.ndarray],
    loss_fn: Callable[[jnp.ndarray, jnp.ndarray], float]
) -> float:
    """Paso de validación distribuido."""
    outputs = state.model.apply(
        {'params': state.params},
        batch['inputs'],
        training=False
    )
    loss = loss_fn(outputs, batch['targets'])
    return cast(float, jax.lax.pmean(loss, axis_name='batch'))

validate_step = model_sharded_jit(validate_step_jit)

def train_model(
    config: CapibaraConfig,
    output_dir: Path,
    use_tpu: bool = False
) -> None:
    """Entrenamiento unificado con soporte TPU y optimizaciones."""
    logger.info("Iniciando entrenamiento unificado")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Inicializar WandB si está habilitado
    run = None
    if config.wandb.enabled:
        run = wandb.init(
            project=config.wandb.project,
            entity=config.wandb.entity,
            config=config.to_dict()
        )

    try:
        # Inicializar modelo y optimizador
        model = DynamicCapibaraModel(
            hidden_size=config.model.hidden_size,
            num_heads=config.model.num_heads,
            num_layers=config.model.num_layers,
            dropout_rate=config.model.dropout_rate,
            use_tpu=use_tpu,
            monitor_metrics=config.model.monitor_metrics,
            vocab_size=config.model.vocab_size,
            max_length=config.model.max_length
        )
        
        optimizer = create_optimizer_from_capibara_config(config)
        
        # Inicializar estado
        key = jax.random.PRNGKey(config.training.seed)
        dummy_batch = jnp.ones((1, config.model.max_length), dtype=jnp.int32)
        variables = model.init(key, dummy_batch, training=True)
        params = variables['params']
        opt_state = optimizer.init(params)
        
        state = TrainingState(
            model=model,
            optimizer=optimizer,
            params=params,
            opt_state=opt_state
        )

        # Inicializar monitor y checkpoint manager
        monitor = RealTimeMonitor()
        monitor.start()
        checkpoint_manager = CheckpointManager(str(output_dir))

        # Restaurar checkpoint si existe
        try:
            state, metadata = checkpoint_manager.restore(state)
            logger.info(f"Restaurado del paso {state.step}")
        except:
            logger.info("Iniciando entrenamiento desde cero")

        # Obtener datasets
        train_dataset = CapibaraDataset(config, split='train')
        val_dataset = CapibaraDataset(config, split='val')

        # Función de pérdida
        def loss_fn(outputs: jnp.ndarray, targets: jnp.ndarray) -> float:
            return cast(float, jnp.mean(optax.softmax_cross_entropy_with_integer_labels(
                outputs, targets
            )))

        # Bucle de entrenamiento
        for epoch in range(config.training.num_epochs):
            epoch_start = time.time()
            epoch_loss = 0.0
            num_batches = 0

            # Entrenamiento
            for batch in train_dataset:
                state, metrics = train_step(state, batch, loss_fn)  # type: ignore
                metrics_dict: Dict[str, float] = metrics  # type: ignore
                epoch_loss += metrics_dict['loss']
                num_batches += 1

                # Logging
                if state.step % config.training.log_every == 0:
                    logger.info(f"Step {state.step}: Loss={metrics_dict['loss']:.4f}")
                    if run is not None:
                        wandb.log(metrics_dict, step=state.step)

            # Validación
            if epoch % config.training.eval_every == 0:
                val_loss = 0.0
                num_val_batches = 0
                for val_batch in val_dataset:
                    batch_loss: float = validate_step(state, val_batch, loss_fn)  # type: ignore
                    val_loss += batch_loss
                    num_val_batches += 1
                val_loss /= num_val_batches

                # Early stopping check
                if val_loss < state.best_val_loss:
                    state.best_val_loss = val_loss
                    state.no_improvement_count = 0
                    checkpoint_manager.save(state, state.step, {'val_loss': val_loss})
                else:
                    state.no_improvement_count += 1

                logger.info(f"Epoch {epoch} - Val Loss: {val_loss:.4f}")
                if run is not None:
                    wandb.log({'val_loss': val_loss}, step=state.step)

                if state.no_improvement_count >= config.training.early_stopping_patience:
                    logger.info("Early stopping triggered")
                    break

            # Checkpoint regular
            if epoch % config.training.checkpoint_every == 0:
                checkpoint_manager.save(state, state.step)

            # Métricas de época
            epoch_time = time.time() - epoch_start
            logger.info(f"Epoch {epoch} - Time: {epoch_time:.2f}s")

    except Exception as e:
        logger.error(f"Error en entrenamiento: {e}", exc_info=True)
        raise
    finally:
        if run is not None:
            wandb.finish()
        monitor.stop()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Entrenamiento unificado de CapibaraModel")
    parser.add_argument("--config", type=str, required=True, help="Ruta al archivo de configuración")
    parser.add_argument("--output_dir", type=str, required=True, help="Directorio de salida")
    parser.add_argument("--use_tpu", action="store_true", help="Usar TPU para entrenamiento")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    config = load_config(args.config)
    train_model(config, Path(args.output_dir), args.use_tpu)