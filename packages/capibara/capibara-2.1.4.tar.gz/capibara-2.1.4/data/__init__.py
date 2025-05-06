"""
Módulo de manejo de datos para CapibaraModel.

Este módulo proporciona:
- CapibaraDataLoader: Cargador de datos basado en tf.data
- Funciones de preprocesamiento de datos
- Registro de datasets
- Interfaces para diferentes tipos de datos
"""

from .data_loader import (
    CapibaraDataLoader,
    DataLoaderConfig,
    get_capibara_data_interface
)

from .dataset import (
    CapibaraDataset,
    CapibaraByteDataset
)

from .dataset_registry import (
    DatasetRegistry
)

from .data_processing import (
    DataProcessingError,
    validate_input_data,
    text_to_bytes,
    bytes_to_text,
    bytes_to_binary_labels,
    prepare_training_data,
    stream_training_data,
    save_preprocessed_data,
    process_batch
)

__all__ = [
    # Data Loader
    'CapibaraDataLoader',
    'DataLoaderConfig',
    'get_capibara_data_interface',
    
    # Datasets
    'CapibaraDataset',
    'CapibaraByteDataset',
    
    # Registry
    'DatasetRegistry',
    'register_dataset',
    'get_dataset_info',
    
    # Data Processing
    'DataProcessingError',
    'validate_input_data',
    'text_to_bytes',
    'bytes_to_text',
    'bytes_to_binary_labels',
    'prepare_training_data',
    'stream_training_data',
    'save_preprocessed_data',
    'process_batch'
]