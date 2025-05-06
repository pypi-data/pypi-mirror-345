"""Interfaz estándar para capas del modelo Capibara.

Esta interfaz define el contrato común que deben implementar todas las capas
del modelo, asegurando consistencia en inputs/outputs y métricas.
"""

from typing import Protocol, Dict, Any, Optional
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore

class ILayer(Protocol):
    """Interfaz estándar para capas del modelo Capibara.
    
    Todas las capas deben implementar este protocolo, asegurando:
    - Entrada: Tensor JAX de forma (batch_size, seq_len, hidden_dim)
    - Salida: Dict con 'output' y 'metrics'
    - Soporte para modo entrenamiento/inferencia
    
    Ejemplo de uso:
    ```python
    class MiCapa(nn.Module, ILayer):
        hidden_size: int
        
        @nn.compact
        def __call__(self, x, training=False, **kwargs):
            # Procesamiento
            x = nn.Dense(self.hidden_size)(x)
            
            # Métricas
            metrics = {
                "norm": jnp.linalg.norm(x),
                "mean": jnp.mean(x)
            }
            
            return {
                "output": x,
                "metrics": metrics,
                "training": training
            }
    ```
    
    Requisitos de memoria:
    - Input: O(batch_size * seq_len * hidden_dim)
    - Output: O(batch_size * seq_len * hidden_dim)
    - Métricas: O(1) por métrica
    """
    
    def __call__(
        self,
        x: jnp.ndarray,
        training: bool = False,
        rng: Optional[nn.PRNGKey] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Aplica la transformación de la capa.
        
        Args:
            x: Tensor de entrada de forma (batch_size, seq_len, hidden_dim)
            training: Si True, activa modo entrenamiento (dropout, etc)
            rng: Key aleatoria para operaciones estocásticas
            **kwargs: Argumentos adicionales específicos de la capa
            
        Returns:
            Dict con:
                - output: Tensor de salida (batch_size, seq_len, hidden_dim)
                - metrics: Dict con métricas de la capa
                - training: Estado de entrenamiento
                
        Ejemplo:
        ```python
        # Uso básico
        output = capa(x)
        
        # Con entrenamiento
        output = capa(x, training=True, rng=key)
        
        # Acceso a métricas
        metrics = output["metrics"]
        ```
        """
        ... 