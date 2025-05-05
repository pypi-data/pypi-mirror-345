from functools import wraps
from typing import Any, Callable, List
from fastapi import Depends, Security
from .auth import get_current_active_user, User

class MCPBase:
    @staticmethod
    def require_auth(scopes: List[str] = None) -> Callable:
        """
        Decorador para requerir autenticación y scopes específicos
        
        Args:
            scopes: Lista de scopes requeridos para acceder al endpoint
            
        Returns:
            Callable: Función decorada con autenticación
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, user: User = Security(get_current_active_user, scopes=scopes or []), **kw) -> Any:
                return await func(*args, **kw)
            return wrapper
        return decorator

    @staticmethod
    def lazy_load(loader: Callable, *args, **kwargs) -> Any:
        """
        Implementación de lazy loading para dependencias pesadas
        
        Args:
            loader: Función que carga el recurso
            *args: Argumentos posicionales para el loader
            **kwargs: Argumentos nombrados para el loader
            
        Returns:
            Any: Instancia del recurso cargado
        """
        _instance = None
        
        def get_instance():
            nonlocal _instance
            if _instance is None:
                _instance = loader(*args, **kwargs)
            return _instance
            
        return get_instance 