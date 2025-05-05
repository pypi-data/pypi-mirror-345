# capibara_model/interfaces/ilayers.py
from abc import ABC, abstractmethod
import jax.numpy as jnp # type: ignore
from typing import Protocol
from typing_extensions import runtime_checkable

@runtime_checkable
class ILayer(Protocol):
    """
    Interfaz (clase abstracta) para las capas de la arquitectura.
    Cada capa que la implemente debe definir su método __call__,
    indicando cómo procesa los tensores de entrada.
    """

    @abstractmethod
    def __call__(
        self, 
        x: jnp.ndarray, 
        training: bool = False, 
        **kwargs
    ) -> jnp.ndarray:
        """
        Lógica de la capa para transformar la entrada x.

        Args:
            x: Tensor de entrada, p. ej. (batch, seq_len, hidden_size).
            training: True si estamos en modo entrenamiento (dropout, etc.).
            **kwargs: Parámetros adicionales que pudieran ser necesarios.

        Returns:
            Un tensor transformado, típicamente de la misma forma que x
            (o adaptado según la operación de la capa).
        """
        pass
# capibara_model/interfaces/imodules.py
from abc import ABC, abstractmethod
import jax.numpy as jnp
from typing import Optional, Dict, Any

class IModule(ABC):
    """
    Interfaz abstracta para módulos en CapibaraModel.
    Los módulos pueden procesar la salida 'x' de capas/submodelos,
    y opcionalmente un 'context', y devuelven un dict con resultados,
    o un tensor, según el uso que les quieras dar.
    """

    @abstractmethod
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> Dict[str, jnp.ndarray]:
        """
        Lógica de procesamiento del módulo.

        Args:
            x (jnp.ndarray): El tensor principal, p. ej. (batch, seq_len, hidden_size).
            context (Optional[jnp.ndarray]): Contexto adicional o de cross-attention, si aplica.
            training (bool): Si estamos en modo entrenamiento (dropout, etc.).
            **kwargs (Any): Parámetros adicionales que el módulo pueda necesitar.

        Returns:
            Dict[str, jnp.ndarray]: Un diccionario con resultados. Por ejemplo:
                {
                    "output": <tensor principal transformado>,
                    "is_active": <indicador binario>,
                    "score": <valor de coherencia>,
                    ...
                }

        Nota: Podrías en lugar de un dict retornar solo un tensor, pero 
        muchos módulos generan más de un valor, así que un dict es flexible.
        """
        pass
