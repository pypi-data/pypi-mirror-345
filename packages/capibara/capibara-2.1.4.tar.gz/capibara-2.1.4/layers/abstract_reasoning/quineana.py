"""Implementación de la capa Quineana para procesamiento lógico.

Esta capa implementa operaciones lógicas inspiradas en la filosofía de Quine,
incluyendo cuantificación y reducción de variables mediante equivalencias lógicas.
"""

import enum
from typing import Dict, Any, Optional, Tuple

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from interfaces.ilayer import ILayer # type: ignore


class QuantificationType(enum.Enum):
    """Tipos de cuantificación soportados."""
    NONE = "none"  # Sin cuantificación
    EXISTENTIAL = "existential"  # Cuantificación existencial
    UNIVERSAL = "universal"  # Cuantificación universal
    BOTH = "both"  # Ambas cuantificaciones
    
    def get_output_dim(self, input_dim: int) -> int:
        """Calcula la dimensión de salida según el tipo de cuantificación.
        
        Args:
            input_dim: Dimensión de entrada
            
        Returns:
            Dimensión de salida
        """
        if self == QuantificationType.NONE:
            return input_dim
        elif self == QuantificationType.BOTH:
            return 2  # Existencial y universal
        else:
            return 1  # Solo existencial o universal
            
    def requires_quantification(self) -> bool:
        """Indica si este tipo requiere cuantificación.
        
        Returns:
            True si requiere cuantificación, False en caso contrario
        """
        return self != QuantificationType.NONE


class ReductionMethod(enum.Enum):
    """Métodos de reducción de variables."""
    LOGICAL_EQUIVALENCE = "logical_equivalence"  # Equivalencia lógica
    ENTROPY_MINIMIZATION = "entropy_minimization"  # Minimización de entropía
    SPARSE_PROJECTION = "sparse_projection"  # Proyección dispersa
    
    def get_threshold(self) -> float:
        """Obtiene el umbral para la reducción.
        
        Returns:
            Umbral para el método de reducción
        """
        if self == ReductionMethod.LOGICAL_EQUIVALENCE:
            return 0.5
        elif self == ReductionMethod.SPARSE_PROJECTION:
            return 0.5
        else:  # ENTROPY_MINIMIZATION
            return 0.0  # Se calcula dinámicamente
            
    def requires_entropy(self) -> bool:
        """Indica si este método requiere cálculo de entropía.
        
        Returns:
            True si requiere entropía, False en caso contrario
        """
        return self == ReductionMethod.ENTROPY_MINIMIZATION


class Quineana(nn.Module, ILayer):
    """Capa de procesamiento lógico inspirada en Quine con cuantificación y reducción de variables.
    
    Implementa conceptos filosóficos de Quine en operaciones lógicas incluyendo:
    - Cuantificación existencial y universal
    - Reducción de variables mediante equivalencias lógicas
    - Métricas de consistencia lógica basadas en entropía
    
    Args:
        hidden_size: Dimensión del espacio lógico
        dropout_rate: Tasa de dropout (default: 0.1)
        quantification: Tipo de cuantificación a aplicar (default: both)
        reduction: Método de reducción de variables (default: logical_equivalence)
        epsilon: Valor pequeño para estabilidad numérica (default: 1e-10)
    """
    hidden_size: int
    dropout_rate: float = 0.1
    quantification: QuantificationType = QuantificationType.BOTH
    reduction: ReductionMethod = ReductionMethod.LOGICAL_EQUIVALENCE
    epsilon: float = 1e-10

    @nn.compact
    def __call__(self, x: jnp.ndarray, training: bool = False, **kwargs) -> Dict[str, Any]:
        """Aplica procesamiento lógico Quineano.
        
        Args:
            x: Tensor de entrada de forma (batch_size, hidden_size)
            training: Si está en modo entrenamiento
            **kwargs: Argumentos adicionales
            
        Returns:
            Diccionario con:
                - output: Tensor lógico procesado
                - metrics: Métricas del procesamiento
                - training: Flag de modo entrenamiento
        """
        # Validación de entrada
        assert x.ndim == 2, f"La entrada debe ser 2D, se obtuvo {x.ndim}D"
        
        # Normalización y proyección lógica
        x = nn.LayerNorm(name="logic_norm")(x)
        x = nn.Dense(self.hidden_size, name="logic_proj")(x)
        
        # Aplicar cuantificación
        x = self._apply_quantification(x)
        
        # Aplicar reducción de variables
        x, reduction_metrics = self._reduce_variables(x)
        
        # Aplicar dropout si está entrenando
        x = nn.Dropout(
            rate=self.dropout_rate,
            deterministic=not training,
            name="logic_dropout"
        )(x)
            
        # Computar métricas
        metrics = self._compute_metrics(x)
        metrics.update(reduction_metrics)
            
        return {
            "output": x,
            "metrics": metrics,
            "training": training
        }

    def _apply_quantification(self, x: jnp.ndarray) -> jnp.ndarray:
        """Aplica la cuantificación seleccionada al tensor de entrada.
        
        Args:
            x: Tensor de entrada de forma (batch_size, hidden_size)
            
        Returns:
            Tensor cuantificado de forma (batch_size, output_dim)
        """
        if not self.quantification.requires_quantification():
            return x
            
        results = []
        
        # Cuantificación existencial (max)
        if self.quantification in [QuantificationType.EXISTENTIAL, QuantificationType.BOTH]:
            existential = jnp.max(x, axis=-1, keepdims=True)
            results.append(existential)
            
        # Cuantificación universal (min)
        if self.quantification in [QuantificationType.UNIVERSAL, QuantificationType.BOTH]:
            universal = jnp.min(x, axis=-1, keepdims=True)
            results.append(universal)
            
        # Combinar resultados
        if len(results) > 0:
            return jnp.concatenate(results, axis=-1)
            
        return x

    def _reduce_variables(self, x: jnp.ndarray) -> Tuple[jnp.ndarray, Dict[str, jnp.ndarray]]:
        """Reduce variables usando el método seleccionado.
        
        Args:
            x: Tensor de entrada de forma (batch_size, hidden_size)
            
        Returns:
            Tupla de (tensor reducido, métricas de reducción)
        """
        metrics = {}
        threshold = self.reduction.get_threshold()
        
        if self.reduction == ReductionMethod.LOGICAL_EQUIVALENCE:
            # Reducción por equivalencia lógica
            equiv = jnp.logical_and(x > threshold, x < threshold)
            reduced = x * (1 - equiv)
            metrics["reduction_ratio"] = jnp.mean(equiv)
            
        elif self.reduction == ReductionMethod.ENTROPY_MINIMIZATION:
            # Reducción basada en entropía
            probs = jax.nn.softmax(x, axis=-1)
            entropy = -jnp.sum(probs * jnp.log(probs + self.epsilon), axis=-1)
            mask = entropy < jnp.median(entropy)
            reduced = x * mask[..., None]
            metrics["reduction_ratio"] = jnp.mean(mask)
            
        elif self.reduction == ReductionMethod.SPARSE_PROJECTION:
            # Proyección dispersa
            reduced = jax.nn.relu(x - threshold)
            metrics["reduction_ratio"] = jnp.mean(reduced > 0)
            
        else:
            reduced = x
            metrics["reduction_ratio"] = jnp.zeros(x.shape[0])
            
        return reduced, metrics

    def _compute_metrics(self, x: jnp.ndarray) -> Dict[str, jnp.ndarray]:
        """Computa métricas del procesamiento lógico.
        
        Args:
            x: Tensor lógico procesado
            
        Returns:
            Diccionario de métricas:
                - logic_entropy: Entropía de la distribución lógica
                - logic_consistency: Puntuación de consistencia
                - logic_sparsity: Esparsidad de activaciones
                - logic_polarity: Sesgo hacia verdadero/falso
        """
        # Softmax seguro para interpretación tipo probabilidad
        logic_probs = jax.nn.softmax(x, axis=-1)
        
        # Entropía lógica
        logic_entropy = -jnp.sum(
            logic_probs * jnp.log(logic_probs + self.epsilon),
            axis=-1
        )
        
        # Consistencia lógica (1 - varianza)
        logic_consistency = 1 - jnp.std(logic_probs, axis=-1)
        
        # Esparsidad lógica
        logic_sparsity = jnp.mean(logic_probs < 0.1, axis=-1)
        
        # Polaridad lógica (sesgo hacia verdadero/falso)
        logic_polarity = jnp.mean(jnp.where(x > 0.5, 1, -1), axis=-1)
            
        return {
            "logic_entropy": logic_entropy,
            "logic_consistency": logic_consistency,
            "logic_sparsity": logic_sparsity,
            "logic_polarity": logic_polarity
        } 