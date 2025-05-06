"""
Módulo de generación de respuestas para CapibaraModel.

Generates or processes responses based on context, calculating coherence
and personality scores in the process.
"""

import jax  # type: ignore
import jax.numpy as jnp  # type: ignore
from flax import linen as nn  # type: ignore
import logging
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field #type:ignore 
from jax.experimental import debugger #type: ignore

from capibara_model.interfaces.imodules import IModule, ModuleOutput # type: ignore
from capibara_model.modules.personality.personality_manager import PersonalityManager, PersonalityConfig
from capibara_model.core.optimizer import distributed_jit, MODEL_SHARDING, REPLICATED

logger = logging.getLogger(__name__)

class ResponseConfig(BaseModel):
    """Configuración del generador de respuestas."""
    hidden_size: int = Field(default=256, gt=0)
    num_heads: int = Field(default=8, gt=0)
    dropout_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    coherence_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    personality_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    dynamic_scaling: bool = Field(default=True)
    use_attention: bool = Field(default=True)
    coherence_network_size: int = Field(default=128, gt=0)
    personality_network_size: int = Field(default=128, gt=0)
    output_network_size: int = Field(default=256, gt=0)
    personality_config: Optional[PersonalityConfig] = None

class ResponseGenerator(nn.Module, IModule):
    """
    Generates or processes responses based on context.

    Attributes:
        config (ResponseConfig): Configuration for the module.
    """
    config: ResponseConfig

    def setup(self):
        """Initialize encoding layers, coherence and personality networks."""
        # Coherence network
        self.coherence = nn.Sequential([
            nn.Dense(self.config.coherence_network_size),
            nn.relu,
            nn.Dropout(self.config.dropout_rate),
            nn.Dense(self.config.hidden_size),
            nn.LayerNorm(),
            nn.Dense(1)  # Single coherence score
        ])

        # Personality network
        self.personality = nn.Sequential([
            nn.Dense(self.config.personality_network_size),
            nn.relu,
            nn.Dropout(self.config.dropout_rate),
            nn.Dense(self.config.hidden_size),
            nn.LayerNorm(),
            nn.Dense(self.config.hidden_size)  # Personality features
        ])

        # Attention mechanism (optional)
        if self.config.use_attention:
            self.attention = nn.MultiHeadDotProductAttention(
                num_heads=self.config.num_heads,
                qkv_features=self.config.hidden_size,
                dropout_rate=self.config.dropout_rate
            )

        # Output projection
        self.output_proj = nn.Sequential([
            nn.Dense(self.config.output_network_size),
            nn.relu,
            nn.Dropout(self.config.dropout_rate),
            nn.Dense(self.config.hidden_size),
            nn.LayerNorm(),
            nn.Dense(self.config.hidden_size)
        ])

        # Auxiliary layers
        self.norm = nn.LayerNorm()
        self.dropout = nn.Dropout(rate=self.config.dropout_rate)

        # Personality manager (optional)
        if self.config.personality_config is not None:
            self.personality_manager = PersonalityManager(
                config=self.config.personality_config
            )

    def _process_response(
        self,
        response: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False
    ) -> Dict[str, jnp.ndarray]:
        """
        Process response with context to generate output.

        Args:
            response (jnp.ndarray): shape (batch, seq_len, hidden_size).
            context (jnp.ndarray, optional): shape (batch, ctx_len, hidden_size).
            training (bool): Whether in training mode.

        Returns:
            Dict with processed outputs and scores.
        """
        # Handle missing context
        if context is None:
            logger.warning("No context provided, using zero context")
            context = jnp.zeros_like(response)

        # Apply attention if enabled
        if self.config.use_attention:
            attended = self.attention(
                response,  # query
                context,  # key
                context,  # value
                deterministic=not training
            )
        else:
            attended = response

        # Calculate coherence score
        coherence_features = self.coherence(attended)
        coherence_score = jax.nn.sigmoid(coherence_features)

        # Process personality
        personality_features = self.personality(attended)
        
        # Use personality manager if available
        if hasattr(self, 'personality_manager'):
            personality_out = self.personality_manager(
                attended,
                personality_features,
                training
            )
            personality_score = personality_out['score']
        else:
            personality_score = jax.nn.sigmoid(jnp.mean(personality_features, axis=-1))

        # Combine features
        combined = jnp.concatenate([
            attended,
            context,
            attended * context,
            attended - context,
            coherence_score,
            personality_features
        ], axis=-1)

        # Apply dynamic scaling if enabled
        if self.config.dynamic_scaling:
            scale = jnp.mean(coherence_score) * self.config.personality_weight
            combined = combined * scale

        # Final output projection
        output = self.output_proj(combined)

        # Calculate activation based on coherence threshold
        is_active = coherence_score > self.config.coherence_threshold

        # Calculate overall score
        score = jnp.mean(output, axis=-1)

        return {
            'output': output,
            'is_active': is_active,
            'score': score,
            'coherence_score': coherence_score,
            'personality_score': personality_score
        }

    @distributed_jit(in_specs=MODEL_SHARDING, out_specs=REPLICATED)
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> ModuleOutput:
        """
        Forward pass for response generation/processing.

        Args:
            x (jnp.ndarray): shape (batch, seq_len, hidden_size).
            context (jnp.ndarray, optional): shape (batch, ctx_len, hidden_size).
            training (bool): Whether in training mode.
            **kwargs: Additional arguments.

        Returns:
            ModuleOutput with generated/processed response and scores.
        """
        with debugger.breakpoint_on_error():
            try:
                logger.debug(f"Input shape: x={x.shape}")
                
                # Validate input
                if x.ndim != 3:
                    raise ValueError(f"Expected 3D input, got shape {x.shape}")

                # Process response
                result = self._process_response(x, context, training)

                # Calculate metrics
                metrics = {
                    'coherence_mean': jnp.mean(result['coherence_score']),
                    'coherence_std': jnp.std(result['coherence_score']),
                    'personality_mean': jnp.mean(result['personality_score']),
                    'personality_std': jnp.std(result['personality_score']),
                    'is_active_ratio': jnp.mean(result['is_active']),
                    'score_mean': jnp.mean(result['score']),
                    'score_std': jnp.std(result['score'])
                }

                logger.debug(f"Output shape: {result['output'].shape}")
                
                return {
                    "output": x,  # Mantenemos la entrada original
                    "is_active": result['is_active'],
                    "score": result['score'],
                    "metrics": metrics
                }

            except Exception as e:
                logger.error(f"Error en ResponseGenerator: {str(e)}")
                raise

# Example Usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create configuration
        config = ResponseConfig(
            hidden_size=256,
            num_heads=8,
            coherence_threshold=0.3,
            personality_weight=0.5,
            dropout_rate=0.1,
            use_attention=True,
            dynamic_scaling=True
        )

        # Initialize model
        key = jax.random.PRNGKey(42)
        model = ResponseGenerator(config)
        
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