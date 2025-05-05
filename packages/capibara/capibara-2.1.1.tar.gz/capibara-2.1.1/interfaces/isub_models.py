"""Interfaces para submodelos."""

from typing import Protocol, Optional, Any, Dict, Union, Tuple
import jax.numpy as jnp # type: ignore

class ISubModel(Protocol):
    """Interfaz base para submodelos."""
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Forward pass del submodelo."""
        ...

class IExperimentalModel(ISubModel):
    """Interfaz para submodelos experimentales."""
    def get_config(self) -> Dict[str, Any]:
        """Obtiene configuración del modelo."""
        return {}
        
    def get_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del modelo."""
        return {}
        
    def validate_input(self, x: jnp.ndarray) -> None:
        """Valida formato de entrada."""
        pass 