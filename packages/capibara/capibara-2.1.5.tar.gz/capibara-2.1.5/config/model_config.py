"""
Configuración del modelo CapibaraModel.

Este módulo define la configuración específica de la arquitectura del modelo,
incluyendo parámetros de capas, atención y otros componentes.
"""

import logging
import yaml  # type: ignore
from pydantic import BaseModel, Field, validator  # type: ignore
from typing import Optional, List, Dict, Any
from .tpu_config import TPUConfig
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ModelConfig(BaseModel):
    """Configuración de la arquitectura del modelo."""
    
    # Configuración básica
    model_name: str = Field("capibara", description="Nombre del modelo")
    model_type: str = Field("transformer", description="Tipo de arquitectura")
    hidden_size: int = Field(768, description="Tamaño de la capa oculta")
    num_layers: int = Field(12, description="Número de capas")
    num_heads: int = Field(12, description="Número de cabezas de atención")
    
    # Configuración de atención
    attention_dropout: float = Field(0.1, description="Dropout de atención")
    attention_scale: bool = Field(True, description="Escalar la atención")
    use_rotary_embeddings: bool = Field(True, description="Usar embeddings rotatorios")
    
    # Configuración de feed-forward
    intermediate_size: int = Field(3072, description="Tamaño de la capa intermedia")
    activation_function: str = Field("gelu", description="Función de activación")
    dropout: float = Field(0.1, description="Dropout general")
    
    # Configuración de embeddings
    vocab_size: int = Field(50257, description="Tamaño del vocabulario")
    max_position_embeddings: int = Field(2048, description="Máxima longitud de secuencia")
    type_vocab_size: int = Field(2, description="Tamaño del vocabulario de tipos")
    
    # Configuración de normalización
    layer_norm_eps: float = Field(1e-12, description="Épsilon para LayerNorm")
    use_layer_norm: bool = Field(True, description="Usar LayerNorm")
    
    # Configuración de inicialización
    initializer_range: float = Field(0.02, description="Rango del inicializador")
    use_xavier_init: bool = Field(True, description="Usar inicialización Xavier")
    
    # Configuración de cuantización
    use_quantization: bool = Field(False, description="Usar cuantización")
    num_bits: int = Field(8, description="Número de bits para cuantización")
    quant_min: float = Field(0.0, description="Valor mínimo de cuantización")
    quant_max: float = Field(255.0, description="Valor máximo de cuantización")
    
    # Configuración avanzada
    custom_layers: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Capas personalizadas"
    )
    
    @validator('hidden_size')
    def validate_hidden_size(cls, v):
        """Valida que el tamaño oculto sea divisible por el número de cabezas."""
        if v % 12 != 0:
            raise ValueError("El tamaño oculto debe ser divisible por 12")
        return v
    
    @validator('num_bits')
    def validate_num_bits(cls, v):
        """Valida que el número de bits sea válido."""
        if v not in [1, 2, 4, 8, 16]:
            raise ValueError("El número de bits debe ser 1, 2, 4, 8 o 16")
        return v
    
    class Config:
        """Configuración de Pydantic."""
        validate_assignment = True
        extra = "forbid"

class CapibaraConfig(BaseModel):
    """
    Configuración principal del modelo CapibaraModel.
    """

    base_model_name: str
    tokenizer_name: str
    max_length: int = 512
    batch_size: int = 128  # Tamaño de batch recomendado para TPUs
    learning_rate: float = 1e-3
    num_epochs: int = 5
    output_dir: str = 'gs://capibara_gpt/output'
    device: str = 'tpu'
    tpu_config: TPUConfig
    log_level: str = 'INFO'

    @validator('device')
    def validate_device(cls, v):
        """Valida que el dispositivo esté configurado como 'tpu'."""
        if v != 'tpu':
            raise ValueError("`device` debe configurarse como 'tpu' para entrenamiento exclusivo en TPU.")
        return v

    @classmethod
    def from_yaml(cls, yaml_path: str, tpu_yaml_path: str) -> 'CapibaraConfig':
        """
        Carga la configuración del modelo desde archivos YAML.

        Args:
            yaml_path: Ruta al archivo de configuración principal.
            tpu_yaml_path: Ruta al archivo de configuración de TPU.

        Returns:
            CapibaraConfig: Instancia de configuración del modelo.

        Raises:
            FileNotFoundError: Si algún archivo YAML no existe.
            yaml.YAMLError: Si hay error al parsear algún archivo YAML.
        """
        try:
            with open(yaml_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            tpu_config = TPUConfig.from_yaml(tpu_yaml_path)
            config_dict['tpu_config'] = tpu_config
            return cls(**config_dict)
        except FileNotFoundError:
            logger.error(f"Archivo de configuración no encontrado: {yaml_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error cargando configuración desde {yaml_path}: {e}")
            raise

@dataclass
class BitNetConfig:
    """Configuración para BitNet158."""
    hidden_size: int = 2048
    intermediate_size: int = 8192
    num_attention_heads: int = 32
    num_hidden_layers: int = 24
    max_position_embeddings: int = 2048
    initializer_range: float = 0.02
    layer_norm_eps: float = 1e-5
    hidden_dropout_prob: float = 0.1
    attention_probs_dropout_prob: float = 0.1
    use_cache: bool = True
    gradient_checkpointing: bool = False
    remat_frequency: int = 2  # Cada cuántas capas aplicar remat

@dataclass
class NeuroAdaptiveConfig:
    """Configuración para NeuroAdaptiveStack."""
    num_layers: int = 24
    hidden_size: int = 2048
    intermediate_size: int = 8192
    num_attention_heads: int = 32
    dropout_rate: float = 0.1
    remat_frequency: int = 2
    use_gradient_checkpointing: bool = True
    layer_id: Optional[int] = None

