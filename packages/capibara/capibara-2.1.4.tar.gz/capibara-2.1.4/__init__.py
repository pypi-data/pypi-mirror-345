"""
Capibara - Un modelo de lenguaje basado en SSM (State Space Models)

Este paquete proporciona una implementación de un modelo de lenguaje basado en SSM,
optimizado para TPU y GPU, con soporte para entrenamiento distribuido y fine-tuning.
"""

from .core.model import DynamicCapibaraModel
from .core.config import ModelConfig
from .core.optimizer import OptimizerType
from .core.tokenizer import AutoTokenizer
from .core.interfaces import BaseModel, BaseLayer, ContentFilter
from .utils.logging import setup_logging
from .utils.system_info import SystemMonitor
from .utils.monitoring import RealTimeMonitor, ResourceMonitor
from .utils.checkpointing import CheckpointManager

__version__ = "0.1.0"

__all__ = [
    'DynamicCapibaraModel',
    'ModelConfig',
    'OptimizerType',
    'AutoTokenizer',
    'BaseModel',
    'BaseLayer',
    'ContentFilter',
    'setup_logging',
    'SystemMonitor',
    'RealTimeMonitor',
    'ResourceMonitor',
    'CheckpointManager'
]
