"""
Configuración de entrenamiento de CapibaraModel.

Este módulo define la configuración específica para el entrenamiento del modelo,
incluyendo estrategias de entrenamiento, validación y monitoreo.
"""
from typing import Optional, List, Dict, Any, cast, TypeVar, Callable
try:
    from pydantic.v1 import BaseModel, Field, validator #type: ignore
except ImportError:
    raise ImportError("Por favor instala pydantic con: pip install pydantic")

try:
    import yaml #type: ignore
except ImportError:
    raise ImportError("Por favor instala PyYAML con: pip install PyYAML")

import os

T = TypeVar('T')

def typed_validator(field: str) -> Callable[[Callable[[Any, T], T]], Callable[[Any, T], T]]:
    """
    Decorador tipado para validadores de Pydantic.
    
    Args:
        field: Nombre del campo a validar
        
    Returns:
        Un decorador que envuelve la función de validación con tipos correctos
    """
    def decorator(func: Callable[[Any, T], T]) -> Callable[[Any, T], T]:
        return cast(Callable[[Any, T], T], validator(field)(func))
    return decorator

class TrainingConfig(BaseModel):
    """
    Configuración completa para el entrenamiento del modelo.
    
    Esta clase define todos los parámetros necesarios para configurar el proceso de entrenamiento,
    incluyendo optimización, estrategias de entrenamiento, validación y monitoreo.
    
    Attributes:
        epochs: Número total de épocas de entrenamiento
        steps_per_epoch: Pasos por época (opcional, se calcula automáticamente si es None)
        validation_steps: Pasos de validación por época (opcional)
        early_stopping_patience: Número de épocas sin mejora antes de detener el entrenamiento
        strategy: Estrategia de distribución (mirrored, multi_worker, etc.)
        use_tpu: Indica si se usa TPU para entrenamiento
        use_mixed_precision: Activa el uso de precisión mixta para acelerar el entrenamiento
        optimizer: Tipo de optimizador (adamw, sgd, etc.)
        learning_rate: Tasa de aprendizaje inicial
        warmup_steps: Número de pasos de calentamiento
        weight_decay: Factor de decaimiento de pesos para regularización
        gradient_clip_norm: Valor máximo para el clipping de gradientes
        use_gradient_centralization: Activa la centralización de gradientes para mejorar la generalización
        batch_size: Tamaño del batch de entrenamiento
        per_replica_batch_size: Tamaño del batch por réplica en entrenamiento distribuido
        save_checkpoints: Indica si se guardan checkpoints
        checkpoint_frequency: Frecuencia de guardado de checkpoints
        keep_checkpoint_max: Número máximo de checkpoints a mantener
        log_frequency: Frecuencia de logging de métricas
        tensorboard_update_freq: Frecuencia de actualización de TensorBoard
        validation_frequency: Frecuencia de validación
        metrics: Lista de métricas a monitorear
        progressive_training_config: Ruta a configuración de entrenamiento progresivo
        component_strategy_config: Ruta a configuración de estrategia por componentes
        custom_callbacks: Lista de callbacks personalizados
    """
    
    # Configuración básica
    epochs: int = Field(10, description="Número de épocas de entrenamiento")
    steps_per_epoch: Optional[int] = Field(None, description="Pasos por época")
    validation_steps: Optional[int] = Field(None, description="Pasos de validación")
    early_stopping_patience: int = Field(3, description="Paciencia para early stopping")
    
    # Configuración de estrategia
    strategy: str = Field("mirrored", description="Estrategia de distribución")
    use_tpu: bool = Field(False, description="Usar TPU para entrenamiento")
    use_mixed_precision: bool = Field(True, description="Usar precisión mixta")
    
    # Configuración de optimización
    optimizer: str = Field("adamw", description="Optimizador a usar")
    learning_rate: float = Field(1e-4, description="Tasa de aprendizaje base")
    warmup_steps: int = Field(1000, description="Pasos de calentamiento")
    weight_decay: float = Field(0.01, description="Decaimiento de pesos")
    gradient_clip_norm: float = Field(1.0, description="Norma de gradiente para clipping")
    use_gradient_centralization: bool = Field(
        True, 
        description="Usar Gradient Centralization para mejorar la generalización"
    )
    
    # Configuración de batch
    batch_size: int = Field(32, description="Tamaño del batch")
    per_replica_batch_size: Optional[int] = Field(None, description="Tamaño del batch por réplica")
    
    # Configuración de checkpoints
    save_checkpoints: bool = Field(True, description="Guardar checkpoints")
    checkpoint_frequency: int = Field(1000, description="Frecuencia de guardado de checkpoints")
    keep_checkpoint_max: int = Field(5, description="Número máximo de checkpoints a mantener")
    
    # Configuración de logging
    log_frequency: int = Field(100, description="Frecuencia de logging")
    tensorboard_update_freq: int = Field(100, description="Frecuencia de actualización de TensorBoard")
    
    # Configuración de validación
    validation_frequency: int = Field(1000, description="Frecuencia de validación")
    metrics: List[str] = Field(
        default_factory=lambda: ["loss", "accuracy"],
        description="Métricas a monitorear"
    )
    
    # Configuración de estrategias
    progressive_training_config: Optional[str] = Field(
        None,
        description="Ruta al archivo de configuración de entrenamiento progresivo"
    )
    component_strategy_config: Optional[str] = Field(
        None,
        description="Ruta al archivo de estrategia por componentes"
    )
    
    # Configuración avanzada
    custom_callbacks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Callbacks personalizados"
    )
    
    def load_progressive_config(self) -> Dict[str, Any]:
        """
        Carga la configuración de entrenamiento progresivo desde archivo YAML.
        
        Returns:
            Dict[str, Any]: Configuración cargada como diccionario
            
        Raises:
            FileNotFoundError: Si el archivo de configuración no existe
        """
        if not self.progressive_training_config:
            return {}
        
        if not os.path.exists(self.progressive_training_config):
            raise FileNotFoundError(
                f"Archivo de configuración progresiva no encontrado: {self.progressive_training_config}"
            )
        
        with open(self.progressive_training_config, 'r') as f:
            return cast(Dict[str, Any], yaml.safe_load(f))
    
    def load_component_strategy(self) -> Dict[str, Any]:
        """
        Carga la estrategia de entrenamiento por componentes desde archivo YAML.
        
        Returns:
            Dict[str, Any]: Estrategia cargada como diccionario
            
        Raises:
            FileNotFoundError: Si el archivo de estrategia no existe
        """
        if not self.component_strategy_config:
            return {}
        
        if not os.path.exists(self.component_strategy_config):
            raise FileNotFoundError(
                f"Archivo de estrategia por componentes no encontrado: {self.component_strategy_config}"
            )
        
        with open(self.component_strategy_config, 'r') as f:
            return cast(Dict[str, Any], yaml.safe_load(f))
    
    @typed_validator('learning_rate')
    def validate_learning_rate(cls, v: float) -> float:
        """
        Valida que la tasa de aprendizaje sea positiva.
        
        Args:
            v: Valor de la tasa de aprendizaje a validar
            
        Returns:
            float: Tasa de aprendizaje validada
            
        Raises:
            ValueError: Si la tasa de aprendizaje no es positiva
        """
        if v <= 0:
            raise ValueError("La tasa de aprendizaje debe ser positiva")
        return v
    
    @typed_validator('batch_size')
    def validate_batch_size(cls, v: int) -> int:
        """
        Valida que el tamaño del batch sea positivo.
        
        Args:
            v: Valor del tamaño de batch a validar
            
        Returns:
            int: Tamaño de batch validado
            
        Raises:
            ValueError: Si el tamaño de batch no es positivo
        """
        if v <= 0:
            raise ValueError("El tamaño del batch debe ser positivo")
        return v
    
    class Config:
        """
        Configuración de Pydantic para la clase TrainingConfig.
        
        Attributes:
            validate_assignment: Activa la validación al asignar valores
            extra: Prohíbe campos adicionales no definidos en el modelo
        """
        validate_assignment = True
        extra = "forbid" 