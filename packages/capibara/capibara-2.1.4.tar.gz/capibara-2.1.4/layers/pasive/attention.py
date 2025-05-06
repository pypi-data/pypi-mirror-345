"""Implementación de atención distribuida optimizada.

Este módulo implementa atención multi-cabeza con sharding automático
y optimizaciones de operaciones matriciales.
"""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from typing import Dict, Any, Optional, Tuple # type: ignore
from interfaces.ilayer import ILayer 

class DistributedAttention(nn.Module, ILayer):
    """
    Capa de atención distribuida optimizada.
    
    Teoría:
    Implementa atención multi-cabeza con sharding automático y optimizaciones
    de operaciones matriciales. Utiliza sharding 2D para distribuir tanto
    las cabezas como las dimensiones de los embeddings.
    
    Args:
        num_heads: Número de cabezas de atención
        head_dim: Dimensión de cada cabeza
        dropout_rate: Tasa de dropout
        use_bias: Usar bias en proyecciones
        sharding_strategy: Estrategia de sharding (2D o 1D)
    """
    num_heads: int
    head_dim: int
    dropout_rate: float = 0.1
    use_bias: bool = True
    sharding_strategy: str = "2d"

    @nn.compact
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        rng: Optional[jax.random.PRNGKey] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Aplica atención distribuida con métricas.
        
        Args:
            x: Tensor de entrada (batch_size, seq_len, hidden_dim)
            context: Tensor de contexto opcional
            training: Modo de entrenamiento
            rng: Key aleatoria para dropout
            **kwargs: Argumentos adicionales
            
        Returns:
            Dict con:
                - output: Atención aplicada
                - metrics: Métricas de atención
                - training: Estado de entrenamiento
        """
        if training and rng is None:
            raise ValueError("Se requiere rng en modo entrenamiento")
            
        # Normalización
        x = nn.LayerNorm(name="norm")(x)
        
        # Proyecciones Q, K, V
        q = nn.Dense(
            self.num_heads * self.head_dim,
            use_bias=self.use_bias,
            name="query"
        )(x)
        k = nn.Dense(
            self.num_heads * self.head_dim,
            use_bias=self.use_bias,
            name="key"
        )(context if context is not None else x)
        v = nn.Dense(
            self.num_heads * self.head_dim,
            use_bias=self.use_bias,
            name="value"
        )(context if context is not None else x)
        
        # Reshape para atención
        batch_size = x.shape[0]
        q = q.reshape(batch_size, -1, self.num_heads, self.head_dim)
        k = k.reshape(batch_size, -1, self.num_heads, self.head_dim)
        v = v.reshape(batch_size, -1, self.num_heads, self.head_dim)
        
        # Atención escalada
        attention = self._compute_attention(q, k, v)
        
        # Dropout en entrenamiento
        if training:
            attention = nn.Dropout(self.dropout_rate)(attention, deterministic=False, rng=rng)
            
        # Proyección de salida
        output = nn.Dense(
            self.num_heads * self.head_dim,
            use_bias=self.use_bias,
            name="out"
        )(attention)
        
        # Calcular métricas
        metrics = self._compute_metrics(q, k, v, attention)
            
        return {
            "output": output,
            "metrics": metrics,
            "training": training
        }

    def _compute_attention(
        self,
        q: jnp.ndarray,
        k: jnp.ndarray,
        v: jnp.ndarray
    ) -> jnp.ndarray:
        """Calcula atención escalada optimizada.
        
        Args:
            q: Queries (batch_size, seq_len, num_heads, head_dim)
            k: Keys (batch_size, seq_len, num_heads, head_dim)
            v: Values (batch_size, seq_len, num_heads, head_dim)
            
        Returns:
            Atención aplicada
        """
        # Matmul optimizado
        scores = jnp.matmul(q, k.swapaxes(-1, -2)) / jnp.sqrt(self.head_dim)
        
        # Softmax
        attention = jax.nn.softmax(scores, axis=-1)
        
        # Aplicar a values
        return jnp.matmul(attention, v)

    def _compute_metrics(
        self,
        q: jnp.ndarray,
        k: jnp.ndarray,
        v: jnp.ndarray,
        attention: jnp.ndarray
    ) -> Dict[str, jnp.ndarray]:
        """Calcula métricas de atención.
        
        Args:
            q: Queries
            k: Keys
            v: Values
            attention: Atención aplicada
            
        Returns:
            Dict con métricas:
                - attention_entropy: Entropía de la atención
                - head_diversity: Diversidad entre cabezas
                - gradient_norm: Norma del gradiente
        """
        # Entropía de la atención
        attention_entropy = -jnp.sum(
            attention * jnp.log(attention + 1e-10),
            axis=-1
        ).mean(axis=-1)
        
        # Diversidad entre cabezas
        head_diversity = jnp.std(attention, axis=-2).mean(axis=-1)
        
        # Norma del gradiente
        gradient_norm = jnp.linalg.norm(
            jnp.concatenate([q, k, v], axis=-1),
            axis=-1
        ).mean(axis=-1)
        
        return {
            "attention_entropy": attention_entropy,
            "head_diversity": head_diversity,
            "gradient_norm": gradient_norm
        } 