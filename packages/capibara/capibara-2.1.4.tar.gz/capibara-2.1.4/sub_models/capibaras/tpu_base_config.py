"""Configuración base para módulos optimizados para TPU."""

import jax.numpy as jnp # type: ignore
from pydantic import BaseModel, Field # type: ignore
from typing import Tuple, Optional # type: ignore

class TPUBaseConfig(BaseModel):
    """Configuración base para módulos optimizados para TPU.
    
    Args:
        hidden_size: Dimensión del espacio oculto
        shard_axis: Ejes para sharding (batch, hidden)
        dtype: Tipo de datos para TPU
        dropout_rate: Tasa de dropout
        use_mixed_precision: Usar precisión mixta
        gradient_checkpointing: Activar checkpointing de gradientes
    """
    hidden_size: int = Field(..., gt=0)
    shard_axis: Tuple[str, str] = ('batch', 'hidden')
    dtype: jnp.dtype = jnp.bfloat16
    dropout_rate: float = Field(0.1, ge=0, le=1)
    use_mixed_precision: bool = True
    gradient_checkpointing: bool = True
    
    class Config:
        arbitrary_types_allowed = True 