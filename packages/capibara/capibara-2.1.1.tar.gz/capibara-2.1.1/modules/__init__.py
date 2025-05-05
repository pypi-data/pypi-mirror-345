"""Módulos principales de CapibaraModel.

Este paquete contiene los módulos principales que componen el modelo CapibaraGPT.
Cada módulo implementa una funcionalidad específica y sigue la interfaz IModule.
"""

import jax #type: ignore
import logging
from typing import Dict, Any, Type

# Módulos principales
from .personality.coherence_detector import CoherenceDetector
from modules.contextual_activation import ContextualActivation
from modules.conversation_manager import ConversationManager
from personality.ethics_module import EthicsModule
from modules.personality.personality_manager import PersonalityManager
from modules.response_generator import ResponseGenerator
from modules.capivision import Mamba1DCore, SS2D, VSSBlock, Capivision

logger = logging.getLogger(__name__)

__all__ = [
    # Módulos de procesamiento
    'CoherenceDetector',
    'ContextualActivation',
    'ConversationManager',
    
    # Módulos de comportamiento
    'EthicsModule',
    'PersonalityManager',
    
    # Módulos de generación
    'ResponseGenerator',
    'CapibaraTextToSpeech',
    
    # Módulos de visión
    'Mamba1DCore',
    'SS2D',
    'VSSBlock',
    'Capivision',
]

class ModuleInitializer:
    """Inicializador de módulos.
    
    Esta clase se encarga de inicializar los módulos del modelo
    según la configuración proporcionada.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa el inicializador con la configuración.
        
        Args:
            config (Dict[str, Any]): Configuración de los módulos.
        """
        self.config = config
        self.modules: Dict[str, Any] = {}
    
    def initialize(self) -> Dict[str, Any]:
        """Inicializa todos los módulos según la configuración.
        
        Returns:
            Dict[str, Any]: Diccionario con los módulos inicializados.
        """
        try:
            # Inicializar cada módulo según su configuración
            for module_name, module_config in self.config.items():
                if module_name in globals():
                    module_class: Type = globals()[module_name]
                    self.modules[module_name] = module_class(config=module_config)
                    logger.info(f"Módulo {module_name} inicializado correctamente")
                else:
                    logger.warning(f"Módulo {module_name} no encontrado")
            
            return self.modules
            
        except Exception as e:
            logger.error(f"Error al inicializar módulos: {str(e)}")
            raise

def initialize_module(config: Dict[str, Any], module_name: str) -> Any:
    """Inicializa un único módulo.
    
    Args:
        config (Dict[str, Any]): Configuración del módulo.
        module_name (str): Nombre del módulo a inicializar.
        
    Returns:
        Any: Instancia del módulo inicializado.
    """
    try:
        if module_name in globals():
            module_class: Type = globals()[module_name]
            module = module_class(config=config)
            logger.info(f"Módulo {module_name} inicializado correctamente")
            return module
        else:
            raise ValueError(f"Módulo {module_name} no encontrado")
            
    except Exception as e:
        logger.error(f"Error al inicializar módulo {module_name}: {str(e)}")
        raise

def initialize_modules(config: Dict[str, Any]) -> Dict[str, Any]:
    """Inicializa todos los módulos del modelo.
    
    Args:
        config (Dict[str, Any]): Configuración de todos los módulos.
        
    Returns:
        Dict[str, Any]: Diccionario con todos los módulos inicializados.
    """
    initializer = ModuleInitializer(config)
    return initializer.initialize()