"""Configuración centralizada para distribución en TPU y GPU."""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from jax.experimental import PartitionSpec as P # type: ignore
from jax.experimental.maps import Mesh # type: ignore
from jax.experimental.maps import mesh # type: ignore
from jax.experimental.maps import shard_map # type: ignore
from functools import wraps, partial
import logging
from typing import Optional, Tuple, Dict, Any, Callable, List, Union, TypeVar, cast
import numpy as np # type: ignore
from jax.experimental.pjit import pjit # type: ignore

logger = logging.getLogger(__name__)

# Tipos genéricos para funciones
F = TypeVar('F', bound=Callable[..., Any])
R = TypeVar('R')

# Configuración de malla TPU
TPU_MESH_SHAPE = (32, 1)  # Forma estándar para TPU v4
TPU_MESH = None  # Se inicializará en setup_mesh()

# Especificaciones de sharding comunes
BATCH_SHARDING = P('batch', None)
MODEL_SHARDING = P(None, 'model')
HYBRID_SHARDING = P('batch', 'model')
REPLICATED = P(None, None)

# Tipos de datos
DTYPE = jnp.float32
TPU_DTYPE = jnp.bfloat16

def setup_mesh(shape: Tuple[int, ...] = TPU_MESH_SHAPE) -> Mesh:
    """Inicializa la malla TPU global.
    
    Args:
        shape: Forma de la malla (por defecto TPU_MESH_SHAPE)
        
    Returns:
        Malla de dispositivos JAX
    """
    global TPU_MESH
    
    devices = jax.devices()
    if len(devices) != np.prod(shape):
        logger.warning(
            f"Forma de malla {shape} no coincide con {len(devices)} dispositivos. "
            f"Ajustando a forma ({len(devices)}, 1)"
        )
        shape = (len(devices), 1)
    
    TPU_MESH = mesh(devices, ('batch', 'model'))
    return TPU_MESH

def get_mesh() -> Mesh:
    """Obtiene la malla TPU global."""
    if TPU_MESH is None:
        return setup_mesh()
    return TPU_MESH

def distributed_jit(
    in_specs: Optional[Union[P, List[P], Tuple[P, ...]]] = None,
    out_specs: Optional[Union[P, List[P], Tuple[P, ...]]] = None,
    static_argnums: Optional[Union[int, Tuple[int, ...]]] = None,
    donate_argnums: Optional[Union[int, Tuple[int, ...]]] = None,
    mesh: Optional[Mesh] = None
) -> Callable[[F], F]:
    """Decorador unificado para JIT y shard_map.
    
    Args:
        in_specs: Especificaciones de partición para argumentos de entrada
        out_specs: Especificaciones de partición para valores de retorno
        static_argnums: Argumentos estáticos para jax.jit
        donate_argnums: Argumentos a donar para jax.jit
        mesh: Malla de dispositivos (por defecto TPU_MESH)
        
    Returns:
        Decorador que aplica JIT y shard_map
    """
    mesh = mesh or get_mesh()
    
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Aplicar shard_map con las especificaciones proporcionadas
            sharded_func = shard_map(
                func,
                mesh=mesh,
                in_specs=in_specs,
                out_specs=out_specs
            )
            
            # Aplicar JIT con los argumentos estáticos y de donación
            jitted_func = jax.jit(
                sharded_func,
                static_argnums=static_argnums,
                donate_argnums=donate_argnums
            )
            
            return jitted_func(*args, **kwargs)
        
        return cast(F, wrapper)
    
    return decorator

def model_sharded_jit(
    in_specs: Optional[Union[P, List[P], Tuple[P, ...]]] = None,
    out_specs: Optional[Union[P, List[P], Tuple[P, ...]]] = None,
    static_argnums: Optional[Union[int, Tuple[int, ...]]] = None,
    donate_argnums: Optional[Union[int, Tuple[int, ...]]] = None
) -> Callable[[F], F]:
    """Decorador específico para funciones con sharding de modelo."""
    return distributed_jit(
        in_specs=in_specs or MODEL_SHARDING,
        out_specs=out_specs or MODEL_SHARDING,
        static_argnums=static_argnums,
        donate_argnums=donate_argnums
    )

def batch_sharded_jit(
    in_specs: Optional[Union[P, List[P], Tuple[P, ...]]] = None,
    out_specs: Optional[Union[P, List[P], Tuple[P, ...]]] = None,
    static_argnums: Optional[Union[int, Tuple[int, ...]]] = None,
    donate_argnums: Optional[Union[int, Tuple[int, ...]]] = None
) -> Callable[[F], F]:
    """Decorador específico para funciones con sharding de batch."""
    return distributed_jit(
        in_specs=in_specs or BATCH_SHARDING,
        out_specs=out_specs or BATCH_SHARDING,
        static_argnums=static_argnums,
        donate_argnums=donate_argnums
    )

def hybrid_sharded_jit(
    in_specs: Optional[Union[P, List[P], Tuple[P, ...]]] = None,
    out_specs: Optional[Union[P, List[P], Tuple[P, ...]]] = None,
    static_argnums: Optional[Union[int, Tuple[int, ...]]] = None,
    donate_argnums: Optional[Union[int, Tuple[int, ...]]] = None
) -> Callable[[F], F]:
    """Decorador específico para funciones con sharding híbrido."""
    return distributed_jit(
        in_specs=in_specs or HYBRID_SHARDING,
        out_specs=out_specs or HYBRID_SHARDING,
        static_argnums=static_argnums,
        donate_argnums=donate_argnums
    )

def sharded_call(
    func: F,
    in_specs: Optional[Union[P, List[P], Tuple[P, ...]]] = None,
    out_specs: Optional[Union[P, List[P], Tuple[P, ...]]] = None,
    mesh: Optional[Mesh] = None
) -> F:
    """Aplica shard_map a una función con especificaciones personalizadas.
    
    Args:
        func: Función a aplicar shard_map
        in_specs: Especificaciones de partición para argumentos de entrada
        out_specs: Especificaciones de partición para valores de retorno
        mesh: Malla de dispositivos (por defecto TPU_MESH)
        
    Returns:
        Función con shard_map aplicado
    """
    mesh = mesh or get_mesh()
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        sharded_func = shard_map(
            func,
            mesh=mesh,
            in_specs=in_specs,
            out_specs=out_specs
        )
        return sharded_func(*args, **kwargs)
    
    return cast(F, wrapper)

def get_sharding_specs(strategy: str = "hybrid") -> Tuple[P, P]:
    """Obtiene especificaciones de sharding según la estrategia.
    
    Args:
        strategy: Estrategia de sharding ("data_parallel", "model_parallel", "hybrid")
        
    Returns:
        Tupla de (in_specs, out_specs)
    """
    if strategy == "data_parallel":
        return BATCH_SHARDING, BATCH_SHARDING
    elif strategy == "model_parallel":
        return MODEL_SHARDING, MODEL_SHARDING
    else:  # hybrid
        return HYBRID_SHARDING, HYBRID_SHARDING

# Inicializar malla al importar el módulo
setup_mesh()

# Ejemplo de uso:
# @distributed_jit(in_specs=(BATCH_SHARDING, MODEL_SHARDING), out_specs=HYBRID_SHARDING)
# def my_function(x, y):
#     return x + y

def create_unified_mesh() -> Mesh:
    """Crea una malla unificada para distribución en TPU."""
    devices = jax.devices()
    mesh_shape = (len(devices), 1)  # (data_parallel, model_parallel)
    return Mesh(devices, mesh_shape)