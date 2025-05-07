"""
Configuración del sistema CapibaraGPT v2.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator #type: ignore
from pathlib import Path #type: ignore  
import os
import yaml #type: ignore
from datetime import timedelta

class SecuritySettings(BaseModel):
    """Configuración de seguridad."""
    api_key: str = Field(..., min_length=32)
    rate_limit: int = Field(100, ge=1, le=1000)
    jwt_secret: str = Field(..., min_length=32)
    jwt_algorithm: str = Field("HS256")
    token_expiry: timedelta = Field(timedelta(hours=1))

class DatabaseSettings(BaseModel):
    """Configuración de base de datos."""
    host: str = Field("localhost")
    port: int = Field(5432, ge=1, le=65535)
    name: str = Field("capibara")
    user: str = Field("postgres")
    password: str = Field(...)
    pool_size: int = Field(5, ge=1, le=20)
    timeout: int = Field(30, ge=1)

class ModelSettings(BaseModel):
    """Configuración de modelos."""
    health_advisor: Dict[str, Any] = Field(
        default_factory=lambda: {
            "min_confidence": 0.7,
            "cache_ttl": 3600
        }
    )
    doc_retriever: Dict[str, Any] = Field(
        default_factory=lambda: {
            "embedding_model": "all-MiniLM-L6-v2",
            "max_results": 5,
            "cache_ttl": 3600
        }
    )
    veracity_verifier: Dict[str, Any] = Field(
        default_factory=lambda: {
            "min_confidence": 0.8,
            "max_evidence": 5,
            "cache_ttl": 3600
        }
    )

class APISettings(BaseModel):
    """Configuración de API."""
    host: str = Field("0.0.0.0")
    port: int = Field(8000, ge=1, le=65535)
    workers: int = Field(4, ge=1, le=32)
    timeout: int = Field(30, ge=1)
    cors_origins: List[str] = Field(["*"])

class LoggingSettings(BaseModel):
    """Configuración de logging."""
    level: str = Field("INFO")
    format: str = Field("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file: Optional[str] = None
    max_size: int = Field(10_000_000)  # 10MB
    backup_count: int = Field(5)

class CacheSettings(BaseModel):
    """Configuración de caché."""
    enabled: bool = Field(True)
    ttl: int = Field(3600, ge=1)
    max_size: int = Field(1000, ge=1)
    backend: str = Field("memory")  # memory, redis

class Settings(BaseModel):
    """Configuración principal del sistema."""
    security: SecuritySettings
    database: DatabaseSettings
    models: ModelSettings
    api: APISettings
    logging: LoggingSettings
    cache: CacheSettings

    @validator("security")
    def validate_security(cls, v):
        if len(v.api_key) < 32:
            raise ValueError("API key debe tener al menos 32 caracteres")
        return v

    @validator("database")
    def validate_database(cls, v):
        if not v.password:
            raise ValueError("Se requiere contraseña de base de datos")
        return v

def load_yaml_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Carga la configuración desde un archivo YAML.
    
    Args:
        config_path: Ruta al archivo de configuración YAML
        
    Returns:
        Diccionario con la configuración
    """
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", "config/config.yaml")
    
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
    
    with open(config_file) as f:
        return yaml.safe_load(f)

def get_settings(config_path: Optional[str] = None) -> Settings:
    """
    Carga y valida la configuración del sistema.
    
    Args:
        config_path: Ruta al archivo de configuración YAML
        
    Returns:
        Objeto Settings con la configuración validada
    """
    config_data = load_yaml_config(config_path)
    return Settings(**config_data)

# Instancia global de configuración
settings = get_settings() 