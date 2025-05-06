"""Modelo Modular con Capacidades Avanzadas."""

import jax #type: ignore
import jax.numpy as jnp #type: ignore
import flax.linen as nn #type: ignore
from typing import Dict, Any, Optional, List, Type, Callable, Union
from functools import partial

from .model import DynamicCapibaraModel
from interfaces.imodules import IModule
from .distribution_config import (
    distributed_jit,
    BATCH_SHARDING,
    MODEL_SHARDING,
    HYBRID_SHARDING,
    TPU_DTYPE,
    REPLICATED
)

class ModuleRegistry:
    """Registro dinámico de módulos."""
    
    def __init__(self) -> None:
        self._modules: Dict[str, Type[IModule]] = {}
        self._factories: Dict[str, Callable[..., IModule]] = {}
        
    def register(self, name: str, module_class: Type[IModule]) -> None:
        """Registra un nuevo módulo."""
        self._modules[name] = module_class
        
    def register_factory(self, name: str, factory: Callable[..., IModule]) -> None:
        """Registra una factory para crear módulos dinámicamente."""
        self._factories[name] = factory
        
    def get_module(self, name: str) -> Type[IModule]:
        """Obtiene una clase de módulo por nombre."""
        if name not in self._modules:
            raise KeyError(f"Módulo {name} no registrado")
        return self._modules[name]
        
    def create_module(self, name: str, **kwargs: Any) -> IModule:
        """Crea una instancia de módulo usando su factory."""
        if name not in self._factories:
            raise KeyError(f"Factory para {name} no registrada")
        return self._factories[name](**kwargs)

class Router(nn.Module):
    """Router para selección dinámica de módulos."""
    
    hidden_size: int
    num_heads: int
    dropout_rate: float
    dtype: Any = jnp.float32
    
    def setup(self):
        """Inicializa el router."""
        self.attention = nn.MultiHeadDotProductAttention(
            num_heads=self.num_heads,
            qkv_features=self.hidden_size,
            dropout_rate=self.dropout_rate,
            dtype=self.dtype
        )
        
    def __call__(self, x: jnp.ndarray, context: Optional[jnp.ndarray] = None) -> jnp.ndarray:
        """Selecciona el módulo más apropiado basado en el contexto."""
        if context is None:
            context = x
            
        # Calcular scores de atención para cada módulo
        scores = self.attention(x, context, context)
        return scores

class ModularCapibaraModel(DynamicCapibaraModel):
    """Modelo Capibara con capacidades modulares avanzadas."""
    
    def setup(self):
        """Inicializa el modelo modular."""
        super().setup()
        
        # Registro de módulos
        self.registry = ModuleRegistry()
        
        # Router para selección de módulos
        self.router = Router(
            hidden_size=self.hidden_size,
            num_heads=self.num_heads,
            dropout_rate=self.dropout_rate,
            dtype=TPU_DTYPE if self.use_tpu else jnp.float32
        )
        
        # Módulos activos
        self.active_modules: List[IModule] = []
        
    def register_module(self, name: str, module_class: Type[IModule]):
        """Registra un nuevo módulo."""
        self.registry.register(name, module_class)
        
    def register_factory(self, name: str, factory: Callable):
        """Registra una factory para crear módulos dinámicamente."""
        self.registry.register_factory(name, factory)
        
    def neurogenesis(self, module_type: str, **kwargs) -> IModule:
        """Crea dinámicamente un nuevo módulo."""
        return self.registry.create_module(module_type, **kwargs)
        
    @distributed_jit(in_specs=MODEL_SHARDING, out_specs=REPLICATED)
    def __call__(
        self,
        inputs: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = True
    ) -> Dict[str, Any]:
        """Forward pass con capacidades modulares."""
        # Embedding base
        x = self.embedding(inputs)
        
        # Selección de módulos mediante router
        if context is not None:
            module_scores = self.router(x, context)
            # TODO: Implementar lógica de selección basada en scores
            
        # Aplicar módulos activos
        for module in self.active_modules:
            result = module(x, context=context, training=training)
            x = result['output']
            
        # Aplicar transformer blocks base
        for block in self.transformer_blocks:
            x = block(x, training=training)
            
        # Obtener métricas
        metrics = {}
        if self.monitor_metrics:
            metrics = self._get_metrics()
            
        return {
            'output': x,
            'metrics': metrics,
            'is_active': True
        }