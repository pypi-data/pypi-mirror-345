import jax #type: ignore
import jax.numpy as jnp #type: ignore
from flax import linen as nn #type: ignore
from typing import Tuple, Optional, Dict, Any, Callable #type: ignore
import logging
from pydantic import BaseModel, Field, validator #type: ignore
from functools import partial #type: ignore

logger = logging.getLogger(__name__)

class DeepDialogConfig(BaseModel):
    """Enhanced configuration for DeepDialog model"""
    hidden_size: int = Field(default=768, gt=0, description="Dimensión del espacio oculto")
    num_layers: int = Field(default=12, gt=0, description="Número de capas transformer")
    num_heads: int = Field(default=8, gt=0, description="Número de cabezas de atención")
    key_size: int = Field(default=64, gt=0, description="Dimensión de las claves de atención")
    dropout_rate: float = Field(default=0.1, ge=0, lt=1, description="Tasa de dropout")
    activation: str = Field(default="gelu", description="Función de activación")
    context_dim: Optional[int] = Field(default=None, description="Dimensión del contexto")
    max_seq_len: int = Field(default=512, gt=0, description="Longitud máxima de secuencia")

    @validator('activation')
    def validate_activation(cls, v):
        """Valida la función de activación"""
        valid_activations = ["gelu", "relu", "tanh", "swish", "sigmoid"]
        if v not in valid_activations:
            raise ValueError(f"Invalid activation: {v}. Valid options: {valid_activations}")
        return v

    @property
    def activation_fn(self) -> Callable:
        """Obtiene la función de activación"""
        return getattr(jax.nn, self.activation)

class DeepDialog(nn.Module):
    """Enhanced Deep Dialog Model with cross-attention support"""
    
    config: DeepDialogConfig

    def setup(self):
        """Initialize model components with dimension checks"""
        try:
            # Input projections
            self.input_proj = nn.Dense(self.config.hidden_size)
            
            # Context handling
            if self.config.context_dim:
                self.context_proj = nn.Dense(self.config.hidden_size)
                self.cross_attn_layers = [
                    CrossAttentionLayer(
                        hidden_size=self.config.hidden_size,
                        num_heads=self.config.num_heads,
                        key_size=self.config.key_size,
                        dropout_rate=self.config.dropout_rate
                    ) for _ in range(self.config.num_layers)
                ]
            
            # Main transformer layers
            self.layers = [
                TransformerLayer(
                    hidden_size=self.config.hidden_size,
                    num_heads=self.config.num_heads,
                    key_size=self.config.key_size,
                    dropout_rate=self.config.dropout_rate,
                    activation_fn=self.config.activation_fn
                ) for _ in range(self.config.num_layers)
            ]

            self.output_norm = nn.LayerNorm(epsilon=1e-6)
            
            logger.info("Model components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing model components: {e}")
            raise

    def _validate_inputs(self, inputs: jnp.ndarray, context: Optional[jnp.ndarray] = None):
        """Improved input validation for sequence data"""
        try:
            # Type validation
            if not isinstance(inputs, jnp.ndarray):
                raise TypeError(f"Expected jnp.ndarray for inputs, got {type(inputs)}")
            
            # Dimension validation
            if inputs.ndim not in [2, 3]:
                raise ValueError(
                    f"Inputs must be 2D (batch, features) or 3D (batch, seq, features). "
                    f"Got {inputs.shape}"
                )
            
            # Sequence length validation
            if inputs.ndim == 3 and inputs.shape[1] > self.config.max_seq_len:
                raise ValueError(
                    f"Sequence length {inputs.shape[1]} exceeds max_seq_len "
                    f"{self.config.max_seq_len}"
                )
            
            # Context validation
            if context is not None:
                if not isinstance(context, jnp.ndarray):
                    raise TypeError(f"Expected jnp.ndarray for context, got {type(context)}")
                    
                if context.ndim != inputs.ndim:
                    raise ValueError(
                        f"Context dim mismatch. Inputs: {inputs.ndim}D, "
                        f"Context: {context.ndim}D"
                    )
                    
                if context.shape[-1] != self.config.context_dim:
                    raise ValueError(
                        f"Context feature dim mismatch. Expected {self.config.context_dim}, "
                        f"got {context.shape[-1]}"
                    )
            
            # Value validation
            if jnp.any(jnp.isnan(inputs)) or jnp.any(jnp.isinf(inputs)):
                raise ValueError("Input contains NaN or Inf values")
            
            if context is not None and (jnp.any(jnp.isnan(context)) or jnp.any(jnp.isinf(context))):
                raise ValueError("Context contains NaN or Inf values")
            
            logger.debug(f"Input validation passed. Shapes: inputs={inputs.shape}, "
                        f"context={context.shape if context is not None else None}")
            
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            raise

    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False
    ) -> jnp.ndarray:
        """
        Enhanced forward pass with sequence support
        
        Args:
            x: Input tensor of shape (batch, seq_len, features) or (batch, features)
            context: Optional context tensor of same shape as x
            training: Whether in training mode
            
        Returns:
            Processed tensor of same shape as input
            
        Raises:
            ValueError: If input validation fails
            TypeError: If input types are invalid
            RuntimeError: If forward pass fails
        """
        try:
            logger.debug(f"Starting forward pass. Input shape: {x.shape}")
            self._validate_inputs(x, context)
            
            # Project inputs
            x = self.input_proj(x)
            
            # Process context
            if context is not None and self.config.context_dim:
                context_proj = self.context_proj(context)
                
                # Apply cross-attention layers
                for i, attn_layer in enumerate(self.cross_attn_layers):
                    x = attn_layer(x, context_proj, training)
                    logger.debug(f"Cross-attention layer {i} completed")
            
            # Process through main layers
            for i, layer in enumerate(self.layers):
                x = layer(x, training=training)
                logger.debug(f"Transformer layer {i} completed")
            
            output = self.output_norm(x)
            logger.debug(f"Forward pass completed. Output shape: {output.shape}")
            
            return output

        except ValueError as ve:
            logger.error(f"Input validation error: {ve}")
            raise
        except TypeError as te:
            logger.error(f"Type error: {te}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in forward pass: {e}")
            raise RuntimeError("Forward pass failed") from e

class CrossAttentionLayer(nn.Module):
    """Cross-attention layer for context integration"""
    hidden_size: int
    num_heads: int
    key_size: int
    dropout_rate: float

    @nn.compact
    def __call__(self, x: jnp.ndarray, context: jnp.ndarray, training: bool) -> jnp.ndarray:
        # Layer normalization
        x_norm = nn.LayerNorm(epsilon=1e-6)(x)
        context_norm = nn.LayerNorm(epsilon=1e-6)(context)
        
        # Cross-attention
        attn = nn.MultiHeadDotProductAttention(
            num_heads=self.num_heads,
            qk_features=self.key_size,
            v_features=self.key_size,
            dropout_rate=self.dropout_rate
        )(x_norm, context_norm, deterministic=not training)
        
        # Residual connection
        x = x + nn.Dropout(self.dropout_rate)(attn, deterministic=not training)
        
        # Feed-forward
        x = nn.Sequential([
            nn.Dense(self.hidden_size * 4),
            nn.relu,
            nn.Dense(self.hidden_size),
            nn.Dropout(self.dropout_rate, deterministic=not training)
        ])(x)
        
        return nn.LayerNorm(epsilon=1e-6)(x)

class TransformerLayer(nn.Module):
    """Enhanced transformer layer with improved stability"""
    hidden_size: int
    num_heads: int
    key_size: int
    dropout_rate: float
    activation_fn: Callable

    def setup(self):
        self.self_attn = nn.MultiHeadDotProductAttention(
            num_heads=self.num_heads,
            qk_features=self.key_size,
            v_features=self.key_size,
            dropout_rate=self.dropout_rate
        )
        self.ffn = nn.Sequential([
            nn.Dense(self.hidden_size * 4),
            self.activation_fn,
            nn.Dropout(self.dropout_rate),
            nn.Dense(self.hidden_size)
        ])
        self.norm1 = nn.LayerNorm(epsilon=1e-6)
        self.norm2 = nn.LayerNorm(epsilon=1e-6)

    def __call__(self, x: jnp.ndarray, training: bool) -> jnp.ndarray:
        # Self-attention
        attn_out = self.self_attn(
            inputs_q=x,
            inputs_kv=x,
            deterministic=not training
        )
        x = self.norm1(x + attn_out)
        
        # Feed-forward
        ffn_out = self.ffn(x)
        return self.norm2(x + ffn_out)

# Ejemplo de uso mejorado
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    try:
        logger.info("Starting Enhanced DeepDialog Test")
        
        # Configuración con soporte para contexto
        config = DeepDialogConfig(
            hidden_size=256,
            num_layers=6,
            num_heads=8,
            key_size=64,
            dropout_rate=0.1,
            activation="swish",
            context_dim=128,
            max_seq_len=512
        )

        # Inicializar modelo
        key = jax.random.PRNGKey(42)
        model = DeepDialog(config)
        
        # Generar datos de prueba (secuencia de diálogo)
        batch_size = 2
        seq_len = 10
        input_dim = 64
        context_dim = config.context_dim
        
        inputs = jax.random.normal(key, (batch_size, seq_len, input_dim))
        context = jax.random.normal(key, (batch_size, seq_len, context_dim))
        
        # Inicializar parámetros
        params = model.init(key, inputs, context)
        
        # Ejecutar modelo
        output = model.apply(params, inputs, context, training=True)
        
        logger.info(f"Output shape: {output.shape}")
        logger.info("Test completed successfully")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise