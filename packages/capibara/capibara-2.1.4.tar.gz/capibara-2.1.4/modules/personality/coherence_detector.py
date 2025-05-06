"""Módulo de detección de coherencia."""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from typing import Dict, Any, Optional # type: ignore
from .base_config import BasePersonalityConfig
from .common_attention import CommonAttention
from .common_scorer import CommonScorer

class CoherenceConfig(BasePersonalityConfig):
    """Configuración del módulo de coherencia."""
    coherence_threshold: float = 0.6
    context_window: int = 5
    min_coherence: float = 0.3

class CoherenceDetector(nn.Module):
    """Módulo que detecta coherencia en respuestas.
    
    Args:
        config: Configuración del módulo
    """
    config: CoherenceConfig
    
    def setup(self):
        """Inicializa componentes."""
        self.attention = CommonAttention(
            hidden_size=self.config.hidden_size,
            num_heads=self.config.num_heads,
            dropout_rate=self.config.dropout_rate
        )
        self.scorer = CommonScorer(
            hidden_size=self.config.hidden_size,
            threshold=self.config.coherence_threshold
        )
        
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[Dict[str, Any]] = None,
        training: bool = False
    ) -> Dict[str, Any]:
        """Evalúa la coherencia de la respuesta.
        
        Args:
            x: Tensor de entrada (batch, seq_len, hidden_size)
            context: Contexto opcional
            training: Modo entrenamiento
            
        Returns:
            Dict con output procesado y métricas
        """
        # Aplicar atención sobre contexto
        if context is not None and "history" in context:
            history = context["history"][-self.config.context_window:]
            history = jnp.stack(history)
            
            attention_result = self.attention(
                query=x,
                key=history,
                value=history,
                training=training
            )
        else:
            attention_result = self.attention(
                query=x,
                training=training
            )
            
        # Calcular score de coherencia
        scoring_result = self.scorer(
            attention_result["output"],
            context,
            training
        )
        
        # Combinar métricas
        metrics = {
            **attention_result["metrics"],
            **scoring_result["metrics"],
            "coherence_score": scoring_result["score"]
        }
        
        return {
            "output": attention_result["output"],
            "is_active": scoring_result["is_active"],
            "score": scoring_result["score"],
            "metrics": metrics
        }
