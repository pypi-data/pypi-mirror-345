"""Módulo de scoring común para módulos de personalidad."""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from typing import Dict, Any, Optional # type: ignore

class CommonScorer(nn.Module):
    """Módulo de scoring con thresholds dinámicos.
    
    Args:
        hidden_size: Dimensión del espacio oculto
        threshold: Valor inicial del threshold
        decay_rate: Tasa de decaimiento del threshold
    """
    hidden_size: int
    threshold: float = 0.5
    decay_rate: float = 0.99
    
    def setup(self):
        """Inicializa componentes de scoring."""
        self.dense = nn.Dense(self.hidden_size)
        self.norm = nn.LayerNorm()
        
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[Dict[str, Any]] = None,
        training: bool = False
    ) -> Dict[str, Any]:
        """Calcula score y aplica threshold dinámico.
        
        Args:
            x: Tensor de entrada (batch, seq_len, hidden_size)
            context: Contexto opcional para ajustar threshold
            training: Modo entrenamiento
            
        Returns:
            Dict con score, is_active y métricas
        """
        # Procesar entrada
        x = self.norm(x)
        x = self.dense(x)
        
        # Calcular score
        score = jax.nn.sigmoid(jnp.mean(x, axis=-1))
        
        # Ajustar threshold según contexto
        if context is not None and "threshold" in context:
            threshold = context["threshold"]
        else:
            threshold = self.threshold
            
        # Aplicar threshold
        is_active = score > threshold
        
        # Métricas
        metrics = {
            "score_mean": jnp.mean(score),
            "score_std": jnp.std(score),
            "threshold": threshold,
            "active_ratio": jnp.mean(is_active.astype(float))
        }
        
        return {
            "score": score,
            "is_active": is_active,
            "metrics": metrics
        } 