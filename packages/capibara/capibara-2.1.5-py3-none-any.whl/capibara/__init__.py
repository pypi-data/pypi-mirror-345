"""
CapibaraGPT - Modelo de lenguaje avanzado basado en SSM y tecnologías innovadoras.
"""

from typing import List, Optional, Union

from .version import __version__

__all__ = ["__version__"]

# Importaciones principales
try:
    from .model import CapibaraModel
    from .config import CapibaraConfig
    from .tokenizer import CapibaraTokenizer
    from .utils import set_seed, get_device

    __all__.extend([
        "CapibaraModel",
        "CapibaraConfig",
        "CapibaraTokenizer",
        "set_seed",
        "get_device",
    ])
except ImportError as e:
    import warnings
    warnings.warn(
        f"No se pudieron importar algunos módulos: {e}. "
        "Asegúrate de que todas las dependencias estén instaladas."
    )

# Configuración de logging
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__) 