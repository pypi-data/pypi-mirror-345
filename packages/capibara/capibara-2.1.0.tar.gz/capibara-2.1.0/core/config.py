"""
Configuration management for CapibaraModel - Versión 2.0
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging
from pydantic import BaseModel, Field, validator, ValidationError # type: ignore 
from omegaconf import OmegaConf # type: ignore
import yaml # type: ignore
from dotenv import load_dotenv # type: ignore
from .config import validate_full_config, ValidationError #type: ignore
import jax.numpy as jnp # type: ignore

logger = logging.getLogger(__name__)
load_dotenv()

# --------------------------------------------------
# Model Component Configuration
# --------------------------------------------------
class TPUConfig(BaseModel):
    enabled: bool = Field(default=False, description="Habilitar soporte TPU")
    device: str = Field(default="", description="Dispositivo TPU a utilizar")
    mesh_shape: List[int] = Field(default=[1, 1], description="Forma de la malla TPU")
    dtype: str = Field(default="float32", description="Tipo de datos para TPU")

class MonitoringConfig(BaseModel):
    enabled: bool = Field(default=True, description="Habilitar monitoreo")
    metrics: List[str] = Field(default=["loss", "accuracy"], description="Métricas a monitorear")
    log_frequency: int = Field(default=100, description="Frecuencia de logging")

class ComponentConfig(BaseModel):
    name: str = Field(..., description="Nombre del componente")
    enabled: bool = Field(default=True, description="Componente habilitado")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuración específica")

class QuantizationConfig(BaseModel):
    enabled: bool = Field(default=False, description="Habilitar cuantización")
    bits: int = Field(default=8, description="Bits para cuantización")
    symmetric: bool = Field(default=True, description="Cuantización simétrica")

class ProgressiveTrainingConfig(BaseModel):
    enabled: bool = Field(default=False, description="Habilitar entrenamiento progresivo")
    stages: List[Dict[str, Any]] = Field(default_factory=list, description="Etapas de entrenamiento")
    transition_epochs: int = Field(default=5, description="Épocas de transición")

# --------------------------------------------------
# Main Configuration Sections
# --------------------------------------------------
class ModelConfig(BaseModel):
    """Configuración base del modelo."""
    
    # Dimensiones del modelo
    hidden_size: int = Field(default=2048, description="Tamaño de la capa oculta")
    num_heads: int = Field(default=32, description="Número de cabezas de atención")
    num_layers: int = Field(default=24, description="Número de capas transformer")
    
    # Vocabulario y secuencias
    vocab_size: int = Field(default=32000, description="Tamaño del vocabulario")
    max_length: int = Field(default=2048, description="Longitud máxima de secuencia")
    
    # Hiperparámetros de entrenamiento
    dropout_rate: float = Field(default=0.1, description="Tasa de dropout")
    learning_rate: float = Field(default=1e-4, description="Tasa de aprendizaje")
    warmup_steps: int = Field(default=1000, description="Pasos de warmup")
    
    # Configuración de TPU
    use_tpu: bool = Field(default=False, description="Usar TPU")
    tpu_dtype: str = Field(default="float32", description="Tipo de datos para TPU")
    
    # Monitoreo y métricas
    monitor_metrics: bool = Field(default=False, description="Habilitar monitoreo de métricas")
    log_every: int = Field(default=100, description="Frecuencia de logging")
    
    # Configuración de distribución
    batch_size: int = Field(default=32, description="Tamaño de batch")
    gradient_accumulation_steps: int = Field(default=1, description="Pasos de acumulación de gradientes")
    
    # Configuración de optimización
    optimizer: str = Field(default="adam", description="Optimizador a usar")
    weight_decay: float = Field(default=0.01, description="Decaimiento de pesos")
    
    # Configuración de tareas
    task_type: str = Field(default="text", description="Tipo de tarea (text/bin)")
    target_type: str = Field(default="next_token", description="Tipo de target")
    
    @validator('tpu_dtype')
    def validate_tpu_dtype(cls, v):
        """Validar tipo de datos TPU."""
        valid_dtypes = ['float32', 'bfloat16', 'float16']
        if v not in valid_dtypes:
            raise ValueError(f"tpu_dtype debe ser uno de {valid_dtypes}")
        return v
    
    @validator('task_type')
    def validate_task_type(cls, v):
        """Validar tipo de tarea."""
        valid_tasks = ['text', 'bin']
        if v not in valid_tasks:
            raise ValueError(f"task_type debe ser uno de {valid_tasks}")
        return v
    
    @validator('target_type')
    def validate_target_type(cls, v):
        """Validar tipo de target."""
        valid_targets = ['next_token', 'binary', 'byte']
        if v not in valid_targets:
            raise ValueError(f"target_type debe ser uno de {valid_targets}")
        return v
    
    @validator('optimizer')
    def validate_optimizer(cls, v):
        """Validar optimizador."""
        valid_optimizers = ['adam', 'adamw', 'lamb']
        if v not in valid_optimizers:
            raise ValueError(f"optimizer debe ser uno de {valid_optimizers}")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir configuración a diccionario."""
        return self.dict()
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ModelConfig':
        """Crear configuración desde diccionario."""
        return cls(**config_dict)
    
    def get_dtype(self) -> Any:
        """Obtener tipo de datos JAX."""
        dtype_map = {
            'float32': jnp.float32,
            'bfloat16': jnp.bfloat16,
            'float16': jnp.float16
        }
        return dtype_map[self.tpu_dtype]

class TrainingConfig(BaseModel):
    num_epochs: int = Field(default=10, description="Número de épocas")
    batch_size: int = Field(default=32, description="Tamaño de batch")
    learning_rate: float = Field(default=1e-4, description="Tasa de aprendizaje")
    weight_decay: float = Field(default=0.01, description="Decaimiento de pesos")
    warmup_steps: int = Field(default=1000, description="Pasos de warmup")
    gradient_clip: float = Field(default=1.0, description="Clip de gradientes")
    seed: int = Field(default=42, description="Semilla aleatoria")
    checkpoint_frequency: int = Field(default=1000, description="Frecuencia de checkpoints")
    early_stopping_patience: int = Field(default=5, description="Paciencia para early stopping")

    @validator('batch_size')
    def validate_batch_size(cls, v):
        if not (v & (v-1) == 0) and v != 0:
            logger.warning("batch_size no es potencia de 2, puede afectar rendimiento")
        return v
    
    @validator('learning_rate')
    def validate_learning_rate(cls, v):
        if v > 1e-3:
            logger.warning("learning_rate alto puede causar inestabilidad")
        return v

class WandbConfig(BaseModel):
    enabled: bool = Field(default=True, description="Habilitar Weights & Biases")
    project: str = Field(default="capibara-model", description="Proyecto W&B")
    entity: str = Field(default="", description="Entidad W&B")
    tags: List[str] = Field(default_factory=list, description="Tags W&B")

class PathsConfig(BaseModel):
    data_dir: Path = Field(default=Path("data"), description="Directorio de datos")
    checkpoint_dir: Path = Field(default=Path("checkpoints"), description="Directorio de checkpoints")
    output_dir: Path = Field(default=Path("output"), description="Directorio de salida")
    log_dir: Path = Field(default=Path("logs"), description="Directorio de logs")

    @validator('*')
    def ensure_paths_exist(cls, v):
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

# --------------------------------------------------
# Main Configuration Container
# --------------------------------------------------
class CapibaraConfig(BaseModel):
    model: ModelConfig = Field(default_factory=ModelConfig, description="Configuración del modelo")
    training: TrainingConfig = Field(default_factory=TrainingConfig, description="Configuración de entrenamiento")
    wandb: WandbConfig = Field(default_factory=WandbConfig, description="Configuración de W&B")
    paths: PathsConfig = Field(default_factory=PathsConfig, description="Configuración de rutas")
    tpu: TPUConfig = Field(default_factory=TPUConfig, description="Configuración TPU")
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig, description="Configuración de monitoreo")
    quantization: QuantizationConfig = Field(default_factory=QuantizationConfig, description="Configuración de cuantización")
    progressive_training: ProgressiveTrainingConfig = Field(default_factory=ProgressiveTrainingConfig, description="Configuración de entrenamiento progresivo")

    @validator("paths")
    def validate_paths(cls, v):
        for path in [v.data_dir, v.checkpoint_dir, v.output_dir, v.log_dir]:
            path.mkdir(parents=True, exist_ok=True)
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convertir la configuración a un diccionario."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "CapibaraConfig":
        """Crear una instancia de CapibaraConfig desde un diccionario."""
        return cls(**config_dict)

    @classmethod
    def from_yaml(cls, yaml_path: Union[str, Path]) -> "CapibaraConfig":
        """Cargar configuración desde un archivo YAML."""
        with open(yaml_path, "r") as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)

    def save_yaml(self, yaml_path: Union[str, Path]) -> None:
        """Guardar configuración en un archivo YAML."""
        with open(yaml_path, "w") as f:
            yaml.dump(self.to_dict(), f)

    @classmethod
    def from_env(cls) -> "CapibaraConfig":
        """Cargar configuración desde variables de entorno."""
        config_dict = {
            "model": {
                "hidden_size": int(os.getenv("CAPIBARA_HIDDEN_SIZE", "768")),
                "num_heads": int(os.getenv("CAPIBARA_NUM_HEADS", "8")),
                "num_layers": int(os.getenv("CAPIBARA_NUM_LAYERS", "12")),
                "dropout_rate": float(os.getenv("CAPIBARA_DROPOUT_RATE", "0.1")),
            },
            "training": {
                "num_epochs": int(os.getenv("CAPIBARA_NUM_EPOCHS", "10")),
                "batch_size": int(os.getenv("CAPIBARA_BATCH_SIZE", "32")),
                "learning_rate": float(os.getenv("CAPIBARA_LEARNING_RATE", "1e-4")),
            },
            "tpu": {
                "enabled": os.getenv("CAPIBARA_USE_TPU", "false").lower() == "true",
                "device": os.getenv("CAPIBARA_TPU_DEVICE", ""),
            }
        }
        return cls.from_dict(config_dict)

# --------------------------------------------------
# Configuration Loading Utilities
# --------------------------------------------------
def _update_nested_config(config_dict: Dict, key_path: str, value: Any):
    """Update nested configuration dictionary with dotted key path"""
    keys = key_path.split('.')
    current = config_dict
    for key in keys[:-1]:
        current = current.setdefault(key, {})
    current[keys[-1]] = value

def _apply_env_overrides(config_dict: Dict):
    """Apply environment variable overrides to configuration"""
    env_mappings = {
        # Model
        'model.hidden_size': 'MODEL_DIM',
        'model.num_heads': 'MODEL_HEADS',
        'model.quantization.enabled': 'QUANTIZATION',
        
        # Training
        'training.batch_size': 'BATCH_SIZE',
        'training.learning_rate': 'LEARNING_RATE',
        'training.num_epochs': 'EPOCHS',
        
        # W&B
        'wandb.project': 'WANDB_PROJECT',
        'wandb.entity': 'WANDB_ENTITY',
    }

    for config_path, env_var in env_mappings.items():
        env_val = os.getenv(env_var)
        if env_val is not None:
            try:
                current_val = OmegaConf.select(config_dict, config_path)
                if current_val is not None:
                    converted_val: Any = env_val
                    if isinstance(current_val, bool):
                        converted_val = env_val.lower() == 'true'
                    elif isinstance(current_val, int):
                        converted_val = int(env_val)
                    elif isinstance(current_val, float):
                        converted_val = float(env_val)
                
                _update_nested_config(config_dict, config_path, converted_val)
                logger.info(f"Overrode {config_path} from {env_var}")
            except Exception as e:
                logger.warning(f"Failed to override {config_path}: {str(e)}")

def load_config(config_path: Union[str, Path]) -> CapibaraConfig:
    """
    Carga y valida la configuración desde un archivo YAML.
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        CapibaraConfig: Configuración validada
        
    Raises:
        ValidationError: Si la configuración no es válida
        FileNotFoundError: Si el archivo no existe
    """
    try:
        # Cargar configuración base
        with open(config_path) as f:
            config_dict = yaml.safe_load(f)
        
        # Aplicar overrides de variables de entorno
        _apply_env_overrides(config_dict)
        
        # Validar configuración básica con Pydantic
        config = CapibaraConfig(**config_dict)
        
        # Realizar validaciones extendidas
        warnings = validate_full_config(config_dict)
        
        # Registrar warnings
        for warning in warnings:
            logger.warning(f"Advertencia de configuración: {warning}")
            
        if warnings:
            logger.warning(
                "Se encontraron advertencias en la configuración. "
                "Revise los logs para más detalles."
            )
        
        return config
        
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {config_path}")
    except ValidationError as e:
        logger.error("Error de validación en la configuración:")
        
        for error in e.errors():
            logger.error(f"  - {error['loc']}: {error['msg']}")
        raise
    except Exception as e:
        logger.error(f"Error al cargar la configuración: {str(e)}")
        raise

def save_config(config: CapibaraConfig, save_path: str) -> None:
    """
    Save configuration to YAML file
    
    Args:
        config: CapibaraConfig object to save
        save_path: Output file path
    """
    try:
        output_path = Path(save_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            yaml.dump(config.dict(), f, sort_keys=False)
            
        logger.info(f"Configuration saved to {save_path}")
    except Exception as e:
        logger.error(f"Failed to save configuration: {str(e)}")
        raise

__all__ = ['CapibaraConfig', 'load_config', 'save_config']
