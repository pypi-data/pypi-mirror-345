"""
Liquid layer implementation for CapibaraModel.

This layer expands the input dimension by an expansion factor, processes it,
then contracts back to the original dimension. Includes a residual connection
and optional dropout.

Example:
    >>> config = LiquidConfig(
    ...     hidden_size=256,
    ...     expansion_factor=4,
    ...     dropout_rate=0.1,
    ...     activation="gelu"
    ... )
    >>> layer = Liquid(config)
    >>> x = jnp.ones((32, 10, 256))
    >>> output = layer(x, training=True)
"""

import jax  # type: ignore
import jax.numpy as jnp  # type: ignore
from flax import linen as nn  # type: ignore
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field # type: ignore

from interfaces.isub_models import IExperimentalModel

logger = logging.getLogger(__name__)

class LiquidConfig(BaseModel):
    """Configuración para capa Liquid."""
    hidden_size: int
    expansion_factor: int = Field(default=4, gt=0)
    use_residual: bool = True
    activation: str = Field(default="gelu")

class Liquid(nn.Module, IExperimentalModel):
    """Capa con expansión/contracción dinámica."""
    
    config: LiquidConfig
    
    def setup(self):
        """Inicializa componentes."""
        self.expand = nn.Dense(
            self.config.hidden_size * self.config.expansion_factor
        )
        self.contract = nn.Dense(self.config.hidden_size)
        self.norm = nn.LayerNorm()
        
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Forward pass."""
        # Validar entrada
        self.validate_input(x)
        
        # Expansión
        x = self.expand(x)
        x = nn.gelu(x)
        
        # Contracción
        x = self.contract(x)
        
        # Residual
        if self.config.use_residual:
            x = x + kwargs.get("residual", x)
            
        # Normalización
        x = self.norm(x)
        
        return {
            "output": x,
            "metrics": {
                "input_norm": jnp.linalg.norm(x),
                "output_norm": jnp.linalg.norm(x),
                "expansion_ratio": self.config.expansion_factor
            }
        }
        
    def get_config(self) -> Dict[str, Any]:
        return self.config.dict()
        
    def get_metrics(self) -> Dict[str, Any]:
        return {
            "expansion_factor": self.config.expansion_factor,
            "use_residual": self.config.use_residual
        }
        
    def validate_input(self, x: jnp.ndarray) -> None:
        if x.ndim != 3:
            raise ValueError("Input must be 3D tensor")

if __name__ == "__main__":
    try:
        logger.info("Starting Liquid example")
        
        # Configuración
        config = LiquidConfig(
            hidden_size=128,
            expansion_factor=4,
            dropout_rate=0.1,
            activation="gelu"
        )

        # Test con diferentes batch sizes
        key = jax.random.PRNGKey(0)
        seq_len = 10
        
        for batch_size in [1, 32, 64]:
            logger.info(f"Testing with batch_size={batch_size}")
            
            # Crear datos de ejemplo
            x = jax.random.normal(
                key,
                (batch_size, seq_len, config.hidden_size)
            )

            # Inicializar y ejecutar modelo
            layer = Liquid(config=config)
            params = layer.init(key, x)
            output = layer.apply(params, x)
            
            logger.info(f"Test successful - Output shape: {output['output'].shape}")

        # Test con input inválido
        try:
            invalid_x = jnp.zeros((32, 10, 64))
            output = layer.apply(params, invalid_x)
        except ValueError as ve:
            logger.info(f"Caught expected ValueError: {ve}")

        logger.info("Liquid example completed successfully")

    except Exception as e:
        logger.error(f"Error in Liquid example: {str(e)}")
        raise
