"""
Configuraciones para componentes cuánticos de CapibaraGPT
Incluye configuraciones para bloques, VQbits y parámetros generales
"""

from typing import Literal, Dict, Optional, Union
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)

class QuantumConfig(BaseModel):
    """
    Configuración general para componentes cuánticos
    """
    hidden_size: int = Field(
        ...,
        gt=0,
        description="Tamaño del espacio latente cuántico"
    )
    num_heads: int = Field(
        ...,
        gt=0,
        description="Número de cabezas de atención cuántica"
    )
    num_layers: int = Field(
        ...,
        gt=0,
        description="Número de capas cuánticas"
    )
    embedding_mode: str = Field(
        default="quantum8",
        description="Modo de embedding cuántico (quantum8/quantum16)"
    )
    num_virtual_qubits: int = Field(
        default=1000,
        description="Número de qubits virtuales a simular"
    )
    states_per_qubit: int = Field(
        default=16,
        description="Estados por qubit (16 o 32)"
    )
    param_chunk_size: int = Field(
        default=1024,
        description="Tamaño del chunk de parámetros por qubit"
    )
    memory_limit_gb: float = Field(
        default=10.0,
        description="Límite de memoria en GB"
    )

    @validator('embedding_mode')
    def validate_embedding_mode(cls, v):
        valid_modes = ["quantum8", "quantum16", "quantum32"]
        if v not in valid_modes:
            raise ValueError(f"embedding_mode debe ser uno de {valid_modes}")
        return v

    @validator('states_per_qubit')
    def validate_states(cls, v):
        if v not in [16, 32]:
            raise ValueError("states_per_qubit debe ser 16 o 32")
        return v

    def estimate_memory_usage(self) -> float:
        """Estima el uso de memoria en GB"""
        params_per_qubit = self.param_chunk_size
        total_params = self.num_virtual_qubits * params_per_qubit
        memory_gb = (total_params * 8) / (1024**3)  # 8 bytes por float64
        
        if memory_gb > self.memory_limit_gb:
            logger.warning(
                f"Configuración requiere {memory_gb:.2f}GB, "
                f"excede límite de {self.memory_limit_gb}GB"
            )
        
        return memory_gb

class QuantumBlockConfig(BaseModel):
    """
    Configuración para bloques cuánticos
    """
    block_size: Literal["8M", "16M", "32M"] = Field(
        default="8M",
        description="Tamaño del bloque de parámetros"
    )
    num_blocks: int = Field(
        default=1,
        description="Número de bloques a utilizar"
    )
    states_per_qubit: Literal[16, 32] = Field(
        default=32,
        description="Estados por qubit"
    )

    def get_block_size_bytes(self) -> int:
        """Convierte el tamaño del bloque a bytes"""
        sizes = {
            "8M": 8 * 1024 * 1024,
            "16M": 16 * 1024 * 1024,
            "32M": 32 * 1024 * 1024
        }
        return sizes[self.block_size]

class VQbitConfig(BaseModel):
    """
    Configuración para qubits virtuales
    """
    block_size: Literal["8M", "16M", "32M"] = Field(
        default="8M",
        description="Tamaño del bloque base"
    )
    num_vqbits: int = Field(
        default=4,
        description="Número de qubits virtuales"
    )
    states_per_vqbit: Literal[16, 32] = Field(
        default=32,
        description="Estados por qubit virtual"
    )
    params_per_vqbit: Optional[int] = Field(
        default=None,
        description="Parámetros por qubit virtual"
    )
    backend_priority: Dict[str, float] = Field(
        default_factory=lambda: {
            "jax": 1.0,
            "pennylane": 0.8,
            "qiskit": 0.6
        },
        description="Prioridades de backends cuánticos"
    )

    @validator('backend_priority')
    def validate_priorities(cls, v):
        if not all(0 <= p <= 1 for p in v.values()):
            raise ValueError("Todas las prioridades deben estar entre 0 y 1")
        return v

    def calculate_memory_requirements(self) -> Dict[str, float]:
        """Calcula requisitos de memoria"""
        block_sizes = {
            "8M": 8,
            "16M": 16,
            "32M": 32
        }
        
        base_size_mb = block_sizes[self.block_size]
        params_size = (self.params_per_vqbit or base_size_mb * 1024 * 1024) * 8  # bytes
        total_size_gb = (params_size * self.num_vqbits) / (1024**3)
        
        return {
            "per_vqbit_mb": params_size / (1024**2),
            "total_gb": total_size_gb,
            "states_memory_mb": (self.states_per_vqbit * self.num_vqbits * 8) / (1024**2)
        }

# Funciones de utilidad para configuración
def create_default_quantum_config(hidden_size: int) -> QuantumConfig:
    """Crea una configuración cuántica por defecto"""
    return QuantumConfig(
        hidden_size=hidden_size,
        num_heads=8,
        num_layers=6,
        embedding_mode="quantum8",
        num_virtual_qubits=1000,
        states_per_qubit=16,
        param_chunk_size=1024,
        memory_limit_gb=10.0
    )

def create_efficient_vqbit_config(num_vqbits: int) -> VQbitConfig:
    """Crea una configuración eficiente de VQbits"""
    return VQbitConfig(
        block_size="8M",
        num_vqbits=num_vqbits,
        states_per_vqbit=16,
        params_per_vqbit=None,
        backend_priority={
            "jax": 1.0,
            "pennylane": 0.7,
            "qiskit": 0.5
        }
    )

# Ejemplo de uso:
if __name__ == "__main__":
    # Configuración básica
    config = create_default_quantum_config(hidden_size=512)
    print(f"Uso de memoria estimado: {config.estimate_memory_usage():.2f}GB")
    
    # Configuración de VQbits
    vqbit_config = create_efficient_vqbit_config(num_vqbits=4)
    memory_reqs = vqbit_config.calculate_memory_requirements()
    print(f"Memoria por VQbit: {memory_reqs['per_vqbit_mb']:.2f}MB")
    print(f"Memoria total: {memory_reqs['total_gb']:.2f}GB")