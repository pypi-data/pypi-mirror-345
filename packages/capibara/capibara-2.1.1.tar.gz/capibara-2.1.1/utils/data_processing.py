"""
Módulo para procesamiento de datos.
"""

import numpy as np  # type: ignore
import jax.numpy as jnp  # type: ignore
from typing import Dict, Any, Union, List, Tuple
from .error_handling import DataProcessingError, handle_error

@handle_error(DataProcessingError)
def process_batch(
    batch: Union[List[str], Dict[str, Any]],
    tokenizer: Any = None,
    max_length: int = 512,
    padding: str = 'max_length',
    truncation: bool = True
) -> Dict[str, jnp.ndarray]:
    """
    Procesa un lote de datos para entrenamiento o inferencia.
    
    Args:
        batch: Lote de datos a procesar
        tokenizer: Tokenizador preentrenado
        max_length: Longitud máxima de secuencia
        padding: Estrategia de padding
        truncation: Si se debe truncar
        
    Returns:
        Dict con tensores procesados
    """
    if tokenizer is not None:
        # Tokenizar
        inputs = tokenizer(
            batch,
            max_length=max_length,
            padding=padding,
            truncation=truncation,
            return_tensors='np'
        )
        
        # Convertir a JAX
        return {
            'input_ids': jnp.array(inputs['input_ids'], dtype=jnp.int32),
            'attention_mask': jnp.array(inputs['attention_mask'], dtype=jnp.int32)
        }
    else:
        # Procesar directamente
        if isinstance(batch, dict):
            return {
                'input_ids': jnp.array(batch['input_ids'], dtype=jnp.int32),
                'attention_mask': jnp.array(batch['attention_mask'], dtype=jnp.int32)
            }
        else:
            raise DataProcessingError("Se requiere tokenizer o diccionario de datos")

@handle_error(DataProcessingError)
def save_processed_data(
    data: Union[np.ndarray, jnp.ndarray],
    output_path: str,
    format: str = 'numpy'
) -> None:
    """
    Guarda datos procesados.
    
    Args:
        data: Datos a guardar
        output_path: Ruta de salida
        format: Formato de salida (numpy o jax)
    """
    if format == 'numpy':
        np.save(output_path, np.array(data))
    elif format == 'jax':
        jnp.save(output_path, jnp.array(data))
    else:
        raise DataProcessingError(f"Formato no soportado: {format}")

@handle_error(DataProcessingError)
def load_processed_data(
    input_path: str,
    format: str = 'numpy'
) -> Union[np.ndarray, jnp.ndarray]:
    """
    Carga datos procesados.
    
    Args:
        input_path: Ruta de entrada
        format: Formato de entrada (numpy o jax)
        
    Returns:
        Datos cargados
    """
    if format == 'numpy':
        return np.load(input_path)
    elif format == 'jax':
        return jnp.load(input_path)
    else:
        raise DataProcessingError(f"Formato no soportado: {format}")

@handle_error(DataProcessingError)
def text_to_bytes(text: str) -> List[int]:
    """
    Convierte texto a bytes.
    
    Args:
        text: Texto a convertir
        
    Returns:
        Lista de bytes
    """
    return [ord(c) for c in text]

@handle_error(DataProcessingError)
def bytes_to_text(bytes_data: List[int]) -> str:
    """
    Convierte bytes a texto.
    
    Args:
        bytes_data: Lista de bytes
        
    Returns:
        Texto convertido
    """
    return ''.join(chr(b) for b in bytes_data)

@handle_error(DataProcessingError)
def prepare_training_data(texts: List[str]) -> List[Tuple[List[int], List[int]]]:
    """
    Prepara datos para entrenamiento.
    
    Args:
        texts: Lista de textos
        
    Returns:
        Lista de tuplas (input_bytes, target_bytes)
    """
    training_data = []
    for text in texts:
        bytes_data = text_to_bytes(text)
        input_bytes = bytes_data[:-1]
        target_bytes = bytes_data[1:]
        training_data.append((input_bytes, target_bytes))
    return training_data