"""Implementación mejorada de NeuroAdaptiveLayer.

Esta capa implementa una arquitectura clara con atención y FFN,
con tracking detallado de memoria y tiempo.
"""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from typing import Dict, Any, Optional, Tuple
import logging
from layers.base import BaseLayer, LayerConfig

logger = logging.getLogger(__name__)

class NeuroAdaptiveLayerConfig(LayerConfig):
    """Configuración específica para NeuroAdaptiveLayer.
    
    Args:
        num_heads: Número de cabezas de atención
        ff_dim: Dimensión de la capa feed-forward
        dropout_rate: Tasa de dropout
    """
    num_heads: int = 8
    ff_dim: int = 2048
    dropout_rate: float = 0.1

class NeuroAdaptiveLayer(BaseLayer):
    """Capa adaptativa con atención y FFN.
    
    Implementa:
    - Atención multi-cabeza
    - Capa feed-forward
    - Tracking de memoria/tiempo
    
    Ejemplo de uso:
    ```python
    config = NeuroAdaptiveLayerConfig(
        hidden_size=512,
        num_heads=8,
        ff_dim=2048
    )
    layer = NeuroAdaptiveLayer(config)
    output = layer(x, training=True, rng=key)
    ```
    """
    
    config: NeuroAdaptiveLayerConfig
    
    def setup(self):
        """Inicializa NeuroAdaptiveLayer."""
        super().setup()
        
        # Atención
        self.attention = nn.MultiHeadDotProductAttention(
            num_heads=self.config.num_heads,
            qkv_features=self.config.hidden_size,
            out_features=self.config.hidden_size
        )
        
        # Feed-forward
        self.ff = nn.Sequential([
            nn.Dense(self.config.ff_dim),
            nn.relu,
            nn.Dense(self.config.hidden_size)
        ])
        
        # Normalización
        self.norm1 = nn.LayerNorm()
        self.norm2 = nn.LayerNorm()
        
        # Dropout
        self.dropout = nn.Dropout(self.config.dropout_rate)
        
    def __call__(
        self,
        x: jnp.ndarray,
        training: bool = False,
        rng: Optional[jax.random.PRNGKey] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Aplica NeuroAdaptiveLayer.
        
        Args:
            x: Tensor de entrada (batch_size, seq_len, hidden_dim)
            training: Modo entrenamiento
            rng: Key aleatoria
            **kwargs: Argumentos adicionales
            
        Returns:
            Dict con output y métricas
        """
        if training and rng is None:
            raise ValueError("Se requiere rng en modo entrenamiento")
            
        # Atención
        attn_output = self.attention(x, x)
        attn_output = self.dropout(attn_output, deterministic=not training)
        x = self.norm1(x + attn_output)
        
        # Feed-forward
        ff_output = self.ff(x)
        ff_output = self.dropout(ff_output, deterministic=not training)
        output = self.norm2(x + ff_output)
        
        # Métricas específicas
        metrics = {
            "attention_norm": jnp.linalg.norm(attn_output),
            "ff_norm": jnp.linalg.norm(ff_output),
            "memory_usage": jax.device_memory_allocated()
        }
        
        # Combinar con métricas base
        base_output = self._base_call(output, training=training, rng=rng)
        base_output["metrics"].update(metrics)
        
        return base_output 