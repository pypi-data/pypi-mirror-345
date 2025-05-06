"""
jax_data_processing.py

Este módulo proporciona funciones para el preprocesamiento de datos optimizado para JAX/TPU.
Incluye funciones para conversión de texto a bytes, normalización y procesamiento de batches.
"""

import logging
from typing import List, Tuple, Dict, Optional, Generator, Union
import jax  # type: ignore
import jax.numpy as jnp  # type: ignore
import numpy as np  # type: ignore
import zlib
import hashlib
from concurrent.futures import ThreadPoolExecutor
import codecs
from pathlib import Path
from utils import (
    handle_error,
    DataProcessingError,
    process_batch as base_process_batch
)

# Configuración del logger
logger = logging.getLogger(__name__)

def validate_input_data(data: Union[List[int], jnp.ndarray], max_value: int = 255) -> None:
    """
    Valida que los datos de entrada sean bytes válidos.
    
    Args:
        data: Lista o array de bytes a validar
        max_value: Valor máximo permitido (default: 255)
        
    Raises:
        DataProcessingError: Si los datos no son válidos
    """
    if isinstance(data, jnp.ndarray):
        data = data.tolist()
    if not all(0 <= x <= max_value for x in data):
        raise DataProcessingError("Datos de entrada contienen valores fuera del rango permitido")

def normalize_text(text: str) -> str:
    """
    Normaliza texto convirtiendo a minúsculas y eliminando espacios extra.
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto normalizado
        
    Raises:
        DataProcessingError: Si hay error en la normalización
    """
    try:
        if not text.strip():
            logger.warning("Texto vacío proporcionado")
            return ""
        return " ".join(text.lower().split())
    except Exception as e:
        logger.error(f"Error normalizando texto: {e}")
        raise DataProcessingError(f"Error en normalización: {e}")

def text_to_bytes(
    text: str,
    encoding: str = 'utf-8',
    errors: str = 'strict',
    max_length: Optional[int] = None,
    normalize: bool = True
) -> jnp.ndarray:
    """
    Convierte texto a array de bytes usando JAX.
    
    Args:
        text: Texto de entrada a convertir
        encoding: Codificación a usar (default: utf-8)
        errors: Manejo de errores de codificación (default: strict)
        max_length: Longitud máxima del array (default: None)
        normalize: Si se debe normalizar el texto (default: True)
        
    Returns:
        Array JAX de bytes
        
    Raises:
        DataProcessingError: Si hay error en la conversión
    """
    try:
        if normalize:
            text = normalize_text(text)
        if not text.strip():
            logger.warning("Texto vacío proporcionado")
            return jnp.array([], dtype=jnp.uint8)
            
        byte_list = list(text.encode(encoding, errors=errors))
        if max_length is not None:
            byte_list = byte_list[:max_length]
            
        return jnp.array(byte_list, dtype=jnp.uint8)
    except Exception as e:
        logger.error(f"Error convirtiendo texto a bytes: {e}")
        raise DataProcessingError(f"Error de codificación: {e}")

def bytes_to_text(
    bytes_data: Union[List[int], jnp.ndarray],
    encoding: str = 'utf-8',
    errors: str = 'replace'
) -> str:
    """
    Convierte array de bytes a texto.
    
    Args:
        bytes_data: Array o lista de bytes a convertir
        encoding: Codificación a usar (default: utf-8)
        errors: Manejo de errores de decodificación (default: replace)
        
    Returns:
        Texto decodificado
        
    Raises:
        DataProcessingError: Si hay error en la decodificación
    """
    try:
        if isinstance(bytes_data, jnp.ndarray):
            bytes_data = bytes_data.tolist()
        validate_input_data(bytes_data)
        return bytes(bytes_data).decode(encoding, errors=errors)
    except Exception as e:
        logger.error(f"Error convirtiendo bytes a texto: {e}")
        raise DataProcessingError(f"Error de decodificación: {e}")

def bytes_to_binary_labels(
    bytes_data: Union[List[int], jnp.ndarray],
    threshold: int = 127
) -> jnp.ndarray:
    """
    Convierte bytes a etiquetas binarias (0 o 1) usando JAX.
    
    Args:
        bytes_data: Array o lista de bytes a convertir
        threshold: Umbral para la conversión (default: 127)
        
    Returns:
        Array JAX de etiquetas binarias
        
    Raises:
        DataProcessingError: Si los datos no son válidos
    """
    try:
        if isinstance(bytes_data, jnp.ndarray):
            bytes_data = bytes_data.tolist()
        validate_input_data(bytes_data)
        return jnp.array([1 if b > threshold else 0 for b in bytes_data], dtype=jnp.uint8)
    except Exception as e:
        logger.error(f"Error en conversión a etiquetas binarias: {e}")
        raise

def prepare_training_data(
    input_bytes: Union[List[int], jnp.ndarray],
    target_bytes: Union[List[int], jnp.ndarray],
    max_length: int,
    padding_value: int = 0
) -> Tuple[jnp.ndarray, jnp.ndarray]:
    """
    Prepara datos de entrenamiento para modo binario usando JAX.
    
    Args:
        input_bytes: Bytes de entrada
        target_bytes: Bytes objetivo
        max_length: Longitud máxima de secuencia
        padding_value: Valor para padding (default: 0)
        
    Returns:
        Tupla con arrays JAX preparados (input, target)
        
    Raises:
        DataProcessingError: Si los datos no son válidos
    """
    try:
        if isinstance(input_bytes, jnp.ndarray):
            input_bytes = input_bytes.tolist()
        if isinstance(target_bytes, jnp.ndarray):
            target_bytes = target_bytes.tolist()
            
        validate_input_data(input_bytes)
        validate_input_data(target_bytes)
        
        # Asegurar longitud máxima
        input_bytes = input_bytes[:max_length]
        target_bytes = target_bytes[:max_length]
        
        # Padding si es necesario
        if len(input_bytes) < max_length:
            input_bytes.extend([padding_value] * (max_length - len(input_bytes)))
        if len(target_bytes) < max_length:
            target_bytes.extend([padding_value] * (max_length - len(target_bytes)))
            
        # Convertir a etiquetas binarias
        input_labels = bytes_to_binary_labels(input_bytes)
        target_labels = bytes_to_binary_labels(target_bytes)
        
        return input_labels, target_labels
        
    except Exception as e:
        logger.error(f"Error preparando datos de entrenamiento: {e}")
        raise

def stream_training_data(
    file_path: str,
    batch_size: int = 512,
    max_workers: int = 4
) -> Generator[Tuple[jnp.ndarray, jnp.ndarray], None, None]:
    """
    Stream de datos de entrenamiento desde archivo usando JAX.
    
    Args:
        file_path: Ruta al archivo de datos
        batch_size: Tamaño del batch (default: 512)
        max_workers: Número máximo de workers para procesamiento paralelo
        
    Yields:
        Tuplas de arrays JAX preparados (input, target)
        
    Raises:
        DataProcessingError: Si hay error en el procesamiento
    """
    try:
        with open(file_path, 'rb') as file:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                while True:
                    # Leer bloques de bytes
                    input_bytes = list(file.read(batch_size))
                    if not input_bytes:
                        break
                        
                    # Generar target como siguiente byte
                    target_bytes = input_bytes[1:] + [0]
                    
                    # Preparar datos en paralelo
                    future = executor.submit(
                        prepare_training_data,
                        input_bytes,
                        target_bytes,
                        max_length=batch_size
                    )
                    
                    yield future.result()
                    
    except Exception as e:
        logger.error(f"Error en stream de datos de entrenamiento: {e}")
        raise DataProcessingError(f"Error en stream de datos: {e}")

def save_preprocessed_data(
    preprocessed_data: List[Tuple[jnp.ndarray, jnp.ndarray]],
    file_path: str,
    compress: bool = True
) -> None:
    """
    Guarda datos preprocesados en formato binario.
    
    Args:
        preprocessed_data: Lista de tuplas (input, target)
        file_path: Ruta donde guardar los datos
        compress: Si se debe comprimir los datos (default: True)
        
    Raises:
        DataProcessingError: Si hay error al guardar
    """
    try:
        with open(file_path, 'wb') as file:
            for input_data, target_data in preprocessed_data:
                # Convertir a lista para validación
                input_list = input_data.tolist()
                target_list = target_data.tolist()
                
                # Validar datos
                validate_input_data(input_list)
                validate_input_data(target_list)
                
                # Convertir a bytes
                input_bytes = bytes(input_list)
                target_bytes = bytes(target_list)
                
                # Comprimir si se solicita
                if compress:
                    input_bytes = zlib.compress(input_bytes)
                    target_bytes = zlib.compress(target_bytes)
                
                # Guardar con longitud y checksum
                file.write(len(input_bytes).to_bytes(4, 'big'))
                file.write(hashlib.sha256(input_bytes).digest())
                file.write(input_bytes)
                file.write(len(target_bytes).to_bytes(4, 'big'))
                file.write(hashlib.sha256(target_bytes).digest())
                file.write(target_bytes)
                
    except Exception as e:
        logger.error(f"Error guardando datos preprocesados: {e}")
        raise DataProcessingError(f"Error al guardar datos: {e}")

@handle_error(DataProcessingError)
def process_batch(
    batch: Dict[str, Union[List[int], jnp.ndarray]],
    dtype: jnp.dtype = jnp.float32
) -> Dict[str, jnp.ndarray]:
    """
    Procesa un batch de datos convirtiendo a arrays JAX.
    
    Args:
        batch: Diccionario con input_ids, context_ids, target_ids y attention_mask
        dtype: Tipo de datos para los arrays (default: float32)
        
    Returns:
        Diccionario con los datos convertidos a arrays JAX
    """
    # Usar la función base para procesar el batch
    processed = base_process_batch(
        batch,
        tokenizer=None,  # No necesitamos tokenizer aquí
        max_length=0,    # No necesitamos max_length aquí
        padding=False,   # No necesitamos padding aquí
        truncation=False # No necesitamos truncation aquí
    )
    
    # Convertir a JAX con el dtype especificado
    return {
        'inputs': jnp.array(processed['input_ids'], dtype=dtype),
        'context': jnp.array(batch['context_ids'], dtype=dtype),
        'targets': jnp.array(batch['target_ids'], dtype=dtype),
        'attention_mask': jnp.array(processed['attention_mask'], dtype=dtype)
    } 