"""
Módulo principal de CapibaraModel.

Este módulo proporciona la interfaz principal para el modelo Capibara,
incluyendo sus componentes principales y utilidades.
"""

from typing import Optional, Dict, Any
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Importaciones principales
from .config import CapibaraConfig
from .model import DynamicCapibaraModel
from .optimizer import OptimizerConfig
from .inference import CapibaraInference

# Importaciones de módulos de personalidad
from modules.personality.personality_manager import PersonalityManager
from modules.personality.ethics_module import EthicsModule
from modules.personality.conversation_manager import ConversationManager
from modules.personality.response_generator import ResponseGenerator

# Importaciones de capas
from capibara_model.layers.sparsity.bitnet import Conv1DBlock

# Importaciones de utilidades
from capibara_model.utils.formatters import load_tokenizer

# Versión del modelo
__version__ = "2.0.0"

# Configuración por defecto
def get_default_config() -> CapibaraConfig:
    """Retorna la configuración por defecto del modelo."""
    return CapibaraConfig()

# Inicialización del modelo
def create_model(config: Optional[CapibaraConfig] = None) -> DynamicCapibaraModel:
    """
    Crea una instancia del modelo Capibara con la configuración especificada.
    
    Args:
        config: Configuración opcional del modelo. Si no se proporciona,
                se usa la configuración por defecto.
                
    Returns:
        Una instancia de DynamicCapibaraModel.
    """
    if config is None:
        config = get_default_config()
    return DynamicCapibaraModel(config)
