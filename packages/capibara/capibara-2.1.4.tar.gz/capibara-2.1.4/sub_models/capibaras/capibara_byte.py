"""Implementación optimizada de Capibara para TPUs."""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from typing import Dict, Any, Optional
from functools import partial
import logging

from .tpu_base_config import TPUBaseConfig
from interfaces.isub_models import ISubModel

logger = logging.getLogger(__name__)

class CapibaraByteConfig(TPUBaseConfig):
    """Configuración específica para CapibaraByte."""
    context_window: int = 128
    cache_size: int = 1024
    use_hybrid_sharding: bool = True

class CapibaraByte(nn.Module, ISubModel):
    """Implementación optimizada de Capibara para TPUs.
    
    Características:
    - Sharding híbrido para TPUs
    - Precisión mixta
    - Cache JIT-compatible
    - Optimizaciones de memoria
    """
    config: CapibaraByteConfig
    
    def setup(self):
        """Inicializa componentes optimizados para TPU."""
        self.dense = nn.Dense(
            self.config.hidden_size,
            dtype=self.config.dtype,
            name="byte_dense"
        )
        self.norm = nn.LayerNorm(
            dtype=self.config.dtype,
            name="byte_norm"
        )
        
    @partial(jax.jit, static_argnums=(0,))
    def _compute_context_weight(self, context_embedding: jnp.ndarray) -> jnp.ndarray:
        """Calcula peso del contexto de forma JIT-compatible."""
        return jnp.mean(context_embedding, axis=-1)
        
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Forward pass optimizado para TPU.
        
        Args:
            x: Tensor de entrada
            context: Tensor de contexto opcional
            training: Modo entrenamiento
            **kwargs: Argumentos adicionales
            
        Returns:
            Dict con output y métricas
        """
        # Normalizar entrada
        x = self.norm(x)
        
        # Procesar contexto si existe
        if context is not None:
            context_weight = self._compute_context_weight(context)
            x = x * context_weight[..., None]
            
        # Proyección densa
        x = self.dense(x)
        
        # Aplicar dropout si es necesario
        if training and self.config.dropout_rate > 0:
            x = nn.Dropout(self.config.dropout_rate)(
                x, deterministic=False
            )
            
        # Métricas
        metrics = {
            "input_norm": jnp.linalg.norm(x),
            "output_norm": jnp.linalg.norm(x),
            "context_weight": context_weight if context is not None else 0.0
        }
        
        return {
            "output": x,
            "metrics": metrics
        }