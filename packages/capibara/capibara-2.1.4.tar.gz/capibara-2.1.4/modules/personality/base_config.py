from pydantic import BaseModel, Field # type: ignore
from typing import Optional

class BasePersonalityConfig(BaseModel):
    """Configuración base para módulos de personalidad.
    
    Args:
        hidden_size: Dimensión del espacio oculto
        coherence_threshold: Umbral de coherencia
        dropout_rate: Tasa de dropout
        num_heads: Número de cabezas de atención
    """
    hidden_size: int = Field(..., gt=0, description="Dimensión del espacio oculto")
    coherence_threshold: float = Field(default=0.6, ge=0, le=1, description="Umbral de coherencia")
    dropout_rate: float = Field(default=0.1, ge=0, le=1, description="Tasa de dropout")
    num_heads: int = Field(default=8, gt=0, description="Número de cabezas de atención")
    deterministic: bool = Field(default=False, description="Modo determinista")
    prevent_cse: bool = Field(default=False, description="Prevenir optimizaciones CSE") 