from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, model_validator # type: ignore
import numpy as np # type: ignore
import os
from pathlib import Path

class TPUConfig(BaseModel):
    cores: int = Field(..., ge=1, description="Número de cores TPU")
    memory_gb: int = Field(..., ge=8, description="Memoria disponible en GB")
    topology: str = Field(..., description="Topología de la TPU (ej: 2x4)")
    dtype: str = Field("float32", description="Tipo de datos para computación")
    use_bfloat16: bool = Field(True, description="Usar bfloat16 para optimización")
    use_8bit_optimizer: bool = Field(True, description="Usar optimizador de 8 bits")
    gradient_accumulation_steps: int = Field(1, ge=1, description="Pasos de acumulación de gradientes")
    sharding_strategy: str = Field("data_parallel", description="Estrategia de sharding")

    @validator("dtype")
    def validate_dtype(cls, v):
        valid_dtypes = ["float32", "float16", "bfloat16"]
        if v not in valid_dtypes:
            raise ValueError(f"dtype debe ser uno de {valid_dtypes}")
        return v

    @validator("sharding_strategy")
    def validate_sharding(cls, v):
        valid_strategies = ["data_parallel", "model_parallel", "hybrid"]
        if v not in valid_strategies:
            raise ValueError(f"sharding_strategy debe ser uno de {valid_strategies}")
        return v

class WandbConfig(BaseModel):
    project: str = Field(..., description="Nombre del proyecto en Weights & Biases")
    entity: str = Field(..., description="Entidad/organización en Weights & Biases")
    tags: List[str] = Field(default_factory=list, description="Tags para el experimento")

class MonitoringConfig(BaseModel):
    enabled: bool = Field(True, description="Habilitar monitoreo")
    log_interval: int = Field(100, ge=1, description="Intervalo de logging")
    save_interval: int = Field(1000, ge=1, description="Intervalo de guardado")
    metrics: List[str] = Field(..., description="Métricas a monitorear")
    wandb: WandbConfig

class QuantizationConfig(BaseModel):
    """Configuración de cuantización avanzada."""
    enabled: bool = Field(True, description="Habilitar cuantización")
    bits: int = Field(8, ge=2, le=32, description="Bits para cuantización")
    mode: str = Field(default="fp8", description="Modo de cuantización: fp4, fp8, int4, int8")
    symmetric: bool = Field(True, description="Usar cuantización simétrica")
    per_channel: bool = Field(True, description="Cuantización por canal")
    granularity: str = Field("tensor", description="Granularidad de cuantización")
    calibration: dict = Field(..., description="Configuración de calibración")
    qat: dict = Field(..., description="Configuración de QAT")

    @validator("granularity")
    def validate_granularity(cls, v):
        valid_granularities = ["tensor", "channel", "group"]
        if v not in valid_granularities:
            raise ValueError(f"granularity debe ser uno de {valid_granularities}")
        return v

    @validator("mode")
    def validate_mode(cls, v):
        valid = ["fp4", "fp8", "int4", "int8"]
        if v not in valid:
            raise ValueError(f"quantization.mode debe ser uno de {valid}")
        return v

class QuantumRoutingConfig(BaseModel):
    """Configuración de enrutamiento cuántico."""
    use_quantum_submodel: bool = Field(default=False, description="Activar submodelo cuántico")
    quantum_trigger_keywords: List[str] = Field(
        default=["qubit", "entanglement", "quantum circuit", "wavefunction"],
        description="Palabras clave que activan el submodelo cuántico"
    )
    quantum_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Umbral de activación cuántica")
    quantum_cache_size: int = Field(default=1000, ge=1, description="Tamaño de caché para estados cuánticos")

class CheckpointingConfig(BaseModel):
    enabled: bool = Field(True, description="Habilitar checkpointing")
    interval: int = Field(5000, ge=1, description="Intervalo de checkpointing")
    max_to_keep: int = Field(5, ge=1, description="Máximo número de checkpoints a mantener")

class ValidationConfig(BaseModel):
    interval: int = Field(1000, ge=1, description="Intervalo de validación")
    metrics: List[str] = Field(..., description="Métricas de validación")

class TrainingConfig(BaseModel):
    batch_size: int = Field(..., ge=1, description="Tamaño de batch")
    learning_rate: float = Field(..., gt=0, description="Learning rate")
    weight_decay: float = Field(..., ge=0, description="Weight decay")
    warmup_steps: int = Field(..., ge=0, description="Pasos de warmup")
    max_steps: int = Field(..., ge=1, description="Máximo número de pasos")
    gradient_clip: float = Field(..., gt=0, description="Valor de clip para gradientes")
    optimizer: str = Field(..., description="Optimizador a utilizar")
    scheduler: str = Field(..., description="Scheduler a utilizar")
    mixed_precision: bool = Field(True, description="Usar precisión mixta")
    checkpointing: CheckpointingConfig
    validation: ValidationConfig

    @validator("optimizer")
    def validate_optimizer(cls, v):
        valid_optimizers = ["adam", "adamw", "sgd", "lamb"]
        if v not in valid_optimizers:
            raise ValueError(f"optimizer debe ser uno de {valid_optimizers}")
        return v

    @validator("scheduler")
    def validate_scheduler(cls, v):
        valid_schedulers = ["cosine", "linear", "constant", "warmup_cosine"]
        if v not in valid_schedulers:
            raise ValueError(f"scheduler debe ser uno de {valid_schedulers}")
        return v

class PathsConfig(BaseModel):
    """Configuración de rutas del proyecto."""
    data_dir: str = Field(..., description="Directorio de datos")
    checkpoint_dir: str = Field(..., description="Directorio de checkpoints")
    output_dir: str = Field(..., description="Directorio de salida")
    log_dir: str = Field(..., description="Directorio de logs")
    model_dir: str = Field(..., description="Directorio de modelos")
    tokenizer_path: str = Field(..., description="Ruta al tokenizador")

    @model_validator(mode='after')
    def validate_paths(self) -> 'PathsConfig':
        """Valida y crea las rutas necesarias."""
        for field_name, field_value in self.model_dump().items():
            if field_name.endswith('_dir'):
                path = Path(field_value)
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)
        return self

class ModelConfig(BaseModel):
    """Configuración del modelo con soporte cuántico."""
    vocab_size: int = Field(..., ge=1, description="Tamaño del vocabulario")
    hidden_size: int = Field(..., ge=1, description="Tamaño de la capa oculta")
    num_layers: int = Field(..., ge=1, description="Número de capas")
    num_heads: int = Field(..., ge=1, description="Número de cabezas de atención")
    intermediate_size: int = Field(..., ge=1, description="Tamaño de la capa intermedia")
    max_position_embeddings: int = Field(..., ge=1, description="Máxima longitud de secuencia")
    dropout: float = Field(..., ge=0, lt=1, description="Dropout rate")
    attention_dropout: float = Field(..., ge=0, lt=1, description="Dropout rate para atención")
    activation: str = Field(..., description="Función de activación")
    layer_norm_eps: float = Field(..., gt=0, description="Epsilon para layer norm")
    initializer_range: float = Field(..., gt=0, description="Rango del inicializador")
    use_cache: bool = Field(True, description="Usar caché para inferencia")
    pad_token_id: int = Field(..., description="ID del token de padding")
    bos_token_id: int = Field(..., description="ID del token de inicio")
    eos_token_id: int = Field(..., description="ID del token de fin")
    
    # Configuraciones cuánticas
    embedding_mode: str = Field(default="classic", description="Modo de embedding: classic, quantum4, quantum8, quantum16")
    quantum_routing: QuantumRoutingConfig = Field(default_factory=QuantumRoutingConfig)
    dominant_modality: str = Field(default="text", description="Modalidad principal: text, audio, code, image, multimodal")

    @validator("activation")
    def validate_activation(cls, v):
        valid_activations = ["gelu", "relu", "silu", "tanh"]
        if v not in valid_activations:
            raise ValueError(f"activation debe ser uno de {valid_activations}")
        return v

    @validator("embedding_mode")
    def validate_embedding_mode(cls, v):
        valid_modes = ["classic", "quantum4", "quantum8", "quantum16"]
        if v not in valid_modes:
            raise ValueError(f"embedding_mode debe ser uno de {valid_modes}")
        return v

    @validator("dominant_modality")
    def validate_dominant_modality(cls, v):
        valid = ["text", "audio", "code", "image", "multimodal"]
        if v not in valid:
            raise ValueError(f"dominant_modality debe ser uno de {valid}")
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a diccionario usando Pydantic V2."""
        return self.model_dump()

class CapibaraConfig(BaseModel):
    """Configuración completa de CapibaraModel."""
    tpu: TPUConfig
    monitoring: MonitoringConfig
    quantization: QuantizationConfig
    training: TrainingConfig
    model: ModelConfig
    paths: PathsConfig

    @model_validator(mode='after')
    def validate_config(self) -> 'CapibaraConfig':
        """Valida la configuración completa."""
        # Validación de rutas
        self.paths.validate_paths()
        
        # Validación de compatibilidad entre componentes
        if self.model.quantum_routing.use_quantum_submodel:
            if self.quantization.mode not in ["fp4", "fp8"]:
                raise ValueError("El submodelo cuántico requiere cuantización FP4 o FP8")
            if self.model.embedding_mode == "classic":
                raise ValueError("El submodelo cuántico requiere un modo de embedding cuántico")
            
        if self.model.embedding_mode.startswith("quantum") and not self.model.quantum_routing.use_quantum_submodel:
            raise ValueError("El modo de embedding cuántico requiere el submodelo cuántico activado")
            
        return self

    @classmethod
    def load_from_env(cls, env_prefix: str = "CAPIBARA_") -> 'CapibaraConfig':
        """Carga configuración desde variables de entorno."""
        env_vars = {
            k[len(env_prefix):].lower(): v 
            for k, v in os.environ.items() 
            if k.startswith(env_prefix)
        }
        return cls.model_validate(env_vars)

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Serializa la configuración a diccionario."""
        return super().model_dump(**kwargs)

    class Config:
        """Configuración de Pydantic V2."""
        extra = "forbid"
        validate_assignment = True
        arbitrary_types_allowed = True