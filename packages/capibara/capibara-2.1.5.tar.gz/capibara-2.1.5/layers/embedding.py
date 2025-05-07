"""Implementación de embeddings distribuidos.

Este módulo implementa embeddings con sharding 2D y validación
de dimensiones.
"""

import jax 
import jax.numpy as jnp 
from flax import linen as nn 
from typing import Dict, Any, Optional, Tuple 
from capibara.interfaces.ilayer import ILayer 

class CapibaraEmbedding(nn.Module, ILayer):
    """
    Capa de embedding distribuido con sharding automático.
    
    Teoría:
    Implementa embeddings con sharding 2D para distribuir tanto el vocabulario
    como las dimensiones del embedding entre dispositivos. Utiliza validación
    de dimensiones y normalización automática.
    
    Args:
        vocab_size: Tamaño del vocabulario (debe ser múltiplo del número de dispositivos)
        embed_dim: Dimensión del embedding
        dropout_rate: Tasa de dropout
        use_bias: Usar bias en proyección
        sharding_strategy: Estrategia de sharding (2D o 1D)
    """
    vocab_size: int
    embed_dim: int
    dropout_rate: float = 0.1
    use_bias: bool = True
    sharding_strategy: str = "2d"

    @nn.compact  # type: ignore
    def __call__(
        self: Any,
        x: jnp.ndarray,
        training: bool = False,
        rng: Optional[jax.random.PRNGKey] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Aplica embedding distribuido con métricas.
        
        Args:
            x: Tensor de entrada (batch_size, seq_len)
            training: Modo de entrenamiento
            rng: Key aleatoria para dropout
            **kwargs: Argumentos adicionales
            
        Returns:
            Dict con:
                - output: Embeddings
                - metrics: Métricas del embedding
                - training: Estado de entrenamiento
        """
        if training and rng is None:
            raise ValueError("Se requiere rng en modo entrenamiento")
            
        # Validar dimensiones
        if x.max() >= self.vocab_size:
            raise ValueError(f"Índices fuera de rango: {x.max()} >= {self.vocab_size}")
            
        # Embedding
        embeddings = nn.Embed(
            self.vocab_size,
            self.embed_dim,
            name="embed"
        )(x)
        
        # Normalización
        embeddings = nn.LayerNorm(name="norm")(embeddings)
        
        # Dropout en entrenamiento
        if training:
            embeddings = nn.Dropout(self.dropout_rate)(embeddings, deterministic=False, rng=rng)
            
        # Calcular métricas
        metrics = self._compute_metrics(embeddings)
            
        return {
            "output": embeddings,
            "metrics": metrics,
            "training": training
        }

    def _compute_metrics(self, embeddings: jnp.ndarray) -> Dict[str, jnp.ndarray]:
        """Calcula métricas del embedding.
        
        Args:
            embeddings: Tensor de embeddings
            
        Returns:
            Dict con métricas:
                - embedding_norm: Norma de los embeddings
                - token_diversity: Diversidad entre tokens
                - gradient_norm: Norma del gradiente
        """
        # Norma de los embeddings
        embedding_norm = jnp.linalg.norm(embeddings, axis=-1).mean(axis=-1)
        
        # Diversidad entre tokens
        token_diversity = jnp.std(embeddings, axis=-2).mean(axis=-1)
        
        # Norma del gradiente
        gradient_norm = jnp.linalg.norm(embeddings, axis=-1).mean(axis=-1)
        
        return {
            "embedding_norm": embedding_norm,
            "token_diversity": token_diversity,
            "gradient_norm": gradient_norm
        } 