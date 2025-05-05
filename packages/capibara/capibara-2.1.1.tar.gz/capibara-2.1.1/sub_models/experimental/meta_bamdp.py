"""Meta BAMDP implementation for CapibaraModel."""

import jax #type: ignore
import jax.numpy as jnp #type: ignore
from flax import linen as nn #type: ignore
import logging
from typing import Tuple, Optional, Dict, Any, Callable, Union
from pydantic import BaseModel, Field  # type: ignore
from functools import partial

from interfaces.isub_models import ISubModel

logger = logging.getLogger(__name__)

class MetaBAMDPConfig(BaseModel):
    """Configuration for MetaBAMDP layer."""
    hidden_size: int = Field(..., gt=0)
    dropout_rate: float = Field(default=0.1, ge=0, lt=1)
    activation: str = Field(default="gelu")
    
    @property
    def activation_fn(self) -> Callable:
        """Get activation function."""
        activations = {
            "gelu": jax.nn.gelu,
            "relu": jax.nn.relu,
            "tanh": jax.nn.tanh
        }
        if self.activation not in activations:
            raise ValueError(f"Unknown activation: {self.activation}")
        return activations[self.activation]

class MetaBAMDP(nn.Module, ISubModel):
    """
    Meta-learning layer with BAMDP updates.
    
    Attributes:
        config: Configuration object
    """
    config: MetaBAMDPConfig

    def setup(self):
        """Initialize model parameters."""
        # Main layers
        self.encoder = nn.Dense(self.config.hidden_size)
        self.processor = nn.Dense(self.config.hidden_size)
        self.decoder = nn.Dense(self.config.hidden_size)
        
        # Auxiliary layers
        self.norm = nn.LayerNorm()
        self.dropout = nn.Dropout(rate=self.config.dropout_rate)

    def _validate_input(self, x: jnp.ndarray) -> None:
        """
        Validate input dimensions and values.
        
        Args:
            x: Input tensor
            
        Raises:
            ValueError: If input is invalid
        """
        if x.ndim != 3:
            raise ValueError(
                f"Expected 3D input (batch, seq_len, dim), got shape {x.shape}"
            )
        if jnp.any(jnp.isnan(x)) or jnp.any(jnp.isinf(x)):
            raise ValueError("Input contains NaN or Inf values")
        
        logger.debug(f"Input validation passed. Shape: {x.shape}")

    def _encode(
        self,
        x: jnp.ndarray,
        training: bool = False
    ) -> jnp.ndarray:
        """
        Encode inputs.
        
        Args:
            x: Input tensor
            training: Whether in training mode
            
        Returns:
            Encoded tensor
        """
        x = self.encoder(x)
        x = self.norm(x)
        if training:
            x = self.dropout(x, deterministic=not training)
        return self.config.activation_fn(x)

    def _process(
        self,
        x: jnp.ndarray,
        training: bool = False
    ) -> jnp.ndarray:
        """
        Process encoded representations.
        
        Args:
            x: Encoded tensor
            training: Whether in training mode
            
        Returns:
            Processed tensor
        """
        x = self.processor(x)
        x = self.norm(x)
        if training:
            x = self.dropout(x, deterministic=not training)
        return self.config.activation_fn(x)

    def _decode(
        self,
        x: jnp.ndarray,
        training: bool = False
    ) -> jnp.ndarray:
        """
        Decode processed representations.
        
        Args:
            x: Processed tensor
            training: Whether in training mode
            
        Returns:
            Decoded tensor
        """
        x = self.decoder(x)
        x = self.norm(x)
        if training:
            x = self.dropout(x, deterministic=not training)
        return x

    def _process_pipeline(
        self,
        x: jnp.ndarray,
        training: bool = False
    ) -> jnp.ndarray:
        """
        Process input through all stages.
        
        Args:
            x: Input tensor
            training: Whether in training mode
            
        Returns:
            Processed tensor
        """
        encoded = self._encode(x, training)
        processed = self._process(encoded, training)
        output = self._decode(processed, training)
        return output

    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> Union[jnp.ndarray, Tuple[jnp.ndarray, jnp.ndarray]]:
        """
        Forward pass through the layer.
        
        Args:
            x: Input tensor (batch, seq_len, dim)
            context: Optional context tensor (unused)
            training: Whether in training mode
            **kwargs: Additional arguments

        Returns:
            Union[jnp.ndarray, Tuple[jnp.ndarray, jnp.ndarray]]:
                - Output tensor, or
                - Tuple of (output, encoded)
        """
        try:
            logger.debug(f"Starting forward pass. Input shape: {x.shape}")
            self._validate_input(x)
            
            # Process input
            if jax.device_count() > 1:
                output = jax.pmap(
                    self._process_pipeline,
                    axis_name='batch'
                )(x, training)
            else:
                output = self._process_pipeline(x, training)
            
            logger.debug(f"Forward pass completed. Output shape: {output.shape}")
            
            # Return according to ISubModel interface
            if kwargs.get('return_encoded', False):
                encoded = self.encoder(x)
                return output, encoded
            return output

        except ValueError as ve:
            logger.error(f"Input validation error: {ve}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in forward pass: {e}")
            raise RuntimeError("Forward pass failed") from e


if __name__ == "__main__":
    try:
        logger.info("Starting MetaBAMDP example")
        
        # Configuración
        config = MetaBAMDPConfig(
            hidden_size=128,
            dropout_rate=0.1,
            activation="gelu"
        )

        # Test con diferentes batch sizes
        key = jax.random.PRNGKey(0)
        seq_len = 10
        input_dim = 64
        
        for batch_size in [1, 32, 64]:
            logger.info(f"Testing with batch_size={batch_size}")
            
            # Crear datos de ejemplo
            x = jax.random.normal(
                key,
                (batch_size, seq_len, input_dim)
            )

            # Inicializar y ejecutar modelo
            model = MetaBAMDP(config=config)
            params = model.init(key, x)
            output = model.apply(params, x)
            
            logger.info(f"Test successful - Output shape: {output.shape}")

        # Test con input inválido
        try:
            invalid_x = jnp.zeros((32, 10))  # Wrong dimensions
            output = model.apply(params, invalid_x)
        except ValueError as ve:
            logger.info(f"Caught expected ValueError: {ve}")

        logger.info("MetaBAMDP example completed successfully")

    except Exception as e:
        logger.error(f"Error in MetaBAMDP example: {str(e)}")
        raise
