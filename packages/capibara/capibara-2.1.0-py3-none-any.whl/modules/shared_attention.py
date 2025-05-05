"""Módulo de atención compartido para todos los módulos."""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from typing import Optional, Dict, Any # type: ignore

class SharedAttention(nn.Module):
    """Atención multi-cabeza compartida con normalización y dropout.
    
    Args:
        hidden_size: Dimensión del espacio oculto
        num_heads: Número de cabezas de atención
        dropout_rate: Tasa de dropout
    """
    hidden_size: int
    num_heads: int
    dropout_rate: float = 0.1
    
    def setup(self):
        """Inicializa componentes de atención."""
        self.attention = nn.MultiHeadDotProductAttention(
            num_heads=self.num_heads,
            qkv_features=self.hidden_size,
            dropout_rate=self.dropout_rate
        )
        self.norm = nn.LayerNorm()
        self.dropout = nn.Dropout(self.dropout_rate)
        
    def __call__(
        self,
        query: jnp.ndarray,
        key: Optional[jnp.ndarray] = None,
        value: Optional[jnp.ndarray] = None,
        mask: Optional[jnp.ndarray] = None,
        training: bool = False
    ) -> Dict[str, Any]:
        """Aplica atención multi-cabeza.
        
        Args:
            query: Tensor de consulta (batch, seq_len, hidden_size)
            key: Tensor de clave (batch, seq_len, hidden_size)
            value: Tensor de valor (batch, seq_len, hidden_size)
            mask: Máscara de atención
            training: Modo entrenamiento
            
        Returns:
            Dict con output y métricas
        """
        # Si no se proporciona key/value, usar query
        key = key if key is not None else query
        value = value if value is not None else query
        
        # Normalizar inputs
        query = self.norm(query)
        key = self.norm(key)
        value = self.norm(value)
        
        # Aplicar atención
        attended = self.attention(
            query,
            key,
            value,
            mask=mask,
            deterministic=not training
        )
        
        # Dropout
        attended = self.dropout(attended, deterministic=not training)
        
        # Métricas
        metrics = {
            "attention_norm": jnp.linalg.norm(attended),
            "query_norm": jnp.linalg.norm(query),
            "key_norm": jnp.linalg.norm(key),
            "value_norm": jnp.linalg.norm(value)
        }
        
        return {
            "output": attended,
            "metrics": metrics
        } 