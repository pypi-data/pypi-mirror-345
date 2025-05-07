"""
Config module for CapibaraModel.

This module provides configuration utilities and schemas.
"""

from .schemas import CapibaraConfig
from .validator import ConfigValidator
from .capibara_config import load_config, save_config, get_default_config

__all__ = [
    "CapibaraConfig",
    "ConfigValidator",
    "load_config",
    "save_config",
    "get_default_config"
] 