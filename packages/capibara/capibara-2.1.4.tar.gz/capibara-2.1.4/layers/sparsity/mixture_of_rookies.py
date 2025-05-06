"""Implementación de MixtureOfRookies con mezcla adaptativa.

Este módulo implementa una mezcla adaptativa entre caminos denso y esparso,
con thresholding dinámico y cuantización opcional.
"""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from typing import Dict, Any, Optional, Tuple, Union # type: ignore
from interfaces.ilayer import ILayer 

class MixtureOfRookies(nn.Module, ILayer):
    """
    Capa que implementa mezcla adaptativa entre caminos denso y esparso.
    
    Teoría:
    Implementa una mezcla adaptativa entre un camino denso y uno esparso,
    donde el parámetro alpha se ajusta dinámicamente según la esparsidad
    de la entrada. Incluye thresholding adaptativo y cuantización opcional.
    
    Args:
        hidden_size: Dimensión del espacio oculto
        dropout_rate: Tasa de dropout
        sparsity_threshold: Umbral inicial para esparsidad
        use_quantization: Habilitar cuantización
        quant_bits: Bits para cuantización
        alpha_init: Valor inicial de mezcla
    """
    hidden_size: int
    dropout_rate: float = 0.1
    sparsity_threshold: float = 0.1
    use_quantization: bool = False
    quant_bits: int = 8
    alpha_init: float = 0.5

    @nn.compact
    def __call__(
        self,
        x: jnp.ndarray,
        training: bool = False,
        rng: Optional[jax.random.PRNGKey] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Aplica mezcla adaptativa con métricas.
        
        Args:
            x: Tensor de entrada (batch_size, seq_len, hidden_dim)
            training: Modo de entrenamiento
            rng: Key aleatoria para dropout
            **kwargs: Argumentos adicionales
            
        Returns:
            Dict con:
                - output: Mezcla adaptativa
                - metrics: Métricas de mezcla
                - training: Estado de entrenamiento
        """
        if training and rng is None:
            raise ValueError("Se requiere rng en modo entrenamiento")
            
        # Normalización
        x = nn.LayerNorm(name="norm")(x)
        
        # Camino denso
        dense = nn.Dense(self.hidden_size, name="dense")(x)
        
        # Camino esparso
        sparse = self._sparse_path(x)
        
        # Mezcla adaptativa
        alpha = self._compute_alpha(x, dense, sparse)
        output = alpha * dense + (1 - alpha) * sparse
        
        # Cuantización opcional
        if self.use_quantization:
            output = self._quantize(output)
        
        # Dropout en entrenamiento
        if training:
            output = nn.Dropout(self.dropout_rate)(output, deterministic=False, rng=rng)
            
        # Calcular métricas
        metrics = self._compute_metrics(x, dense, sparse, alpha)
            
        return {
            "output": output,
            "metrics": metrics,
            "training": training
        }

    def _sparse_path(self, x: jnp.ndarray) -> jnp.ndarray:
        """Camino esparso con thresholding adaptativo.
        
        Args:
            x: Tensor de entrada
            
        Returns:
            Tensor esparso
        """
        # Proyección esparsa
        sparse = nn.Dense(self.hidden_size, name="sparse")(x)
        
        # Thresholding adaptativo
        threshold = self.sparsity_threshold * jnp.std(sparse)
        mask = jnp.abs(sparse) > threshold
        return sparse * mask

    def _compute_alpha(
        self,
        x: jnp.ndarray,
        dense: jnp.ndarray,
        sparse: jnp.ndarray
    ) -> jnp.ndarray:
        """Calcula mezcla adaptativa.
        
        Args:
            x: Tensor de entrada
            dense: Camino denso
            sparse: Camino esparso
            
        Returns:
            Parámetro de mezcla
        """
        # Calcular esparsidad
        sparsity = jnp.mean(jnp.abs(sparse) > 0, axis=-1, keepdims=True)
        
        # Alpha adaptativo
        alpha = nn.Dense(1, name="alpha")(x)
        alpha = jax.nn.sigmoid(alpha)
        
        # Ajustar por esparsidad
        return alpha * (1 - sparsity) + self.alpha_init * sparsity

    def _quantize(self, x: jnp.ndarray) -> jnp.ndarray:
        """Aplica cuantización opcional.
        
        Args:
            x: Tensor a cuantizar
            
        Returns:
            Tensor cuantizado
        """
        scale = (2 ** (self.quant_bits - 1)) - 1
        return jnp.round(x * scale) / scale

    def _compute_metrics(
        self,
        x: jnp.ndarray,
        dense: jnp.ndarray,
        sparse: jnp.ndarray,
        alpha: jnp.ndarray
    ) -> Dict[str, jnp.ndarray]:
        """Calcula métricas de mezcla.
        
        Args:
            x: Tensor de entrada
            dense: Camino denso
            sparse: Camino esparso
            alpha: Parámetro de mezcla
            
        Returns:
            Dict con métricas:
                - sparsity: Nivel de esparsidad
                - alpha_mean: Media de mezcla
                - path_diversity: Diversidad entre caminos
        """
        # Esparsidad
        sparsity = jnp.mean(jnp.abs(sparse) > 0, axis=-1)
        
        # Media de mezcla
        alpha_mean = jnp.mean(alpha, axis=-1)
        
        # Diversidad entre caminos
        path_diversity = jnp.std(
            jnp.concatenate([dense, sparse], axis=-1),
            axis=-1
        )
        
        return {
            "sparsity": sparsity,
            "alpha_mean": alpha_mean,
            "path_diversity": path_diversity
        } 