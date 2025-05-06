"""Implementación base para capas distribuidas."""

from typing import Optional, Dict, Any, Union, Tuple
import jax # type: ignore
import jax.numpy as jnp # type: ignore
from jax.experimental import PartitionSpec as P # type: ignore

from capibara_model.interfaces.ilayer import ILayer # type: ignore
from capibara_model.core.distribution_config import (
    distributed_jit,
    model_sharded_jit,
    batch_sharded_jit,
    hybrid_sharded_jit
) # type: ignore 

class Layer(ILayer):
    """Clase base para capas con soporte de distribución."""
    
    def __init__(
        self,
        sharding_strategy: str = "hybrid",
        name: Optional[str] = None
    ):
        """Inicializa la capa base.
        
        Args:
            sharding_strategy: Estrategia de sharding
            name: Nombre opcional de la capa
        """
        super().__init__(sharding_strategy)
        self.name = name
        
        # Selecciona el decorador de distribución
        if sharding_strategy == "data_parallel":
            self.distributed_call = batch_sharded_jit(
                in_specs=self.in_specs,
                out_specs=self.out_specs
            )(self._call_impl)
        elif sharding_strategy == "model_parallel":
            self.distributed_call = model_sharded_jit(
                in_specs=self.in_specs,
                out_specs=self.out_specs
            )(self._call_impl)
        else:  # hybrid
            self.distributed_call = hybrid_sharded_jit(
                in_specs=self.in_specs,
                out_specs=self.out_specs
            )(self._call_impl)
    
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> Union[jnp.ndarray, Tuple[jnp.ndarray, Dict[str, Any]]]:
        """Forward pass con distribución.
        
        Args:
            x: Tensor de entrada
            context: Tensor de contexto opcional
            training: Si estamos en modo entrenamiento
            **kwargs: Argumentos adicionales
            
        Returns:
            Tensor de salida o tupla (output, metrics)
        """
        self._validate_input(x)
        return self.distributed_call(x, context, training, **kwargs)
    
    def _call_impl(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> Union[jnp.ndarray, Tuple[jnp.ndarray, Dict[str, Any]]]:
        """Implementación del forward pass.
        
        Args:
            x: Tensor de entrada
            context: Tensor de contexto opcional
            training: Si estamos en modo entrenamiento
            **kwargs: Argumentos adicionales
            
        Returns:
            Tensor de salida o tupla (output, metrics)
        """
        raise NotImplementedError("Subclases deben implementar _call_impl")
    
    def _get_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de la capa.
        
        Returns:
            Diccionario de métricas
        """
        return {} 