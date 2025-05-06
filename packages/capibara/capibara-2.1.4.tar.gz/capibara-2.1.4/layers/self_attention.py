"""Implementación mejorada de SelfAttention.

Esta capa implementa atención estándar con soporte para máscaras
y conexión residual.
"""

import jax #type: ignore
import jax.numpy as jnp #type: ignore
from flax import linen as nn #type: ignore
import logging
from typing import Optional, Dict, Any

from interfaces.ilayer import ILayer
from layers.base import BaseLayer, LayerConfig

logger = logging.getLogger(__name__)

class SelfAttentionConfig(LayerConfig):
    """Configuración específica para SelfAttention.
    
    Args:
        num_heads: Número de cabezas de atención
        dropout_rate: Tasa de dropout
        use_mask: Si True, usa máscara de atención
    """
    num_heads: int = 8
    dropout_rate: float = 0.1
    use_mask: bool = True

class SelfAttention(BaseLayer, ILayer):
    """Capa de auto-atención estándar.
    
    Implementa:
    - Atención multi-cabeza
    - Soporte para máscaras
    - Conexión residual
    
    Ejemplo de uso:
    ```python
    config = SelfAttentionConfig(
        hidden_size=512,
        num_heads=8,
        use_mask=True
    )
    layer = SelfAttention(config)
    output = layer(x, training=True, rng=key)
    ```
    """
    
    config: SelfAttentionConfig
    
    def setup(self):
        """Inicializa SelfAttention."""
        super().setup()
        
        # Atención
        self.attention = nn.MultiHeadDotProductAttention(
            num_heads=self.config.num_heads,
            qkv_features=self.config.hidden_size,
            out_features=self.config.hidden_size
        )
        
        # Normalización
        self.norm = nn.LayerNorm()
        
        # Dropout
        self.dropout = nn.Dropout(self.config.dropout_rate)
    
    def __call__(
        self,
        x: jnp.ndarray,
        training: bool = False,
        rng: Optional[jax.random.PRNGKey] = None,
        attention_mask: Optional[jnp.ndarray] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Aplica SelfAttention.
        
        Args:
            x: Tensor de entrada (batch_size, seq_len, hidden_dim)
            training: Modo entrenamiento
            rng: Key aleatoria
            attention_mask: Máscara de atención opcional
            **kwargs: Argumentos adicionales
            
        Returns:
            Dict con output y métricas
        """
        if training and rng is None:
            raise ValueError("Se requiere rng en modo entrenamiento")
            
        # Aplicar máscara si está disponible
        if attention_mask is not None and self.config.use_mask:
            x = x + jnp.where(attention_mask == 0, -1e9, 0.0)
            
        # Atención
        attn_output = self.attention(x, x)
        attn_output = self.dropout(attn_output, deterministic=not training)
        
        # Conexión residual + normalización
        output = self.norm(x + attn_output)
        
        # Métricas específicas
        metrics = {
            "attention_norm": jnp.linalg.norm(attn_output),
            "residual_norm": jnp.linalg.norm(x),
            "mask_used": attention_mask is not None
        }
        
        # Combinar con métricas base
        base_output = self._base_call(output, training=training, rng=rng)
        base_output["metrics"].update(metrics)
        
        return base_output