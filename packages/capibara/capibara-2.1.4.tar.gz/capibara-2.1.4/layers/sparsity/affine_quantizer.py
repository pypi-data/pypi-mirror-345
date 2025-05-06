"""Quantizador Affine para CapibaraModel (con STE para QAT)."""

import jax #type: ignore
import jax.numpy as jnp #type: ignore
import flax.linen as nn #type: ignore
from typing import Dict, Any, Optional, Union, Tuple
from functools import partial
from interfaces.ilayer import ILayer
from core.config import CapibaraConfig

# Asumimos que distributed_jit está definido como antes
# from capibara_model.core.distribution_config import distributed_jit
# Placeholder si no está disponible en este contexto:
def distributed_jit(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

class AffineQuantizer(nn.Module, ILayer):
    """
    Quantizador con transformación affine y Straight-Through Estimator (STE)
    para ser usable en Quantization-Aware Training (QAT).
    """

    def __init__(
        self,
        config: CapibaraConfig,
        name: Optional[str] = None
    ):
        super().__init__(name=name)
        self.config = config
        self.num_bits = config.model.num_bits

    def setup(self):
        """Inicializa los parámetros aprendibles del quantizador."""
        self.scale = self.param(
            'scale',
            nn.initializers.ones,
            (self.config.model.hidden_size,),
            jnp.float32
        )
        self.zero_point = self.param(
            'zero_point',
            nn.initializers.zeros,
            (self.config.model.hidden_size,),
            jnp.float32
        )

    def _quantize(self, x: jnp.ndarray) -> jnp.ndarray:
        """Aplica cuantización con STE."""
        x_scaled = x * self.scale + self.zero_point
        quant_min = 0.0
        quant_max = 2**self.num_bits - 1.0
        return jnp.clip(jnp.round(x_scaled), quant_min, quant_max)

    def _dequantize(self, x: jnp.ndarray) -> jnp.ndarray:
        """Aplica dequantización."""
        return (x - self.zero_point) / self.scale

    @distributed_jit(in_specs=None, out_specs=None)  # Aplica JIT distribuido
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> Union[jnp.ndarray, Tuple[jnp.ndarray, Dict[str, Any]]]:
        """Aplica quantización affine con STE."""
        x_quant = self._quantize(x)
        x_dequant = self._dequantize(x_quant)

        if training:
            output = x + jax.lax.stop_gradient(x_dequant - x)
        else:
            output = x_quant

        metrics = {
            'quantization_error': jnp.mean(jnp.abs(x - x_dequant)),
            'scale_mean': jnp.mean(self.scale),
            'zero_point_mean': jnp.mean(self.zero_point)
        }

        return output, metrics

    def _get_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del cuantizador."""
        return {
            "scale_mean": jnp.mean(self.scale),
            "zero_point_mean": jnp.mean(self.zero_point)
        }