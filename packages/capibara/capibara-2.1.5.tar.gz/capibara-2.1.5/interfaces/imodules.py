# capibara_model/interfaces/imodules.py
"""Interfaz para módulos del modelo CapibaraGPT."""

from typing import Dict, Any, Optional
import jax.numpy as jnp #type: ignore
from abc import ABC, abstractmethod

class IModule(ABC):
    """Interfaz base para módulos del modelo."""
    
    @abstractmethod
    def __call__(
        self,
        inputs: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = True
    ) -> Dict[str, Any]:
        """Forward pass del módulo."""
        pass
