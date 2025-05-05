"""
Data loader module for CapibaraGPT model.

This module provides:
- CapibaraDataLoader: a tf.data-based loader for raw binary files.
- A factory method get_capibara_data_interface(...) that decides whether
  to use CapibaraDataLoader (binary) or CapibaraDataset (text).
- Offline preprocessing capabilities
- JAX optimizations
- Dataset registry integration
"""

from typing import Dict, Any, Iterator, Optional, Union, List
from pathlib import Path
import logging
import json
import numpy as np # type: ignore
import jax # type: ignore
import jax.numpy as jnp # type: ignore
import tensorflow as tf  # type: ignore
from pydantic import BaseModel, Field  # type: ignore
from concurrent.futures import ThreadPoolExecutor
import pyarrow as pa # type: ignore
import pyarrow.parquet as pq # type: ignore
from datasets import load_dataset # type: ignore
import requests # type: ignore
import zipfile # type: ignore
import io # type: ignore
from utils import (
    handle_error,
    DataProcessingError,
    BaseConfig,
    process_batch
)

from core.config import CapibaraConfig
from data.dataset_registry import _registry as global_registry
from data.dataset import CapibaraDataset, CapibaraByteDataset
from utils.tokenizer import CapibaraTokenizer

logger = logging.getLogger(__name__)

class DataLoaderConfig(BaseConfig):
    """Configuración para el cargador de datos."""
    batch_size: int = 32
    dataset_type: str = "huggingface"
    dataset_config: Dict[str, Any] = {}
    cache_dir: Optional[str] = None
    num_workers: int = 4
    prefetch_factor: int = 2
    dataset_path: Optional[str] = None
    shuffle: bool = True
    max_length: int = 512

class Preprocessor:
    """Handles offline preprocessing of data."""
    
    def __init__(self, config: DataLoaderConfig):
        self.config = config
        self.cache_dir = Path(config.cache_dir) if config.cache_dir else Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        
    def preprocess_and_cache(self, data: List[Dict[str, Any]], split: str) -> None:
        """Preprocesses data and caches it in Parquet format."""
        cache_path = self.cache_dir / f"{split}_preprocessed.parquet"
        
        if cache_path.exists():
            logger.info(f"Using cached preprocessed data from {cache_path}")
            return
            
        logger.info(f"Preprocessing and caching data to {cache_path}")
        
        # Convert to PyArrow table
        table = pa.Table.from_pylist(data)
        
        # Write to Parquet
        pq.write_table(table, cache_path)
        
    def load_cached(self, split: str) -> List[Dict[str, Any]]:
        """Loads preprocessed data from cache."""
        cache_path = self.cache_dir / f"{split}_preprocessed.parquet"
        if not cache_path.exists():
            raise FileNotFoundError(f"No cached data found at {cache_path}")
            
        table = pq.read_table(cache_path)
        return table.to_pylist()

class CapibaraDataLoader:
    """Cargador de datos para CapibaraGPT."""
    
    def __init__(self, config: DataLoaderConfig):
        """
        Inicializa el cargador de datos.
        
        Args:
            config: Configuración del cargador
        """
        self.config = config
        self._tf_dataset = None
        self.num_samples = 0
        
        if config.dataset_path:
            self._validate_config()
            self._tf_dataset = self._create_tf_dataset()
            self.num_samples = self._count_samples()
    
    def _validate_config(self) -> None:
        """Valida la configuración del cargador."""
        if not Path(self.config.dataset_path).exists():
            raise ValueError(f"Dataset path does not exist: {self.config.dataset_path}")
    
    def _count_samples(self) -> int:
        """Cuenta el número de muestras en el dataset."""
        count = 0
        try:
            for file_path in Path(self.config.dataset_path).rglob("*"):
                if file_path.is_file():
                    count += 1
            return count
        except Exception as e:
            raise DataProcessingError(f"Error counting samples: {e}")
    
    def _create_tf_dataset(self) -> tf.data.Dataset:
        """Crea un dataset de TensorFlow."""
        file_pattern = str(Path(self.config.dataset_path) / "*")
        ds = tf.data.Dataset.list_files(
            file_pattern,
            shuffle=self.config.shuffle,
            seed=0,
            reshuffle_each_iteration=False
        )
        
        def read_and_process(file_path):
            raw_bytes = tf.io.read_file(file_path)
            byte_array = tf.io.decode_raw(raw_bytes, tf.uint8)
            byte_array = byte_array[:self.config.max_length]
            
            # Padding para longitud fija
            pad_length = self.config.max_length - tf.shape(byte_array)[0]
            byte_array = tf.pad(
                byte_array,
                paddings=[[0, pad_length]],
                mode='CONSTANT',
                constant_values=0
            )
            byte_array.set_shape([self.config.max_length])
            
            # Crear inputs y targets
            inputs = byte_array[:-1]
            targets = byte_array[1:]
            
            # Generar máscara de atención
            attention_mask = tf.ones_like(inputs, dtype=tf.int32)
            
            return {
                'inputs': inputs,
                'targets': targets,
                'attention_mask': attention_mask
            }
        
        ds = ds.map(read_and_process, num_parallel_calls=tf.data.AUTOTUNE)
        ds = ds.batch(self.config.batch_size, drop_remainder=True)
        ds = ds.prefetch(tf.data.AUTOTUNE)
        
        # Optimizaciones para JAX
        options = tf.data.Options()
        options.experimental_distribute.auto_shard_policy = (
            tf.data.experimental.AutoShardPolicy.DATA
        )
        ds = ds.with_options(options)
        return ds
    
    @handle_error(DataProcessingError)
    def load_dataset(self) -> Any:
        """
        Carga el dataset según la configuración.
        
        Returns:
            Dataset cargado
        """
        if self.config.dataset_type == "huggingface":
            return self._load_huggingface_dataset(self.config.dataset_config)
        elif self.config.dataset_type == "url":
            return self._load_url_dataset(self.config.dataset_config)
        else:
            raise DataProcessingError(f"Tipo de dataset no soportado: {self.config.dataset_type}")
    
    @handle_error(DataProcessingError)
    def _load_huggingface_dataset(self, config: Dict[str, Any]) -> Any:
        """
        Carga un dataset de Hugging Face.
        
        Args:
            config: Configuración del dataset
            
        Returns:
            Dataset de Hugging Face
        """
        dataset = load_dataset(
            config['identifier'],
            split=config.get('split', 'train'),
            cache_dir=self.config.cache_dir
        )
        return dataset
    
    @handle_error(DataProcessingError)
    def _load_url_dataset(self, config: Dict[str, Any]) -> Path:
        """
        Carga un dataset desde una URL.
        
        Args:
            config: Configuración del dataset
            
        Returns:
            Ruta al dataset descargado
        """
        response = requests.get(config['url'])
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall("temp_data")
            
        # Ejecutar script de procesamiento si existe
        if 'processing_script' in config:
            import subprocess
            subprocess.run(['python', config['processing_script']])
            
        return Path("temp_data")
    
    def __iter__(self) -> Iterator[Dict[str, tf.Tensor]]:
        """Iterador sobre el dataset."""
        if self._tf_dataset is None:
            raise DataProcessingError("Dataset no inicializado")
        return iter(self._tf_dataset)
    
    def __len__(self) -> int:
        """Longitud del dataset en batches."""
        if self.num_samples == 0:
            return 0
        return (self.num_samples + self.config.batch_size - 1) // self.config.batch_size
    
    def __del__(self):
        """Limpieza al destruir el objeto."""
        try:
            if self._tf_dataset is not None:
                del self._tf_dataset
        except Exception:
            pass

# Factory function remains unchanged
from capibara_model.data.dataset import CapibaraDataset, DatasetConfig  # type: ignore
from capibara_model.tokenizer import CapibaraTokenizer  # type: ignore

def get_capibara_data_interface(
    config: Dict[str, Any], 
    split: str = 'train'
) -> Union[CapibaraDataLoader, CapibaraDataset]:
    """Obtiene la interfaz de datos según la configuración y el split."""
    data_mode = config['data'].get('data_mode', 'text')
    
    if data_mode == 'text':
        dataset_config = DatasetConfig(
            batch_size=config['training'].get('batch_size', 32),
            max_seq_length=config['model'].get('max_seq_length', 512),
            shuffle_buffer_size=config['training'].get('shuffle_buffer_size', 10000),
            seed=config['training'].get('seed', 42)
        )
        tokenizer = CapibaraTokenizer.from_config(config['tokenizer'])
        
        if 'texts' in config['data']:
            texts = config['data']['texts'][split]
            return CapibaraDataset(
                config=dataset_config,
                tokenizer=tokenizer,
                texts=texts
            )
        elif 'train_data_path' in config['training']:
            path = config['training'][f'{split}_data_path']
            return CapibaraDataset.from_file(path, tokenizer=tokenizer)
        else:
            raise ValueError(f"No valid text source found in config for split {split}")
    else:
        return CapibaraDataLoader(config=DataLoaderConfig(**config['data']), split=split)

if __name__ == "__main__":
    try:
        logger.info("Starting DataLoader example")
        
        # Test config
        config = DataLoaderConfig(
            dataset_path="./data/binary",
            batch_size=32,
            shuffle=True,
            num_workers=4,
            max_length=512,
            preprocess_offline=True,
            cache_dir="./cache"
        )

        # Test different batch sizes
        for batch_size in [1, 32, 64]:
            logger.info(f"Testing with batch_size={batch_size}")
            test_config = config.copy()
            test_config.batch_size = batch_size
            loader = CapibaraDataLoader(config=test_config)
            logger.info(f"Created loader with {len(loader)} batches")
            for batch in loader:
                logger.debug(f"Batch shapes: bytes={batch['bytes'].shape}")
                break

        # Test invalid path
        try:
            invalid_config = config.copy()
            invalid_config.dataset_path = "/invalid/path"
            loader = CapibaraDataLoader(config=invalid_config)
        except ValueError as ve:
            logger.info(f"Caught expected ValueError: {ve}")

        logger.info("DataLoader example completed successfully")

    except Exception as e:
        logger.error(f"Error in DataLoader example: {str(e)}")
        raise