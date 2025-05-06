"""Módulo de ética para evaluar respuestas."""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
import logging
from typing import Dict, Any, Optional # type: ignore
from .base_config import BasePersonalityConfig
from .common_attention import CommonAttention
from .common_scorer import CommonScorer

logger = logging.getLogger(__name__)

class EthicsConfig(BasePersonalityConfig):
    """Configuración del módulo de ética."""
    ethical_threshold: float = 0.7
    ethical_concepts: Dict[str, float] = {
        "honesty": 1.0,
        "respect": 1.0,
        "fairness": 1.0,
        "harm": -1.0
    }

class EthicsModule(nn.Module):
    """Módulo que evalúa la ética de respuestas.
    
    Args:
        config: Configuración del módulo
    """
    config: EthicsConfig
    
    def setup(self):
        """Inicializa componentes."""
        self.attention = CommonAttention(
            hidden_size=self.config.hidden_size,
            num_heads=self.config.num_heads,
            dropout_rate=self.config.dropout_rate
        )
        self.scorer = CommonScorer(
            hidden_size=self.config.hidden_size,
            threshold=self.config.ethical_threshold
        )
        
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[Dict[str, Any]] = None,
        training: bool = False
    ) -> Dict[str, Any]:
        """Evalúa la ética de la respuesta.
        
        Args:
            x: Tensor de entrada (batch, seq_len, hidden_size)
            context: Contexto opcional
            training: Modo entrenamiento
            
        Returns:
            Dict con output procesado y métricas
        """
        # Aplicar atención sobre conceptos éticos
        ethical_concepts = jnp.array(list(self.config.ethical_concepts.values()))
        ethical_concepts = jnp.expand_dims(ethical_concepts, 0)  # Add batch dim
        
        attention_result = self.attention(
            query=x,
            key=ethical_concepts,
            value=ethical_concepts,
            training=training
        )
        
        # Calcular score ético
        scoring_result = self.scorer(
            attention_result["output"],
            context,
            training
        )
        
        # Combinar métricas
        metrics = {
            **attention_result["metrics"],
            **scoring_result["metrics"],
            "ethical_score": scoring_result["score"]
        }
        
        logger.debug(f"Output shape: {attention_result['output'].shape}")
        
        return {
            "output": attention_result["output"],
            "is_active": scoring_result["is_active"],
            "score": scoring_result["score"],
            "metrics": metrics
        }
