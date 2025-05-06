"""CapibaraByte Ultra-Optimizado para TPU con Distribución Unificada."""

import jax #type: ignore
import jax.numpy as jnp #type: ignore
from flax import linen as nn #type: ignore
from dataclasses import dataclass
from typing import Tuple, Callable, Optional, Dict, Any
from functools import partial
import logging

from core.distribution_config import (
    distributed_jit,
    model_sharded_jit,
    batch_sharded_jit,
    BATCH_SHARDING,
    MODEL_SHARDING,
    HYBRID_SHARDING,
    TPU_DTYPE
)
from core._model import create_unified_mesh

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ByteConfigTPU:
    """Configuración para TPUCapibaraByte.
    
    Attributes:
        input_dim: Dimensión de entrada
        hidden_size: Tamaño del estado oculto
        update_rate: Tasa de actualización del estado
        activation: Función de activación
        shard_axis: Ejes para sharding
        dtype: Tipo de datos para TPU
    """
    input_dim: int = 256
    hidden_size: int = 2048
    update_rate: float = 0.1
    activation: Callable = jax.nn.gelu
    shard_axis: Tuple[str, str] = ('batch', 'hidden')
    dtype: jnp.dtype = TPU_DTYPE

class TPUCapibaraByte(nn.Module):
    """Versión distribuida para TPU con sharding unificado."""
    
    config: ByteConfigTPU

    def setup(self):
        """Inicialización con distribución unificada."""
        try:
            # Configuración de malla
            self.mesh = create_unified_mesh()
            
            # Sharding de parámetros
            self.W_state = self.param('W_state',
                                    nn.initializers.he_normal(),
                                    (self.config.hidden_size, self.config.hidden_size),
                                    sharding=HYBRID_SHARDING)
            
            self.W_conv = self.param('W_conv',
                                   nn.initializers.he_normal(),
                                   (self.config.input_dim, self.config.hidden_size),
                                   sharding=HYBRID_SHARDING)

            # Capa de normalización distribuida
            self.norm = nn.LayerNorm(sharding=HYBRID_SHARDING)
            
            # Cache para parámetros convertidos
            self._cached_params = None
            
        except Exception as e:
            logger.error(f"Error en setup: {e}")
            raise

    def _validate_input(self, x: jnp.ndarray) -> None:
        """Valida las dimensiones y tipo de la entrada."""
        if x.ndim != 3:
            raise ValueError(f"Input debe ser 3D (batch, seq_len, dim), got {x.shape}")
        if x.shape[-1] != self.config.input_dim:
            raise ValueError(f"Última dimensión debe ser {self.config.input_dim}, got {x.shape[-1]}")

    def _convert_params(self) -> Dict[str, jnp.ndarray]:
        """Convierte parámetros al tipo de TPU con caching."""
        if self._cached_params is None:
            self._cached_params = {
                'W_state': self.W_state.astype(self.config.dtype),
                'W_conv': self.W_conv.astype(self.config.dtype)
            }
        return self._cached_params

    @distributed_jit
    def __call__(self, x: jnp.ndarray, initial_state: Optional[jnp.ndarray] = None, 
                training: bool = False) -> Tuple[jnp.ndarray, jnp.ndarray]:
        """Forward pass distribuido con optimización de layout.
        
        Args:
            x: Input tensor de forma (batch, seq_len, input_dim)
            initial_state: Estado inicial opcional
            training: Modo de entrenamiento
            
        Returns:
            Tuple de (estado_final, todos_estados)
        """
        try:
            self._validate_input(x)
            x = jnp.asarray(x, self.config.dtype)
            
            # Obtener parámetros convertidos
            params = self._convert_params()
            
            # Procesamiento vectorizado optimizado
            def scan_fn(carry, x_t):
                x_t = self.norm(x_t)
                new_state = (1 - self.config.update_rate) * carry + \
                          self.config.update_rate * self.config.activation(
                              jnp.dot(carry, params['W_state']) + 
                              jnp.dot(x_t, params['W_conv'])
                          )
                return new_state, new_state

            initial_state = initial_state if initial_state is not None else jnp.zeros(
                (x.shape[0], self.config.hidden_size), dtype=self.config.dtype)
            
            final_state, all_states = jax.lax.scan(
                scan_fn,
                initial_state,
                jnp.moveaxis(x, 1, 0)  # Layout óptimo para XLA
            )
            
            return final_state, jnp.moveaxis(all_states, 0, 1)
            
        except Exception as e:
            logger.error(f"Error en forward pass: {e}")
            raise

# Bloque de Entrenamiento Distribuido
@distributed_jit
def train_step(state, batch, context):
    """Paso de entrenamiento optimizado para TPU.
    
    Args:
        state: Estado actual del modelo
        batch: Lote de datos
        context: Contexto opcional
        
    Returns:
        Tuple de (nuevo_estado, pérdida)
    """
    try:
        def loss_fn(params):
            _, states = TPUCapibaraByte().apply(
                {'params': params},
                batch['inputs'],
                context,
                training=True
            )
            return jnp.mean(states ** 2)  # Pérdida de ejemplo
            
        grad_fn = jax.value_and_grad(loss_fn)
        loss, grads = grad_fn(state.params)
        return state.apply_gradients(grads=grads), loss
        
    except Exception as e:
        logger.error(f"Error en train_step: {e}")
        raise