"""
Módulo para inicialización centralizada de módulos.
"""

import logging
from typing import Dict, Any, Type, Optional
from .error_handling import handle_error

logger = logging.getLogger(__name__)

class ModuleInitializer:
    """Inicializador de módulos."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el inicializador con la configuración.
        
        Args:
            config: Configuración de los módulos
        """
        self.config = config
        self.modules: Dict[str, Any] = {}
    
    @handle_error()
    def initialize(self) -> Dict[str, Any]:
        """
        Inicializa todos los módulos según la configuración.
        
        Returns:
            Dict con los módulos inicializados
        """
        for module_name, module_config in self.config.items():
            if module_name in globals():
                module_class: Type = globals()[module_name]
                self.modules[module_name] = module_class(config=module_config)
                logger.info(f"Módulo {module_name} inicializado correctamente")
            else:
                logger.warning(f"Módulo {module_name} no encontrado")
        
        return self.modules
    
    @handle_error()
    def initialize_module(
        self,
        module_name: str,
        module_config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Inicializa un único módulo.
        
        Args:
            module_name: Nombre del módulo
            module_config: Configuración específica del módulo
            
        Returns:
            Instancia del módulo inicializado
        """
        if module_name not in globals():
            raise ValueError(f"Módulo {module_name} no encontrado")
            
        config = module_config or self.config.get(module_name, {})
        module_class: Type = globals()[module_name]
        module = module_class(config=config)
        
        logger.info(f"Módulo {module_name} inicializado correctamente")
        return module
    
    def get_module(self, module_name: str) -> Any:
        """
        Obtiene un módulo inicializado.
        
        Args:
            module_name: Nombre del módulo
            
        Returns:
            Instancia del módulo
        """
        if module_name not in self.modules:
            raise ValueError(f"Módulo {module_name} no inicializado")
        return self.modules[module_name]
    
    def has_module(self, module_name: str) -> bool:
        """
        Verifica si un módulo está inicializado.
        
        Args:
            module_name: Nombre del módulo
            
        Returns:
            True si el módulo está inicializado
        """
        return module_name in self.modules 