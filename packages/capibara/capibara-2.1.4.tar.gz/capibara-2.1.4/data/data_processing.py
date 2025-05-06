"""
data_processing.py

Este módulo proporciona funciones para el preprocesamiento de datos de entrenamiento para CapibaraModel.
Incluye funciones para conversión de texto a bytes y otras tareas de procesamiento de datos.
"""

import logging
from typing import List, Tuple, Dict, Optional, Generator
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

def validate_input_data(data: List[int], max_value: int = 255) -> None:
    """
    Valida que los datos de entrada sean bytes válidos.
    
    Args:
        data: Lista de bytes a validar
        max_value: Valor máximo permitido (default: 255)
        
    Raises:
        DataProcessingError: Si los datos no son válidos
    """
    if not all(0 <= x <= max_value for x in data):
        raise DataProcessingError("Datos de entrada contienen valores fuera del rango permitido")

def text_to_bytes(
    text: str,
    encoding: str = 'utf-8',
    errors: str = 'strict'
) -> List[int]:
    """
    Convierte texto a lista de bytes usando la codificación especificada.
    
    Args:
        text: Texto de entrada a convertir
        encoding: Codificación a usar (default: utf-8)
        errors: Manejo de errores de codificación (default: strict)
        
    Returns:
        Lista de bytes representando el texto
        
    Raises:
        DataProcessingError: Si hay error en la conversión
    """
    try:
        return list(text.encode(encoding, errors=errors))
    except UnicodeEncodeError as e:
        logger.error(f"Error convirtiendo texto a bytes: {e}")
        raise DataProcessingError(f"Error de codificación: {e}")

def bytes_to_text(
    bytes_list: List[int],
    encoding: str = 'utf-8',
    errors: str = 'replace'
) -> str:
    """
    Convierte lista de bytes a texto usando la codificación especificada.
    
    Args:
        bytes_list: Lista de bytes a convertir
        encoding: Codificación a usar (default: utf-8)
        errors: Manejo de errores de decodificación (default: replace)
        
    Returns:
        Texto decodificado
        
    Raises:
        DataProcessingError: Si hay error en la decodificación
    """
    try:
        validate_input_data(bytes_list)
        return bytes(bytes_list).decode(encoding, errors=errors)
    except UnicodeDecodeError as e:
        logger.error(f"Error convirtiendo bytes a texto: {e}")
        raise DataProcessingError(f"Error de decodificación: {e}")

def bytes_to_binary_labels(
    bytes_data: List[int],
    threshold: int = 127
) -> List[int]:
    """
    Convierte bytes a etiquetas binarias (0 o 1).
    
    Args:
        bytes_data: Lista de bytes a convertir
        threshold: Umbral para la conversión (default: 127)
        
    Returns:
        Lista de etiquetas binarias
        
    Raises:
        DataProcessingError: Si los datos no son válidos
    """
    try:
        validate_input_data(bytes_data)
        return [1 if b > threshold else 0 for b in bytes_data]
    except DataProcessingError as e:
        logger.error(f"Error en conversión a etiquetas binarias: {e}")
        raise

def prepare_training_data(
    input_bytes: List[int],
    target_bytes: List[int],
    max_length: int,
    padding_value: int = 0
) -> Tuple[List[int], List[int]]:
    """
    Prepara datos de entrenamiento para modo binario.
    
    Args:
        input_bytes: Bytes de entrada
        target_bytes: Bytes objetivo
        max_length: Longitud máxima de secuencia
        padding_value: Valor para padding (default: 0)
        
    Returns:
        Tupla con datos preparados (input, target)
        
    Raises:
        DataProcessingError: Si los datos no son válidos
    """
    try:
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
        
    except DataProcessingError as e:
        logger.error(f"Error preparando datos de entrenamiento: {e}")
        raise

def stream_training_data(
    file_path: str,
    batch_size: int = 512,
    max_workers: int = 4
) -> Generator[Tuple[List[int], List[int]], None, None]:
    """
    Stream de datos de entrenamiento desde archivo.
    
    Args:
        file_path: Ruta al archivo de datos
        batch_size: Tamaño del batch (default: 512)
        max_workers: Número máximo de workers para procesamiento paralelo
        
    Yields:
        Tuplas de datos preparados (input, target)
        
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
    preprocessed_data: List[Tuple[List[int], List[int]]],
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
                # Validar datos
                validate_input_data(input_data)
                validate_input_data(target_data)
                
                # Convertir a bytes
                input_bytes = bytes(input_data)
                target_bytes = bytes(target_data)
                
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
    batch: Dict,
    dtype: np.dtype = np.float32
) -> Dict:
    """
    Procesa un batch de datos convirtiendo listas a arrays numpy.
    
    Args:
        batch: Diccionario con input_ids, context_ids, target_ids y attention_mask
        dtype: Tipo de datos para los arrays (default: float32)
        
    Returns:
        Diccionario con los datos convertidos a arrays numpy
    """
    # Usar la función base para procesar el batch
    processed = base_process_batch(
        batch,
        tokenizer=None,  # No necesitamos tokenizer aquí
        max_length=0,    # No necesitamos max_length aquí
        padding=False,   # No necesitamos padding aquí
        truncation=False # No necesitamos truncation aquí
    )
    
    # Convertir a numpy con el dtype especificado
    return {
        'inputs': np.array(processed['input_ids'], dtype=dtype),
        'context': np.array(batch['context_ids'], dtype=dtype),
        'targets': np.array(batch['target_ids'], dtype=dtype),
        'attention_mask': np.array(processed['attention_mask'], dtype=dtype)
    } 