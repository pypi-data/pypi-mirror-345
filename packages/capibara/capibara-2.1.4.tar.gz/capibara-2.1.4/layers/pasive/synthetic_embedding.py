"""
Lightweight synthetic embedding layer for CapibaraModel.

This version avoids duplicating attention, BitNet, or sparse logic that
the main model might already implement.
"""

import jax  # type: ignore
import jax.numpy as jnp  # type: ignore
from flax import linen as nn  # type: ignore
import logging
from typing import Any

from interfaces.ilayers import ILayer

logger = logging.getLogger(__name__)

class SyntheticEmbedding(nn.Module, ILayer):
    """
    A simpler synthetic embedding layer that only performs a projection
    to `hidden_size` and applies normalization + dropout.

    Attributes:
        hidden_size (int): Dimensionality of the embedding.
        dropout_rate (float): Dropout rate.
    """
    hidden_size: int
    dropout_rate: float = 0.1

    def setup(self):
        """Initialize projection and auxiliary layers."""
        # A simple dense projection to match hidden_size
        self.projection = nn.Dense(self.hidden_size)

        # Auxiliary layers
        self.norm = nn.LayerNorm()
        self.dropout = nn.Dropout(rate=self.dropout_rate)

    def __call__(
        self,
        x: jnp.ndarray,
        training: bool = False,
        **kwargs: Any
    ) -> jnp.ndarray:
        """
        Forward pass for the synthetic embedding.

        Args:
            x (jnp.ndarray): Input tensor of shape (batch_size, seq_len, input_dim).
            training (bool): Whether we're in training mode (affects dropout).
            **kwargs: Additional keyword arguments.

        Returns:
            jnp.ndarray: Embedding output of shape (batch_size, seq_len, hidden_size).
        """
        try:
            # Basic shape check
            if x.ndim != 3:
                raise ValueError(
                    f"SyntheticEmbedding expects a 3D input (batch, seq_len, dim). Got {x.shape}."
                )

            # Simple projection
            x = self.projection(x)

            # Normalization + dropout
            x = self.norm(x)
            if training:
                x = self.dropout(x, deterministic=not training)

            return x

        except Exception as e:
            logger.error(f"Error in SyntheticEmbedding forward pass: {e}")
            raise
