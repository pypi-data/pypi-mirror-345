"""
Configuración específica para TPU en CapibaraModel.

Este módulo define la configuración necesaria para el entrenamiento en TPU,
incluyendo validación y carga desde archivos YAML.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator #type: ignore
import yaml #type: ignore
import os #thype: ignore

class TPUConfig(BaseModel):
    """Configuración para el uso de TPU."""
    
    # Configuración básica
    enabled: bool = Field(True, description="Habilitar uso de TPU")
    num_cores: int = Field(8, description="Número de cores TPU a usar")
    dtype: str = Field("bfloat16", description="Tipo de datos para cálculos")
    precision: str = Field("high", description="Precisión de cálculos")
    optimization_level: int = Field(3, description="Nivel de optimización")
    enable_xla: bool = Field(True, description="Habilitar XLA para optimización")
    enable_auto_mixed_precision: bool = Field(True, description="Habilitar precisión mixta automática")
    
    # Configuración de memoria
    memory_limit: Optional[int] = Field(None, description="Límite de memoria en bytes")
    memory_fraction: float = Field(0.9, description="Fracción de memoria a usar")
    
    # Configuración de rendimiento
    batch_size_per_core: int = Field(16, description="Tamaño de batch por core")
    steps_per_loop: int = Field(100, description="Pasos por iteración")
    
    # Configuración de logging
    tpu_log_level: str = Field("INFO", description="Nivel de logging para TPU")
    
    @validator('num_cores')
    def validate_num_cores(cls, v):
        """Valida que el número de cores sea válido."""
        valid_cores = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
        if v not in valid_cores:
            raise ValueError(f"El número de cores debe ser uno de: {valid_cores}")
        return v
    
    @validator('dtype')
    def validate_dtype(cls, v):
        """Valida que el tipo de datos sea válido."""
        valid_dtypes = ["bfloat16", "float32", "float16"]
        if v not in valid_dtypes:
            raise ValueError(f"El tipo de datos debe ser uno de: {valid_dtypes}")
        return v
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'TPUConfig':
        """
        Carga la configuración desde un archivo YAML.
        
        Args:
            yaml_path: Ruta al archivo YAML de configuración
            
        Returns:
            TPUConfig: Instancia de configuración de TPU
            
        Raises:
            FileNotFoundError: Si el archivo YAML no existe
            yaml.YAMLError: Si hay error al parsear el YAML
        """
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {yaml_path}")
            
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)
            
        # Extraer la sección tpu del YAML
        tpu_config = config_dict.get('tpu', {})
        return cls(**tpu_config)
    
    def to_yaml(self, yaml_path: str) -> None:
        """
        Guarda la configuración en un archivo YAML.
        
        Args:
            yaml_path: Ruta donde guardar el archivo YAML
        """
        config_dict = {'tpu': self.dict()}
        with open(yaml_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
    
    class Config:
        """Configuración de Pydantic."""
        validate_assignment = True
        extra = "forbid" 