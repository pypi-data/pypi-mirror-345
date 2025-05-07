"""
Validadores extendidos para la configuración de CapibaraModel
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import validator, ValidationError #type: ignore
import torch 
import jax 
import logging
from pathlib import Path
import os
import shutil
import psutil #type: ignore
import numpy as np #type: ignore
from jax.experimental import mesh_utils 
from .config_types import CapibaraConfig

logger = logging.getLogger(__name__)

def validate_hardware_compatibility(config: Dict[str, Any]) -> List[str]:
    """Valida la compatibilidad del hardware con la configuración."""
    warnings = []
    
    try:
        # Validar memoria disponible
        if torch.cuda.is_available():
            gpu_mem = torch.cuda.get_device_properties(0).total_memory
            model_mem = estimate_model_memory(config)
            if model_mem > gpu_mem * 0.9:  # 90% del límite
                warnings.append(
                    f"La configuración requiere {model_mem/1e9:.2f}GB pero solo hay {gpu_mem/1e9:.2f}GB disponibles"
                )
            
            # Validar versión de CUDA
            cuda_version = torch.version.cuda
            if cuda_version < "11.0":
                warnings.append(f"Versión de CUDA ({cuda_version}) puede ser demasiado antigua")
    except Exception as e:
        logger.error(f"Error validando GPU: {str(e)}")
        warnings.append(f"No se pudo validar memoria GPU: {str(e)}")

    try:
        # Validar memoria CPU
        cpu_mem = psutil.virtual_memory().total
        if model_mem > cpu_mem * 0.8:  # 80% del límite
            warnings.append(
                f"La configuración requiere {model_mem/1e9:.2f}GB de RAM pero solo hay {cpu_mem/1e9:.2f}GB disponibles"
            )
        
        # Validar núcleos CPU
        cpu_cores = psutil.cpu_count(logical=False)
        if cpu_cores < 4:
            warnings.append(f"Pocos núcleos CPU ({cpu_cores}) pueden limitar el rendimiento")
    except Exception as e:
        logger.error(f"Error validando CPU: {str(e)}")
        warnings.append(f"No se pudo validar memoria CPU: {str(e)}")

    # Validar TPU si está habilitado
    if config.get('use_tpu', False):
        try:
            tpu_devices = jax.devices('tpu')
            if not tpu_devices:
                warnings.append("TPU configurado pero no detectado en el sistema")
            else:
                # Validar sharding para TPU
                num_devices = len(tpu_devices)
                if config.get('model', {}).get('sharding', {}).get('enabled', False):
                    shard_size = config['model']['sharding']['size']
                    if shard_size > num_devices:
                        warnings.append(f"Sharding size ({shard_size}) excede número de TPUs disponibles ({num_devices})")
                    
                    # Validar topología de TPU
                    try:
                        topology = mesh_utils.create_device_mesh((num_devices,))
                        logger.info(f"Topología TPU detectada: {topology}")
                    except Exception as e:
                        warnings.append(f"Error validando topología TPU: {str(e)}")
        except Exception as e:
            logger.error(f"Error validando TPU: {str(e)}")
            warnings.append(f"Error validando TPU: {str(e)}")
    
    return warnings

def validate_training_compatibility(config: Dict[str, Any]) -> List[str]:
    """Valida la compatibilidad de los parámetros de entrenamiento."""
    warnings = []
    
    try:
        # Validar batch size
        batch_size = config['training']['batch_size']
        seq_length = config['model']['max_seq_length']
        if batch_size * seq_length > 1e6:
            warnings.append("Batch size × sequence length puede causar problemas de memoria")
        
        # Validar learning rate
        lr = config['training']['learning_rate']
        if lr > 1e-3:
            warnings.append("Learning rate puede ser demasiado alto para entrenamiento estable")
        elif lr < 1e-6:
            warnings.append("Learning rate puede ser demasiado bajo para convergencia")
        
        # Validar progressive training
        if config['progressive_training']['enabled']:
            if not config['training']['phase_ordering']:
                warnings.append("Progressive training habilitado pero phase_ordering está vacío")
            else:
                # Validar orden de fases
                phases = config['training']['phase_ordering']
                if not all(isinstance(p, dict) and 'name' in p for p in phases):
                    warnings.append("Formato inválido en phase_ordering")
        
        # Validar optimizaciones
        if config.get('optimization', {}).get('quantization', {}).get('enabled', False):
            if config['training']['mixed_precision']:
                warnings.append("Quantization y mixed precision pueden causar conflictos")
            if config.get('optimization', {}).get('gradient_checkpointing', False):
                warnings.append("Quantization y gradient checkpointing pueden reducir rendimiento")
            
            # Validar configuración de quantización
            bit_width = config.get('optimization', {}).get('quantization', {}).get('bit_width', 8)
            if bit_width not in [4, 8, 16]:
                warnings.append(f"Bit width inválido para quantización: {bit_width}")
    except Exception as e:
        logger.error(f"Error validando entrenamiento: {str(e)}")
        warnings.append(f"Error en validación de entrenamiento: {str(e)}")
    
    return warnings

def validate_component_dependencies(config: Dict[str, Any]) -> List[str]:
    """Valida las dependencias entre componentes."""
    warnings = []
    components = config['model']['components']
    
    try:
        # Validar dependencias de atención
        if components.get('self_attention', {}).get('enabled', False):
            if not components.get('embeddings', {}).get('enabled', False):
                warnings.append("Self-attention requiere que embeddings esté habilitado")
            
            # Validar configuración de atención
            num_heads = config['model']['num_heads']
            hidden_size = config['model']['hidden_size']
            if hidden_size % num_heads != 0:
                warnings.append(f"hidden_size ({hidden_size}) debe ser divisible por num_heads ({num_heads})")
        
        # Validar dependencias de quantization
        if config.get('optimization', {}).get('quantization', {}).get('enabled', False):
            if config['training']['mixed_precision']:
                warnings.append("Quantization y mixed precision pueden causar conflictos")
            if not components.get('normalization', {}).get('enabled', False):
                warnings.append("Quantization requiere normalización para estabilidad")
            
            # Validar configuración de quantización
            if config.get('optimization', {}).get('quantization', {}).get('symmetric', True):
                if not components.get('normalization', {}).get('enabled', False):
                    warnings.append("Quantización simétrica requiere normalización")
        
        # Validar dependencias de TPU
        if config.get('use_tpu', False):
            if not config.get('optimization', {}).get('sharding', {}).get('enabled', False):
                warnings.append("TPU requiere sharding para máximo rendimiento")
            
            # Validar configuración de sharding
            if config.get('optimization', {}).get('sharding', {}).get('enabled', False):
                shard_size = config['optimization']['sharding']['size']
                if shard_size < 2:
                    warnings.append("Sharding size debe ser al menos 2 para TPU")
    except Exception as e:
        logger.error(f"Error validando componentes: {str(e)}")
        warnings.append(f"Error en validación de componentes: {str(e)}")
    
    return warnings

def validate_paths_and_permissions(config: Dict[str, Any]) -> List[str]:
    """Valida rutas y permisos de archivos."""
    warnings = []
    
    try:
        for key, path in config['paths'].items():
            path_obj = Path(path)
            
            # Verificar existencia y permisos
            if not path_obj.exists():
                try:
                    path_obj.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Directorio creado: {path}")
                except Exception as e:
                    logger.error(f"Error creando directorio {path}: {str(e)}")
                    warnings.append(f"No se puede crear {key} en {path}: {str(e)}")
            else:
                if not os.access(path, os.W_OK):
                    warnings.append(f"No hay permisos de escritura en {path}")
                if not os.access(path, os.R_OK):
                    warnings.append(f"No hay permisos de lectura en {path}")
                
                # Verificar espacio disponible
                try:
                    free_space = shutil.disk_usage(path).free
                    if free_space < 1e9:  # Menos de 1GB
                        warnings.append(f"Poco espacio disponible en {path}: {free_space/1e9:.2f}GB")
                except Exception:
                    pass  # Ignorar errores de espacio en disco
    except Exception as e:
        logger.error(f"Error validando rutas: {str(e)}")
        warnings.append(f"Error en validación de rutas: {str(e)}")
    
    return warnings

def estimate_model_memory(config: Dict[str, Any]) -> int:
    """Estima el uso de memoria del modelo en bytes."""
    try:
        hidden_size = config['model']['hidden_size']
        num_layers = config['model']['num_layers']
        vocab_size = config['model']['vocab_size']
        seq_length = config['model']['max_seq_length']
        batch_size = config['training']['batch_size']
        
        # Factor de precisión basado en configuración
        precision_factor = 4  # float32 por defecto
        if config.get('optimization', {}).get('quantization', {}).get('enabled', False):
            precision_factor = 2  # bfloat16
        elif config['training']['mixed_precision']:
            precision_factor = 2  # mixed precision
        
        # Estimación de parámetros principales
        embedding_params = vocab_size * hidden_size * precision_factor
        attention_params = num_layers * (hidden_size * hidden_size * precision_factor) * 4  # 4 matrices por capa
        ffn_params = num_layers * (hidden_size * hidden_size * precision_factor) * 2  # 2 matrices por capa
        
        # Estimación de activaciones durante forward pass
        activations = batch_size * seq_length * hidden_size * precision_factor * num_layers
        
        # Overhead para gradientes durante entrenamiento
        training_overhead = (embedding_params + attention_params + ffn_params) * 2
        
        # Memoria adicional para optimizaciones
        optimization_overhead = 0
        if config.get('optimization', {}).get('gradient_checkpointing', False):
            optimization_overhead += activations * 0.5  # Reducción de memoria por checkpointing
        if config.get('optimization', {}).get('sharding', {}).get('enabled', False):
            optimization_overhead += (embedding_params + attention_params + ffn_params) * 0.1  # Overhead de sharding
        
        total_memory = embedding_params + attention_params + ffn_params + activations + training_overhead + optimization_overhead
        return int(total_memory)
    except Exception as e:
        logger.error(f"Error estimando memoria: {str(e)}")
        raise

def validate_full_config(config: Dict[str, Any]) -> List[str]:
    """Realiza una validación completa de la configuración."""
    all_warnings = []
    
    try:
        # Validar hardware
        all_warnings.extend(validate_hardware_compatibility(config))
        
        # Validar parámetros de entrenamiento
        all_warnings.extend(validate_training_compatibility(config))
        
        # Validar dependencias de componentes
        all_warnings.extend(validate_component_dependencies(config))
        
        # Validar rutas y permisos
        all_warnings.extend(validate_paths_and_permissions(config))
        
        # Validar usando Pydantic
        try:
            CapibaraConfig(**config)
        except ValidationError as e:
            all_warnings.extend(str(err) for err in e.errors())
    except Exception as e:
        logger.error(f"Error en validación completa: {str(e)}")
        all_warnings.append(f"Error en validación completa: {str(e)}")
    
    return all_warnings 