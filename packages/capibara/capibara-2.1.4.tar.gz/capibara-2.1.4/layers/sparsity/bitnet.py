import jax # type: ignore
import jax.numpy as jnp # type: ignore
import flax.linen as nn # type: ignore
from typing import Optional, Tuple
import logging
from config.model_config import BitNetConfig

logger = logging.getLogger(__name__)

class BitNet158(nn.Module):
    """Implementación de BitNet158 con cuantización y logging mejorado."""
    config: BitNetConfig
    
    def setup(self):
        self.quantization_scale = self.param(
            'quantization_scale',
            nn.initializers.constant(1.0),
            (1,)
        )
        
    def quantize(self, x: jnp.ndarray) -> jnp.ndarray:
        """Cuantización de los pesos."""
        try:
            scale = jnp.abs(x).max()
            x_quantized = jnp.clip(x / scale, -1, 1)
            return x_quantized * self.quantization_scale
        except Exception as e:
            logger.error(f"Error en cuantización: {e}")
            raise ValueError("Error en el proceso de cuantización") from e
            
    def __call__(self, x: jnp.ndarray) -> jnp.ndarray:
        """Forward pass con logging de métricas."""
        try:
            # Logging de memoria y tiempo
            start_time = jax.lax.stop_gradient(jax.lax.clock())
            
            # Cuantización
            x_quantized = self.quantize(x)
            
            # Transformación lineal
            x = nn.Dense(
                self.config.hidden_size,
                kernel_init=nn.initializers.normal(stddev=self.config.initializer_range)
            )(x_quantized)
            
            # Logging de métricas
            end_time = jax.lax.stop_gradient(jax.lax.clock())
            duration = end_time - start_time
            memory_usage = jax.device_memory_allocated()
            
            logger.debug(f"BitNet158 - Tiempo: {duration:.4f}s, Memoria: {memory_usage/1024/1024:.2f}MB")
            
            return x
            
        except jax.errors.JAXTypeError as e:
            logger.error(f"Error de tipo en BitNet158: {e}")
            raise ValueError("Error en los tipos de datos de entrada") from e
        except jax.errors.JAXRuntimeError as e:
            logger.error(f"Error de runtime en BitNet158: {e}")
            raise RuntimeError("Error durante la ejecución") from e
        except Exception as e:
            logger.error(f"Error inesperado en BitNet158: {e}")
            raise 