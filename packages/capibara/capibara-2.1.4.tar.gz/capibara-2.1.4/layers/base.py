
Esta capa proporciona funcionalidad base para todas las capas del modelo,
incluyendo métricas estándar y manejo de configuración.
"""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from typing import Dict, Any, Optional
from interfaces.ilayer import ILayer
from dataclasses import dataclass

@dataclass
class LayerConfig:
    """Configuración base para capas.
    
    Args:
        hidden_size: Dimensión del espacio oculto
        dropout_rate: Tasa de dropout
        deterministic: Si True, desactiva estocasticidad
        prevent_cse: Si True, previene eliminación de subexpresiones comunes
    """
    hidden_size: int
    dropout_rate: float = 0.1
    deterministic: bool = False
    prevent_cse: bool = False

class BaseLayer(nn.Module, ILayer):
    """Capa base con métricas estándar.
    
    Proporciona:
    - Métricas base (norma, gradiente, memoria)
    - Manejo de configuración
    - Soporte para entrenamiento/inferencia
    
    Ejemplo de uso:
    ```python
    class MiCapa(BaseLayer):
        def setup(self):
            super().setup()
            self.dense = nn.Dense(self.config.hidden_size)
            
        def __call__(self, x, training=False, **kwargs):
            x = self.dense(x)
            return self._base_call(x, training=training)
    ```
    """
    
    config: LayerConfig
    
    def setup(self):
        """Inicializa la capa base."""
        self.is_training = not self.config.deterministic
        
    def _base_metrics(
        self,
        x: jnp.ndarray,
        output: jnp.ndarray
    ) -> Dict[str, jnp.ndarray]:
        """Calcula métricas base.
        
        Args:
            x: Tensor de entrada (batch_size, seq_len, hidden_dim)
            output: Tensor de salida (batch_size, seq_len, hidden_dim)
            
        Returns:
            Dict con métricas base:
                - output_norm: Norma de la salida
                - gradient_norm: Norma del gradiente
                - memory_usage: Uso de memoria
        """
        return {
            "output_norm": jnp.linalg.norm(output),
            "gradient_norm": jnp.linalg.norm(output - x),
            "memory_usage": jax.device_memory_allocated()
        }
        
    def _base_call(
        self,
        x: jnp.ndarray,
        training: bool = False,
        rng: Optional[jax.random.PRNGKey] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Llamada base con métricas.
        
        Args:
            x: Tensor de entrada
            training: Modo entrenamiento
            rng: Key aleatoria
            **kwargs: Argumentos adicionales
            
        Returns:
            Dict con output y métricas
        """
        if training and rng is None:
            raise ValueError("Se requiere rng en modo entrenamiento")
            
        # Aplicar dropout si es necesario
        if training and self.config.dropout_rate > 0:
            x = nn.Dropout(self.config.dropout_rate)(
                x, deterministic=False, rng=rng
            )
            
        # Calcular métricas
        metrics = self._base_metrics(x, x)
        
        return {
            "output": x,
            "metrics": metrics,
            "training": training
        }
        
    def __call__(
        self,
        x: jnp.ndarray,
        training: bool = False,
        rng: Optional[jax.random.PRNGKey] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Implementación de ILayer.
        
        Args:
            x: Tensor de entrada
            training: Modo entrenamiento
            rng: Key aleatoria
            **kwargs: Argumentos adicionales
            
        Returns:
            Dict con output y métricas
        """
        return self._base_call(x, training=training, rng=rng, **kwargs) """Capa base con métricas y utilidades comunes.

Esta capa sirve de punto de partida para todos los módulos de Capibara. Su
función principal es estandarizar la configuración y exponer utilidades para
seguimiento de métricas.

-----
Fórmulas
========
* **Norma L₂ de la salida**  
  :math:`\lVert y \rVert_2 = \sqrt{\sum_i y_i^2}`
* **Uso aproximado de memoria**  
  :math:`M \approx B \cdot S \cdot D \cdot \text{sizeof}(\text{dtype})`
  donde ``B`` es el *batch size*, ``S`` la longitud de secuencia y ``D`` la
  dimensión oculta.

-----
Parámetros
==========
config : LayerConfig
    Configuración compartida con la red. Ver :class:`LayerConfig`.

-----
Ejemplo
=======
>>> class MiCapa(BaseLayer):
>>>     def setup(self):
>>>         super().setup()
>>>         self.dense = nn.Dense(self.config.hidden_size)
>>>     def __call__(self, x, training=False, **kw):
>>>         x = self.dense(x)
>>>         return self._base_call(x, training=training, **kw)

"""