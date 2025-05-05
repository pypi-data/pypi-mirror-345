"""
Módulo para manejo de errores.
"""

from functools import wraps
from typing import Type, Any, Callable
from pydantic import BaseModel

class BaseConfig(BaseModel):
    """Clase base para configuración."""
    pass

class DataProcessingError(Exception):
    """Error en el procesamiento de datos."""
    pass

class ConfigError(Exception):
    """Error en la configuración."""
    pass

def handle_error(error_type: Type[Exception]) -> Callable:
    """
    Decorador para manejo de errores.
    
    Args:
        error_type: Tipo de error a manejar
        
    Returns:
        Función decorada
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise error_type(str(e)) from e
        return wrapper
    return decorator