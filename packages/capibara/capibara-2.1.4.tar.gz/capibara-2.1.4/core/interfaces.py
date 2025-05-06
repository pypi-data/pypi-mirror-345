from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
import jax.numpy as jnp # type: ignore
from dataclasses import dataclass

@dataclass
class ModelInput:
    """Estructura de entrada para el modelo."""
    input_ids: jnp.ndarray
    attention_mask: Optional[jnp.ndarray] = None
    position_ids: Optional[jnp.ndarray] = None
    token_type_ids: Optional[jnp.ndarray] = None
    deterministic: bool = True

@dataclass
class ModelOutput:
    """Estructura de salida del modelo."""
    last_hidden_state: jnp.ndarray
    hidden_states: Optional[Tuple[jnp.ndarray, ...]] = None
    attentions: Optional[Tuple[jnp.ndarray, ...]] = None
    loss: Optional[jnp.ndarray] = None

class BaseLayer(ABC):
    """Interfaz base para capas del modelo."""
    
    @abstractmethod
    def __call__(self, 
                 hidden_states: jnp.ndarray,
                 attention_mask: Optional[jnp.ndarray] = None,
                 deterministic: bool = True) -> Tuple[jnp.ndarray, Optional[Tuple[jnp.ndarray, ...]]]:
        """Forward pass de la capa."""
        pass

class BaseModel(ABC):
    """Interfaz base para el modelo."""
    
    @abstractmethod
    def __call__(self, 
                 input_ids: jnp.ndarray,
                 attention_mask: Optional[jnp.ndarray] = None,
                 position_ids: Optional[jnp.ndarray] = None,
                 token_type_ids: Optional[jnp.ndarray] = None,
                 deterministic: bool = True) -> ModelOutput:
        """Forward pass del modelo."""
        pass
    
    @abstractmethod
    def generate(self,
                 input_ids: jnp.ndarray,
                 max_length: int,
                 num_beams: int = 1,
                 temperature: float = 1.0,
                 top_k: int = 50,
                 top_p: float = 1.0,
                 do_sample: bool = True) -> jnp.ndarray:
        """Generación de texto."""
        pass

class ContentFilter(ABC):
    """Interfaz para filtro de contenido."""
    
    @abstractmethod
    def is_safe(self, text: str) -> bool:
        """Verifica si el texto es seguro."""
        pass
    
    @abstractmethod
    def get_risk_score(self, text: str) -> float:
        """Obtiene el puntaje de riesgo del texto."""
        pass
    
    @abstractmethod
    def get_risk_categories(self, text: str) -> List[str]:
        """Obtiene las categorías de riesgo del texto."""
        pass 