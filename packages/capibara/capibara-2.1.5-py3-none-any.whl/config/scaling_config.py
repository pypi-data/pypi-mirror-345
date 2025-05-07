"""
Configuración de escalado para CapibaraModel.

Este módulo define la configuración para el plan de escalado del modelo,
incluyendo las diferentes fases y características avanzadas.
"""
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, validator #type: ignore
import yaml #type: ignore
import os
from pathlib import Path

class ScalingPhase(BaseModel):
    """Configuración de una fase de escalado."""
    name: str
    target_params: int
    dataset_tokens: int
    precision: Literal["FP16", "FP8", "FP4"]
    purpose: str
    checkpoint_interval: int

class ArchitectureConfig(BaseModel):
    """Configuración de la arquitectura base."""
    base_model: str = "BitNet1.58"
    activation: str = "SwiGLU"
    normalization: str = "RootMeanSquareNorm"
    positional_embedding: str = "Rotary"
    attention_mechanism: List[str] = ["MambaSSM", "FlashAttention2"]
    
    scaling: Dict[str, Any] = Field(
        default_factory=lambda: {
            "method": "u-µP",
            "precision": "FP16",
            "transfer_hyperparams": True,
            "direct_fp16_training": True
        }
    )

class QuantumEmbeddingConfig(BaseModel):
    """Configuración de la capa de embedding cuántico."""
    enabled: bool = True
    mode: Literal["classic", "quantum4", "quantum16"] = "quantum16"
    states_per_param: int = 16
    encoding_type: Literal["discrete", "vectorial", "binary"] = "vectorial"
    temperature: float = 0.1
    use_softmax: bool = True

class QuantumSubmodelConfig(BaseModel):
    """Configuración del submodelo cuántico."""
    enabled: bool = True
    activation_mode: str = "dynamic"
    trigger_keywords: List[str] = ["quantum", "physics", "simulation", "system"]
    router: Dict[str, Any] = Field(
        default_factory=lambda: {
            "type": "attention_based",
            "threshold": 0.7
        }
    )
    cross_attention: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "latent_dim": 128
        }
    )

class QuantizationConfig(BaseModel):
    """Configuración de cuantización."""
    training: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "precision": "FP8",
            "method": "SmoothQuant",
            "fine_grained": True,
            "quantize_weights": True,
            "quantize_activations": True,
            "quantize_softmax": True
        }
    )
    inference: Dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "precision": "FP8",
            "method": "ZeroQuant",
            "dynamic_range": True
        }
    )

class ScalingConfig(BaseModel):
    """Configuración completa de escalado."""
    architecture: ArchitectureConfig = Field(default_factory=ArchitectureConfig)
    quantum_embedding: QuantumEmbeddingConfig = Field(default_factory=QuantumEmbeddingConfig)
    quantum_submodel: QuantumSubmodelConfig = Field(default_factory=QuantumSubmodelConfig)
    quantization: QuantizationConfig = Field(default_factory=QuantizationConfig)
    scaling_plan: Dict[str, List[ScalingPhase]] = Field(
        default_factory=lambda: {
            "phases": [
                ScalingPhase(
                    name="300M",
                    target_params=300000000,
                    dataset_tokens=3000000000,
                    precision="FP16",
                    purpose="Pipeline validation",
                    checkpoint_interval=1000
                ),
                # ... otras fases ...
            ]
        }
    )
    monitoring: Dict[str, Any] = Field(
        default_factory=lambda: {
            "metrics": ["loss", "perplexity", "quantum_activation_rate"],
            "alerts": {
                "quantum_activation_threshold": 0.8,
                "memory_usage_threshold": 0.9,
                "precision_loss_threshold": 0.1
            },
            "logging": {
                "frequency": 100,
                "tensorboard": True,
                "wandb": True
            }
        }
    )
    optimization: Dict[str, Any] = Field(
        default_factory=lambda: {
            "gradient_checkpointing": True,
            "mixed_precision": True,
            "gradient_clip_norm": 1.0,
            "zero_stage": 2,
            "sharding": "2d",
            "remat": True
        }
    )
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'ScalingConfig':
        """
        Carga la configuración desde un archivo YAML.
        
        Args:
            yaml_path: Ruta al archivo YAML de configuración
            
        Returns:
            ScalingConfig: Instancia de configuración de escalado
        """
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {yaml_path}")
            
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)
            
        return cls(**config_dict)
    
    def to_yaml(self, yaml_path: str) -> None:
        """
        Guarda la configuración en un archivo YAML.
        
        Args:
            yaml_path: Ruta donde guardar el archivo YAML
        """
        config_dict = self.dict()
        with open(yaml_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
    
    def get_current_phase(self, current_params: int) -> Optional[ScalingPhase]:
        """
        Obtiene la fase actual basada en el número de parámetros.
        
        Args:
            current_params: Número actual de parámetros del modelo
            
        Returns:
            Optional[ScalingPhase]: Fase actual o None si no hay fase correspondiente
        """
        for phase in self.scaling_plan["phases"]:
            if current_params <= phase.target_params:
                return phase
        return None
    
    class Config:
        """Configuración de Pydantic."""
        validate_assignment = True
        extra = "forbid" 