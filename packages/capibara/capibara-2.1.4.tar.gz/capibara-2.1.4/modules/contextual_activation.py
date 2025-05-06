"""
Enhanced Contextual Activation Module for CapibaraModel

Computes relevance between encoded inputs with improved attention mechanisms
and dynamic thresholding for activation decisions.
"""

import jax #type: ignore
import jax.numpy as jnp #type: ignore
from flax import linen as nn #type: ignore
import logging
from typing import Optional, Dict, Any, Tuple #type: ignore
from dataclasses import dataclass #type: ignore
from pydantic import BaseModel, Field, validator  # type: ignore
from jax.experimental import debugger #type: ignore

from capibara_model.interfaces.imodules import IModule, ModuleOutput
from capibara_model.core.distribution_config import distributed_jit, MODEL_SHARDING, REPLICATED

logger = logging.getLogger(__name__)

@dataclass
class ActivationOutput:
    output: jnp.ndarray
    is_active: jnp.ndarray
    score: jnp.ndarray
    attention_weights: Optional[jnp.ndarray] = None

class ContextualConfig(BaseModel):
    """Configuration for contextual activation"""
    hidden_size: int = Field(..., gt=0)
    num_heads: int = Field(default=4, gt=0)
    initial_threshold: float = Field(default=0.5, ge=0, le=1)
    dropout_rate: float = Field(default=0.1, ge=0, lt=1)
    use_attention: bool = Field(default=True)
    dynamic_threshold: bool = Field(default=False)

    @validator('hidden_size')
    def validate_hidden_size(cls, v):
        if v % 64 != 0:
            raise ValueError("hidden_size should be divisible by 64 for optimal performance")
        return v

class ContextualActivation(nn.Module, IModule):
    """
    Enhanced contextual activation module with attention mechanisms
    and dynamic thresholding capabilities.
    """
    config: ContextualConfig

    def setup(self):
        """Initialize layers and components"""
        # Encoding layers
        self.text_proj = nn.Dense(self.config.hidden_size)
        self.context_proj = nn.Dense(self.config.hidden_size)
        
        # Attention mechanism
        if self.config.use_attention:
            self.attention = nn.MultiHeadDotProductAttention(
                num_heads=self.config.num_heads,
                qkv_features=self.config.hidden_size,
                dropout_rate=self.config.dropout_rate
            )
        
        # Scoring network
        self.scoring_network = nn.Sequential([
            nn.Dense(self.config.hidden_size * 2),
            nn.relu,
            nn.Dropout(self.config.dropout_rate),
            nn.Dense(1)
        ])
        
        # Dynamic threshold parameters
        if self.config.dynamic_threshold:
            self.threshold_network = nn.Sequential([
                nn.Dense(self.config.hidden_size),
                nn.sigmoid,
                nn.Dense(1)
            ])
        
        # Normalization and dropout
        self.norm = nn.LayerNorm()
        self.dropout = nn.Dropout(self.config.dropout_rate)

    def _compute_relevance(
        self,
        text: jnp.ndarray,
        context: jnp.ndarray,
        training: bool
    ) -> Tuple[jnp.ndarray, Optional[jnp.ndarray]]:
        """
        Compute relevance score between text and context with optional attention.
        
        Args:
            text: Input text features (batch, seq_len, features)
            context: Context features (batch, seq_len, features)
            training: Training mode flag
            
        Returns:
            Tuple of (relevance scores, attention weights)
        """
        # Project inputs
        text_proj = self.text_proj(text)
        context_proj = self.context_proj(context)
        
        # Apply attention if enabled
        attention_weights = None
        if self.config.use_attention:
            text_proj = self.norm(text_proj)
            context_proj = self.norm(context_proj)
            
            attn_output = self.attention(
                inputs_q=text_proj,
                inputs_kv=context_proj,
                deterministic=not training
            )
            text_proj = text_proj + attn_output
            attention_weights = self.attention.attention_weights
        
        # Combine features
        combined = jnp.concatenate([
            text_proj,
            context_proj,
            text_proj * context_proj,
            text_proj - context_proj
        ], axis=-1)
        
        # Compute relevance scores
        scores = self.scoring_network(combined)
        return jax.nn.sigmoid(scores), attention_weights

    def _compute_threshold(
        self,
        text: jnp.ndarray,
        context: jnp.ndarray,
        training: bool
    ) -> jnp.ndarray:
        """Compute dynamic threshold based on input features"""
        if not self.config.dynamic_threshold:
            return jnp.array(self.config.initial_threshold)
        
        # Compute dynamic threshold
        features = jnp.concatenate([text.mean(axis=1), context.mean(axis=1)], axis=-1)
        return jax.nn.sigmoid(self.threshold_network(features))

    @distributed_jit(in_specs=MODEL_SHARDING, out_specs=REPLICATED)
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> ModuleOutput:
        """
        Forward pass through the activation module.
        
        Args:
            x: Input text features (batch, seq_len, features)
            context: Context features (batch, seq_len, features)
            training: Training mode flag
            **kwargs: Additional arguments
            
        Returns:
            ModuleOutput with results
        """
        with debugger.breakpoint_on_error():
            try:
                # Validate inputs
                if context is None:
                    raise ValueError("Context tensor is required")
                
                if x.ndim != 3 or context.ndim != 3:
                    raise ValueError(
                        f"Expected 3D inputs, got shapes {x.shape}, {context.shape}"
                    )
                
                if x.shape[-1] != context.shape[-1]:
                    raise ValueError(
                        f"Feature dimension mismatch: text {x.shape[-1]}, context {context.shape[-1]}"
                    )

                # Compute relevance and threshold
                relevance, attention_weights = self._compute_relevance(x, context, training)
                threshold = self._compute_threshold(x, context, training)
                
                # Determine activation
                is_active = relevance > threshold

                # Calculate metrics
                metrics = {
                    'relevance_mean': jnp.mean(relevance),
                    'relevance_std': jnp.std(relevance),
                    'threshold': jnp.mean(threshold),
                    'activation_rate': jnp.mean(is_active.astype(jnp.float32))
                }

                if attention_weights is not None:
                    metrics['attention_entropy'] = -jnp.mean(jnp.sum(
                        attention_weights * jnp.log(attention_weights + 1e-10), axis=-1
                    ))

                return {
                    "output": x,  # Mantenemos la entrada original
                    "is_active": is_active,
                    "score": relevance,
                    "metrics": metrics
                }

            except Exception as e:
                logger.error(f"Error en ContextualActivation: {str(e)}")
                raise

# Example Usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create configuration
        config = ContextualConfig(
            hidden_size=256,
            num_heads=4,
            initial_threshold=0.5,
            dropout_rate=0.1,
            use_attention=True,
            dynamic_threshold=True
        )

        # Initialize model
        key = jax.random.PRNGKey(42)
        model = ContextualActivation(config)
        
        # Generate test data
        batch_size = 2
        seq_len = 10
        feature_dim = 128
        
        text_input = jax.random.normal(key, (batch_size, seq_len, feature_dim))
        context_input = jax.random.normal(key, (batch_size, seq_len, feature_dim))
        
        # Initialize parameters
        params = model.init(key, text_input, context_input)
        
        # Run forward pass
        output = model.apply(params, text_input, context_input, training=True)
        
        logger.info(f"Output shapes: {output['output'].shape}")
        logger.info(f"Activation rate: {output['is_active'].mean():.2f}")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise