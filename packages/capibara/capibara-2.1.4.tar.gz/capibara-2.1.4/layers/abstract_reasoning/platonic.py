"""Implementación de la capa Platonic para procesamiento conceptual.

Esta capa implementa operaciones axiomáticas sobre conceptos platónicos usando
t-norms y t-conorms para operaciones lógicas difusas, siguiendo los axiomas:
- Conmutatividad
- Asociatividad
- Monotonicidad
- Elemento neutro
"""

import enum
from typing import Dict, Any, Optional, Callable

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from interfaces.ilayer import ILayer # type: ignore


class TNormType(enum.Enum):
    """Tipos de t-norms soportados."""
    PRODUCT = "product"  # T-norm producto
    MINIMUM = "minimum"  # T-norm mínimo
    LUKASIEWICZ = "lukasiewicz"  # T-norm Lukasiewicz
    DRASTIC = "drastic"  # T-norm drástica
    HAMACHER = "hamacher"  # T-norm Hamacher


class Platonic(nn.Module, ILayer):
    """Capa de procesamiento de conceptos platónicos con operaciones axiomáticas.
    
    Implementa operaciones lógicas difusas usando t-norms y t-conorms que preservan
    los axiomas matemáticos de los conceptos platónicos. Soporta múltiples tipos
    de t-norms y proporciona métricas de calidad conceptual.
    
    Args:
        hidden_size: Dimensión del espacio conceptual
        dropout_rate: Tasa de dropout (default: 0.1)
        t_norm: Tipo de t-norm a usar (default: product)
        epsilon: Valor pequeño para estabilidad numérica (default: 1e-10)
    """
    hidden_size: int
    dropout_rate: float = 0.1
    t_norm: TNormType = TNormType.PRODUCT
    epsilon: float = 1e-10

    @nn.compact
    def __call__(self, x: jnp.ndarray, training: bool = False, **kwargs) -> Dict[str, Any]:
        """Aplica procesamiento de conceptos platónicos.
        
        Args:
            x: Tensor de entrada de forma (batch_size, hidden_size)
            training: Si está en modo entrenamiento
            **kwargs: Argumentos adicionales
            
        Returns:
            Diccionario con:
                - output: Conceptos procesados
                - metrics: Métricas del procesamiento
                - training: Flag de modo entrenamiento
        """
        # Validación de entrada
        assert x.ndim == 2, f"La entrada debe ser 2D, se obtuvo {x.ndim}D"
        assert x.shape[-1] == self.hidden_size or x.shape[-1] % 2 == 0, (
            "La última dimensión debe coincidir con hidden_size o ser par para operaciones por pares"
        )

        # Normalización y proyección conceptual
        x = nn.LayerNorm(name="concept_norm")(x)
        x = nn.Dense(self.hidden_size, name="concept_proj")(x)
        
        # Aplicar operaciones platónicas
        x = self._apply_platonic_ops(x)
        
        # Aplicar dropout si está entrenando
        x = nn.Dropout(
            rate=self.dropout_rate,
            deterministic=not training,
            name="concept_dropout"
        )(x)
            
        return {
            "output": x,
            "metrics": self._compute_metrics(x),
            "training": training
        }

    def _apply_platonic_ops(self, x: jnp.ndarray) -> jnp.ndarray:
        """Aplica operaciones t-norm seleccionadas.
        
        Args:
            x: Tensor de entrada
            
        Returns:
            Tensor procesado con la t-norm seleccionada
        """
        # Reorganizar para operaciones por pares
        batch_size = x.shape[0]
        x_reshaped = x.reshape(batch_size, -1, 2)
        
        # Aplicación vectorizada de t-norm
        return jax.vmap(self._get_t_norm_fn())(x_reshaped).reshape(batch_size, -1)

    def _get_t_norm_fn(self) -> Callable[[jnp.ndarray], jnp.ndarray]:
        """Retorna la función t-norm seleccionada.
        
        Returns:
            Función que implementa la t-norm seleccionada
        """
        if self.t_norm == TNormType.PRODUCT:
            return lambda x: x[..., 0] * x[..., 1]
        elif self.t_norm == TNormType.MINIMUM:
            return lambda x: jnp.minimum(x[..., 0], x[..., 1])
        elif self.t_norm == TNormType.LUKASIEWICZ:
            return lambda x: jnp.maximum(0, x[..., 0] + x[..., 1] - 1)
        elif self.t_norm == TNormType.DRASTIC:
            return lambda x: jnp.where(
                jnp.maximum(x[..., 0], x[..., 1]) == 1,
                jnp.minimum(x[..., 0], x[..., 1]),
                0
            )
        elif self.t_norm == TNormType.HAMACHER:
            return lambda x: (x[..., 0] * x[..., 1]) / (
                x[..., 0] + x[..., 1] - x[..., 0] * x[..., 1] + self.epsilon
            )
        else:
            raise ValueError(f"T-norm no soportada: {self.t_norm}")

    def _compute_metrics(self, x: jnp.ndarray) -> Dict[str, jnp.ndarray]:
        """Computa métricas de calidad conceptual.
        
        Args:
            x: Tensor de conceptos procesados
            
        Returns:
            Diccionario de métricas:
                - concept_entropy: Entropía de la distribución conceptual
                - t_norm_value: Valor medio de la t-norm
                - concept_clarity: Claridad del concepto (1 - std)
                - concept_sparsity: Esparsidad de la activación conceptual
        """
        # Softmax seguro para interpretación tipo probabilidad
        concept_probs = jax.nn.softmax(x, axis=-1)
        
        # Entropía conceptual
        concept_entropy = -jnp.sum(
            concept_probs * jnp.log(concept_probs + self.epsilon),
            axis=-1
        )
        
        # Valor de t-norm
        t_norm_value = jnp.mean(x, axis=-1)
        
        # Claridad conceptual (1 - desviación estándar)
        concept_clarity = 1 - jnp.std(concept_probs, axis=-1)
        
        # Esparsidad conceptual
        concept_sparsity = jnp.mean(concept_probs < 0.1, axis=-1)
            
        return {
            "concept_entropy": concept_entropy,
            "t_norm_value": t_norm_value,
            "concept_clarity": concept_clarity,
            "concept_sparsity": concept_sparsity
        } 