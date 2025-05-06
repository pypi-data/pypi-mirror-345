"""
Módulo de gestión de conversación para CapibaraModel.

Manages conversation flow with improved coherence checking and
contextual activation mechanisms.
"""

import jax #type: ignore
import jax.numpy as jnp #type: ignore
from flax import linen as nn #type: ignore
import logging
from typing import Dict, Optional, Tuple, Any #type: ignore
from dataclasses import dataclass #type: ignore
from pydantic import BaseModel, Field, validator  # type: ignore
from jax.experimental import debugger #type: ignore
from capibara_model.interfaces.imodules import IModule, ModuleOutput # type: ignore
from capibara_model.core.optimizer import distributed_jit, MODEL_SHARDING, REPLICATED # type: ignore    
from .base_config import BasePersonalityConfig
from .coherence_detector import CoherenceDetector, CoherenceConfig

logger = logging.getLogger(__name__)

@dataclass
class ConversationOutput:
    output: jnp.ndarray
    is_active: jnp.ndarray
    score: jnp.ndarray
    coherence_score: jnp.ndarray
    activation_score: jnp.ndarray

class ConversationConfig(BasePersonalityConfig):
    """Configuración específica para ConversationManager.
    
    Args:
        max_turns: Máximo número de turnos
        response_length: Longitud máxima de respuesta
        temperature: Temperatura para sampling
    """
    max_turns: int = Field(default=10, gt=0, description="Máximo número de turnos")
    response_length: int = Field(default=100, gt=0, description="Longitud máxima de respuesta")
    temperature: float = Field(default=0.7, gt=0, description="Temperatura para sampling")

    @validator('hidden_size')
    def validate_hidden_size(cls, v):
        if v % 64 != 0:
            raise ValueError("hidden_size should be divisible by 64 for optimal performance")
        return v

class ConversationManager(nn.Module, IModule):
    """Gestiona conversaciones con coherencia y personalidad."""
    
    config: ConversationConfig
    
    def setup(self):
        """Inicializa los componentes."""
        # Compartir configuración base con CoherenceDetector
        coherence_config = CoherenceConfig(**self.config.dict())
        self.coherence_detector = CoherenceDetector(coherence_config)
        
        # Inicializar otros componentes
        self.context_encoder = nn.Dense(self.config.hidden_size)
        self.response_encoder = nn.Dense(self.config.hidden_size)
        self.attention = nn.MultiHeadDotProductAttention(
            num_heads=self.config.num_heads,
            qkv_features=self.config.hidden_size
        )
        
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Procesa la entrada con coherencia y personalidad."""
        # Detectar coherencia
        coherence_result = self.coherence_detector(x, context, training=training)
        
        # Procesar con coherencia
        if coherence_result["is_coherent"]:
            # Codificar contexto y respuesta
            context_encoded = self.context_encoder(context) if context is not None else None
            response_encoded = self.response_encoder(x)
            
            # Aplicar atención
            attended = self.attention(
                response_encoded,
                context_encoded,
                deterministic=not training
            )
            
            # Métricas
            metrics = {
                "coherence_score": coherence_result["coherence_score"],
                "attention_norm": jnp.linalg.norm(attended),
                "context_shape": context.shape if context is not None else None
            }
            
            return {
                "output": attended,  # Devolver el output procesado
                "metrics": metrics,
                "is_coherent": True
            }
        else:
            return {
                "output": x,  # Mantener input original si no es coherente
                "metrics": {"coherence_score": coherence_result["coherence_score"]},
                "is_coherent": False
            }

# Example Usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create configuration
        config = ConversationConfig(
            hidden_size=256,
            num_heads=4,
            coherence_threshold=0.6,
            activation_threshold=0.5,
            dropout_rate=0.1,
            use_attention=True,
            dynamic_thresholds=True
        )

        # Initialize model
        key = jax.random.PRNGKey(42)
        model = ConversationManager(config)
        
        # Generate test data
        batch_size = 2
        seq_len = 10
        feature_dim = 128
        
        response_input = jax.random.normal(key, (batch_size, seq_len, feature_dim))
        context_input = jax.random.normal(key, (batch_size, seq_len, feature_dim))
        
        # Initialize parameters
        params = model.init(key, response_input, context_input)
        
        # Run forward pass
        output = model.apply(params, response_input, context_input, training=True)
        
        logger.info(f"Output shapes: {output['output'].shape}")
        logger.info(f"Mean score: {output['score'].mean():.2f}")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise