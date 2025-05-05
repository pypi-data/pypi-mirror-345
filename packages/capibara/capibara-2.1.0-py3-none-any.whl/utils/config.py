"""
Módulo para manejo de configuración.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel #type: ignore
from .error_handling import ConfigError, handle_error

class BaseConfig(BaseModel):
    """Clase base para configuración."""
    pass

@handle_error(ConfigError)
def load_config(config_path: str) -> Dict[str, Any]:
    """
    Carga configuración desde archivo.
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        Dict con configuración
    """
    try:
        with open(config_path, 'r') as f:
            import yaml #type: ignore
            return yaml.safe_load(f)
    except Exception as e:
        raise ConfigError(f"Error cargando configuración: {str(e)}")

from utils import (
    process_batch,
    save_processed_data,
    load_processed_data,
    handle_error,
    DataProcessingError,
    ConfigError,
    BaseConfig,
    load_config
)