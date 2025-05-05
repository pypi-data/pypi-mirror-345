"""
Dataset implementation for CapibaraModel (Versión 2.0)

Este módulo implementa un dataset optimizado para JAX con las siguientes características:
- Validación cruzada integrada
- Gestión eficiente de memoria
- Compatibilidad con TPU/GPU
- Soporte para datos comprimidos
"""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
import logging
import numpy as np # type: ignore
from typing import Dict, Any, List, Optional, Iterator, Tuple, Union, cast, Generator
from pathlib import Path
from functools import partial
from dataclasses import dataclass, field
import json
import hashlib
import gzip
import shutil
from sklearn.model_selection import KFold # type: ignore

# Configuración de logging
logger = logging.getLogger(__name__)

class DataProcessingError(Exception):
    """Error en el procesamiento de datos."""
    pass

@dataclass
class DatasetConfig:
    """Configuración del dataset."""
    batch_size: int = 32
    max_length: int = 512
    shuffle_buffer_size: int = 1000
    prefetch_size: int = 2
    num_parallel_calls: int = 4
    seed: int = 42
    task_type: str = 'text'
    compression: bool = True
    max_value: int = 255
    memory_optimization: Dict[str, Any] = field(default_factory=lambda: {
        'offload_to_cpu': True,
        'gradient_checkpointing': True,
        'remat_frequency': 4
    })
    validation: Dict[str, Any] = field(default_factory=lambda: {
        'n_splits': 5,
        'metrics': ['loss', 'accuracy'],
        'shuffle': True
    })

    def __post_init__(self):
        """Inicialización post-construcción."""
        if self.memory_optimization is None:
            self.memory_optimization = {
                'offload_to_cpu': True,
                'gradient_checkpointing': True,
                'remat_frequency': 4
            }
        if self.validation is None:
            self.validation = {
                'n_splits': 5,
                'metrics': ['loss', 'accuracy'],
                'shuffle': True
            }

class JAXDataset:
    """Dataset unificado usando JAX para procesamiento eficiente."""
    
    def __init__(self, config: DatasetConfig):
        """
        Inicializa el dataset.
        
        Args:
            config: Configuración del dataset
        """
        self.config = config
        self.rng = jax.random.PRNGKey(config.seed)
        self._data = None
        self._tokenizer = None
        self._kfold = KFold(
            n_splits=config.validation['n_splits'],
            shuffle=config.validation['shuffle'],
            random_state=config.seed
        )
        
    def get_kfold_splits(self) -> Generator[Tuple[jnp.ndarray, jnp.ndarray], None, None]:
        """
        Genera splits para validación cruzada.
        
        Yields:
            Tuplas de (train_indices, val_indices)
        """
        if self._data is None:
            raise DataProcessingError("No hay datos disponibles para validación")
            
        indices = jnp.arange(len(self._data))
        for train_idx, val_idx in self._kfold.split(indices):
            yield jnp.array(train_idx), jnp.array(val_idx)
            
    def optimize_memory(self, batch: Dict[str, jnp.ndarray]) -> Dict[str, jnp.ndarray]:
        """
        Optimiza el uso de memoria del batch.
        
        Args:
            batch: Batch a optimizar
            
        Returns:
            Batch optimizado
        """
        if not self.config.memory_optimization['offload_to_cpu']:
            return batch
            
        # Convertir a CPU si es necesario
        return jax.tree_map(
            lambda x: jax.device_put(x, jax.devices('cpu')[0]),
            batch
        )
        
    def load_from_file(self, file_path: Union[str, Path]) -> None:
        """
        Carga datos desde un archivo.
        
        Args:
            file_path: Ruta al archivo de datos
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise DataProcessingError(f"Archivo no encontrado: {path}")
                
            # Cargar datos según el tipo de archivo
            if path.suffix == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                raise DataProcessingError(f"Formato de archivo no soportado: {path.suffix}")
                
            # Convertir a arrays JAX
            self._data = jax.tree_map(
                lambda x: jnp.array(x) if isinstance(x, (np.ndarray, list)) else x,
                data
            )
            
            logger.info(f"Datos cargados desde {path}")
            
        except Exception as e:
            logger.error(f"Error cargando datos: {str(e)}")
            raise
            
    def preprocess(self, tokenizer: Any) -> None:
        """
        Preprocesa los datos usando el tokenizador.
        
        Args:
            tokenizer: Instancia del tokenizador
        """
        try:
            if self._data is None:
                raise DataProcessingError("No hay datos cargados para preprocesar")
                
            self._tokenizer = tokenizer
            
            # Tokenizar y preparar batches
            def tokenize_batch(batch):
                return tokenizer(
                    batch,
                    max_length=self.config.max_length,
                    padding='max_length',
                    truncation=True,
                    return_tensors='jax'
                )
                
            # Aplicar tokenización en batches
            self._data = jax.vmap(tokenize_batch)(self._data)
            
            logger.info("Datos preprocesados exitosamente")
            
        except Exception as e:
            logger.error(f"Error en preprocesamiento: {str(e)}")
            raise
            
    def get_batch(self, batch_size: Optional[int] = None) -> Dict[str, jnp.ndarray]:
        """
        Obtiene un batch de datos.
        
        Args:
            batch_size: Tamaño del batch (opcional)
            
        Returns:
            Diccionario con los tensores del batch
        """
        try:
            if self._data is None:
                raise DataProcessingError("No hay datos disponibles")
                
            batch_size = batch_size or self.config.batch_size
            
            # Obtener índices aleatorios
            self.rng, subkey = jax.random.split(self.rng)
            indices = jax.random.permutation(
                subkey, 
                jnp.arange(len(self._data))
            )[:batch_size]
            
            # Obtener batch
            batch = jax.tree_map(
                lambda x: x[indices],
                self._data
            )
            
            # Optimizar memoria si está configurado
            if self.config.memory_optimization['offload_to_cpu']:
                batch = self.optimize_memory(batch)
                
            return batch
            
        except Exception as e:
            logger.error(f"Error obteniendo batch: {str(e)}")
            raise
            
    def get_iterator(self) -> jax.tree_util.Partial:
        """
        Crea un iterador para los datos.
        
        Returns:
            Función parcial que devuelve batches
        """
        try:
            return jax.tree_util.Partial(self.get_batch)
            
        except Exception as e:
            logger.error(f"Error creando iterador: {str(e)}")
            raise
            
    def validate_batch(self, batch: Dict[str, jnp.ndarray]) -> bool:
        """
        Valida un batch de datos.
        
        Args:
            batch: Batch a validar
            
        Returns:
            True si el batch es válido
        """
        try:
            # Verificar estructura
            required_keys = {'input_ids', 'attention_mask'}
            if not all(k in batch for k in required_keys):
                return False
                
            # Verificar dimensiones
            batch_size = batch['input_ids'].shape[0]
            if batch['attention_mask'].shape[0] != batch_size:
                return False
                
            # Verificar tipos
            if not all(isinstance(v, jnp.ndarray) for v in batch.values()):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validando batch: {str(e)}")
            return False

def validate_input_data(data: Union[List[int], jnp.ndarray], max_value: int = 255) -> None:
    """
    Valida datos de entrada.
    
    Args:
        data: Datos a validar
        max_value: Valor máximo permitido
        
    Raises:
        DataProcessingError: Si los datos son inválidos
    """
    if isinstance(data, jnp.ndarray):
        if jnp.any((data < 0) | (data > max_value)):
            raise DataProcessingError("Valores fuera de rango")
    else:
        if not all(0 <= x <= max_value for x in data):
            raise DataProcessingError("Valores fuera de rango")

def normalize_text(text: str) -> str:
    """
    Normaliza texto.
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto normalizado
        
    Raises:
        DataProcessingError: Si el texto es None
    """
    if text is None:
        raise DataProcessingError("Texto no puede ser None")
    return text.strip().lower()

def bytes_to_binary_labels(bytes_data: jnp.ndarray, threshold: int = 127) -> jnp.ndarray:
    """
    Convierte bytes a etiquetas binarias usando operaciones vectorizadas.
    
    Args:
        bytes_data: Array de bytes
        threshold: Umbral para la conversión
        
    Returns:
        Array de etiquetas binarias
    """
    validate_input_data(bytes_data)
    return jnp.where(bytes_data > threshold, 1, 0).astype(jnp.uint8)

def stream_training_data(file_path: Union[str, Path], batch_size: int = 512) -> Generator[Tuple[jnp.ndarray, jnp.ndarray], None, None]:
    """
    Stream de datos de entrenamiento.
    
    Args:
        file_path: Ruta al archivo
        batch_size: Tamaño del batch
        
    Yields:
        Tuplas de (input, target)
    """
    path = Path(file_path)
    if not path.exists():
        raise DataProcessingError(f"Archivo no encontrado: {path}")
        
    with open(path, 'rb') as file:
        while True:
            input_bytes = file.read(batch_size)
            if not input_bytes:
                break
            target_bytes = input_bytes[1:] + b'\x00'
            input_array = jnp.array(list(input_bytes), dtype=jnp.uint8)
            target_array = jnp.array(list(target_bytes), dtype=jnp.uint8)
            yield input_array, target_array

def load_preprocessed_data(file_path: Union[str, Path], compress: bool = True) -> List[Tuple[jnp.ndarray, jnp.ndarray]]:
    """
    Carga datos preprocesados.
    
    Args:
        file_path: Ruta al archivo
        compress: Si los datos están comprimidos
        
    Returns:
        Lista de tuplas (input, target)
    """
    path = Path(file_path)
    if not path.exists():
        raise DataProcessingError(f"Archivo no encontrado: {path}")
        
    try:
        if compress:
            with gzip.open(path, 'rt') as f:
                data = json.load(f)
        else:
            with open(path, 'r') as f:
                data = json.load(f)
                
        # Convertir a arrays JAX
        return [(jnp.array(x[0]), jnp.array(x[1])) for x in data]
        
    except Exception as e:
        raise DataProcessingError(f"Error cargando datos: {str(e)}")

def save_preprocessed_data(data: List[Tuple[jnp.ndarray, jnp.ndarray]], 
                         file_path: Union[str, Path], 
                         compress: bool = True) -> None:
    """
    Guarda datos preprocesados.
    
    Args:
        data: Datos a guardar
        file_path: Ruta de destino
        compress: Si se debe comprimir
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Convertir arrays JAX a listas
        serializable_data = [(x[0].tolist(), x[1].tolist()) for x in data]
        
        if compress:
            with gzip.open(path, 'wt') as f:
                json.dump(serializable_data, f)
        else:
            with open(path, 'w') as f:
                json.dump(serializable_data, f)
                
    except Exception as e:
        raise DataProcessingError(f"Error guardando datos: {str(e)}")

# Ejemplo de uso
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Crear configuración
        config = DatasetConfig(
            batch_size=32,
            max_length=512,
            shuffle_buffer_size=1000,
            memory_optimization={
                'offload_to_cpu': True,
                'gradient_checkpointing': True
            },
            validation={
                'n_splits': 5,
                'metrics': ['loss', 'accuracy']
            }
        )
        
        # Crear dataset
        dataset = JAXDataset(config)
        
        # Ejemplo de uso
        logger.info("Dataset creado exitosamente")
        
    except Exception as e:
        logger.error(f"Error en ejemplo: {str(e)}")
        raise