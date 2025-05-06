# Interfaces de CapibaraModel

## Descripción General

CapibaraModel utiliza un sistema de interfaces jerárquico para garantizar consistencia y compatibilidad entre componentes. Las interfaces principales son:

- `IModule`: Interfaz base para todos los módulos
- `ILayer`: Interfaz para capas neuronales
- `ISubModel`: Interfaz para submodelos especializados

## IModule

```python
class IModule(Protocol):
    """Interfaz base para todos los módulos."""
    
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> Union[jnp.ndarray, Tuple[jnp.ndarray, Dict[str, Any]]]:
        """
        Forward pass del módulo.
        
        Args:
            x: Tensor de entrada
            context: Tensor de contexto opcional
            training: Si estamos en modo entrenamiento
            **kwargs: Argumentos adicionales
            
        Returns:
            Tensor de salida o tupla (output, metrics)
        """
        pass
```

## ILayer

```python
class ILayer(IModule):
    """Interfaz para capas neuronales."""
    
    def _get_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas de la capa.
        
        Returns:
            Diccionario con métricas relevantes
        """
        pass
```

## ISubModel

```python
class ISubModel(IModule):
    """Interfaz para submodelos especializados."""
    
    def get_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración del submodelo.
        
        Returns:
            Diccionario con configuración
        """
        pass
```

## Uso

Todas las implementaciones deben:

1. Heredar explícitamente de la interfaz correspondiente
2. Implementar todos los métodos requeridos
3. Mantener la firma de métodos consistente
4. Documentar claramente el comportamiento

## Ejemplo

```python
class MiModulo(nn.Module, IModule):
    def __call__(self, x, context=None, training=False, **kwargs):
        # Implementación
        return output, metrics
``` 