"""Módulo para gestionar el registro central de datasets."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

from core.config import ModelConfig
from .dataset import DatasetConfig
from .dataset import CapibaraDataset, CapibaraByteDataset
from .data_loader import CapibaraDataLoader, get_capibara_data_interface

logger = logging.getLogger(__name__)

@dataclass
class CapibaraTokenizer:
    """Tokenizador simple para CapibaraGPT."""
    @classmethod
    def from_pretrained(cls, path: str) -> 'CapibaraTokenizer':
        return cls()

class DatasetRegistry:
    """Clase para gestionar el registro central de datasets."""
    
    def __init__(self, registry_path: str = "data/dataset_registry.json"):
        """Inicializa el registro de datasets.
        
        Args:
            registry_path: Ruta al archivo JSON del registro
        """
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()
        
    def _load_registry(self) -> Dict[str, Any]:
        """Carga el registro desde el archivo JSON."""
        try:
            if not self.registry_path.exists():
                logger.warning(f"Archivo de registro no encontrado: {self.registry_path}")
                return {}
                
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error cargando registro: {e}")
            return {}
            
    def get_dataset_info(self, dataset_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de un dataset por nombre.
        
        Args:
            dataset_name: Nombre del dataset en el registro
            
        Returns:
            Dict con información del dataset o None si no existe
        """
        return self.registry.get(dataset_name)
        
    def list_datasets(self) -> Dict[str, str]:
        """Lista todos los datasets disponibles con sus descripciones.
        
        Returns:
            Dict con nombres y descripciones de datasets
        """
        return {name: info.get('description', 'Sin descripción') 
                for name, info in self.registry.items()}
                
    def add_dataset(self, name: str, info: Dict[str, Any]) -> bool:
        """Añade un nuevo dataset al registro.
        
        Args:
            name: Nombre del dataset
            info: Información del dataset
            
        Returns:
            True si se añadió correctamente
        """
        try:
            if name in self.registry:
                logger.warning(f"Dataset {name} ya existe en el registro")
                return False
                
            self.registry[name] = info
            
            # Guardar cambios
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            logger.error(f"Error añadiendo dataset {name}: {e}")
            return False
            
    def update_dataset(self, name: str, info: Dict[str, Any]) -> bool:
        """Actualiza información de un dataset existente.
        
        Args:
            name: Nombre del dataset
            info: Nueva información del dataset
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            if name not in self.registry:
                logger.warning(f"Dataset {name} no existe en el registro")
                return False
                
            self.registry[name].update(info)
            
            # Guardar cambios
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando dataset {name}: {e}")
            return False

# Instancia global del registro
_registry = DatasetRegistry()

def get_dataset_from_registry(
    dataset_name: str,
    config: ModelConfig,
    split: str = "train"
) -> Union[CapibaraDataset, CapibaraByteDataset, CapibaraDataLoader]:
    """Obtiene un dataset desde el registro centralizado.
    
    Args:
        dataset_name: Nombre del dataset en el registro
        config: Configuración del modelo
        split: División del dataset a cargar (train, validation, test)
        
    Returns:
        Dataset cargado según el tipo especificado en el registro
    """
    try:
        # Obtener información del dataset desde el registro
        dataset_info = _registry.get_dataset_info(dataset_name)
        if not dataset_info:
            logger.warning(f"Dataset {dataset_name} no encontrado en el registro")
            # Fallback a dataset por defecto
            return _create_default_dataset(config, split)
            
        # Determinar el tipo de dataset según la configuración
        if config.model.model_type == "binary":
            logger.info(f"Cargando dataset binario: {dataset_name}")
            return _create_binary_dataset(dataset_info, config, split)
        else:
            logger.info(f"Cargando dataset de texto: {dataset_name}")
            return _create_text_dataset(dataset_info, config, split)
            
    except Exception as e:
        logger.error(f"Error cargando dataset {dataset_name}: {e}")
        # Fallback a dataset por defecto
        return _create_default_dataset(config, split)

def _create_default_dataset(
    config: ModelConfig,
    split: str
) -> Union[CapibaraDataset, CapibaraByteDataset]:
    """Crea un dataset por defecto cuando no se encuentra en el registro.
    
    Args:
        config: Configuración del modelo
        split: División del dataset a cargar
        
    Returns:
        Dataset por defecto
    """
    logger.info(f"Creando dataset por defecto para split {split}")
    
    # Crear tokenizador
    tokenizer = CapibaraTokenizer.from_pretrained(config.model.tokenizer_path)
    
    # Determinar ruta de datos según el split
    data_path = f"data/{split}"
    if not Path(data_path).exists():
        logger.warning(f"Ruta de datos {data_path} no encontrada, usando data/")
        data_path = "data/"
        
    # Crear configuración del dataset
    dataset_config = DatasetConfig(
        batch_size=config.training.batch_size,
        max_seq_length=config.model.max_seq_length,
        shuffle_buffer_size=config.training.shuffle_buffer_size,
        seed=config.training.seed
    )
        
    # Crear dataset según el tipo de modelo
    if config.model.model_type == "binary":
        return CapibaraByteDataset(
            config=dataset_config,
            tokenizer=tokenizer
        )
    else:
        return CapibaraDataset(
            config=dataset_config,
            tokenizer=tokenizer
        )

def _create_binary_dataset(
    dataset_info: Dict[str, Any],
    config: ModelConfig,
    split: str
) -> CapibaraByteDataset:
    """Crea un dataset binario desde la información del registro.
    
    Args:
        dataset_info: Información del dataset desde el registro
        config: Configuración del modelo
        split: División del dataset a cargar
        
    Returns:
        Dataset binario
    """
    # Obtener ruta de datos del registro o usar valor por defecto
    data_path = dataset_info.get("path", f"data/{split}")
    
    # Crear tokenizador
    tokenizer = CapibaraTokenizer.from_pretrained(config.model.tokenizer_path)
    
    # Crear configuración del dataset
    dataset_config = DatasetConfig(
        batch_size=config.training.batch_size,
        max_seq_length=config.model.max_seq_length,
        shuffle_buffer_size=config.training.shuffle_buffer_size,
        seed=config.training.seed
    )
    
    # Crear dataset binario
    return CapibaraByteDataset(
        config=dataset_config,
        tokenizer=tokenizer
    )

def _create_text_dataset(
    dataset_info: Dict[str, Any],
    config: ModelConfig,
    split: str
) -> CapibaraDataset:
    """Crea un dataset de texto desde la información del registro.
    
    Args:
        dataset_info: Información del dataset desde el registro
        config: Configuración del modelo
        split: División del dataset a cargar
        
    Returns:
        Dataset de texto
    """
    # Obtener ruta de datos del registro o usar valor por defecto
    data_path = dataset_info.get("path", f"data/{split}")
    
    # Crear tokenizador
    tokenizer = CapibaraTokenizer.from_pretrained(config.model.tokenizer_path)
    
    # Crear configuración del dataset
    dataset_config = DatasetConfig(
        batch_size=config.training.batch_size,
        max_seq_length=config.model.max_seq_length,
        shuffle_buffer_size=config.training.shuffle_buffer_size,
        seed=config.training.seed
    )
    
    # Crear dataset de texto
    return CapibaraDataset(
        config=dataset_config,
        tokenizer=tokenizer
    )