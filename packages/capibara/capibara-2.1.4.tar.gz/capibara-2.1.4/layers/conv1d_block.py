"""Implementación de bloques convolucionales 1D.

Este módulo implementa diferentes tipos de convolución 1D con
documentación detallada de dimensiones y métricas unificadas.
"""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from typing import Dict, Any, Optional, Tuple, Literal # type: ignore
from capibara.interfaces.ilayer import ILayer 

class Conv1DBlock(nn.Module, ILayer):
    """
    Bloque convolucional 1D flexible y eficiente para secuencias.

    Conv1DBlock implementa diferentes variantes de convolución 1D:
      - Standard: Convolución tradicional para extracción de patrones locales.
      - Dilated: Convolución dilatada para ampliar el campo receptivo sin aumentar el coste computacional.
      - Separable: Convolución separable en profundidad para máxima eficiencia y reducción de parámetros.

    Este bloque es ideal para tareas de procesamiento de texto, audio o cualquier dato secuencial donde se requiera capturar dependencias locales y globales de manera eficiente.

    Características principales:
      - Soporte para dropout y normalización layer norm.
      - Métricas automáticas de campo receptivo, correlación de características y norma de gradiente.
      - Configuración flexible del tipo de convolución, tamaño de kernel y tasa de dilatación.

    Args:
        features (int): Número de características de salida.
        kernel_size (int): Tamaño del kernel de convolución.
        conv_type (str): Tipo de convolución ("standard", "dilated", "separable").
        dilation_rate (int): Tasa de dilatación (solo para "dilated").
        dropout_rate (float): Tasa de dropout.
        use_bias (bool): Si se usa bias en las convoluciones.

    Ejemplo de uso:
        >>> block = Conv1DBlock(features=128, kernel_size=3, conv_type="dilated", dilation_rate=2)
        >>> output = block(x, training=True, rng=key)

    Returns:
        Dict[str, Any]: Diccionario con:
            - "output": Tensor tras convolución y normalización.
            - "metrics": Métricas de campo receptivo, correlación y gradiente.
            - "training": Estado de entrenamiento.
    """
    features: int
    kernel_size: int
    conv_type: Literal["standard", "dilated", "separable"] = "standard"
    dilation_rate: int = 1
    dropout_rate: float = 0.1
    use_bias: bool = True

    @nn.compact
    def __call__(
        self,
        x: jnp.ndarray,
        training: bool = False,
        rng: Optional[jax.random.PRNGKey] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Aplica convolución 1D con métricas.
        
        Args:
            x: Tensor de entrada (batch_size, seq_len, channels)
            training: Modo de entrenamiento
            rng: Key aleatoria para dropout
            **kwargs: Argumentos adicionales
            
        Returns:
            Dict con:
                - output: Convolución aplicada
                - metrics: Métricas de convolución
                - training: Estado de entrenamiento
        """
        if training and rng is None:
            raise ValueError("Se requiere rng en modo entrenamiento")
            
        # Normalización
        x = nn.LayerNorm(name="norm")(x)
        
        # Convolución según tipo
        if self.conv_type == "standard":
            conv = nn.Conv(
                self.features,
                (self.kernel_size,),
                padding="SAME",
                use_bias=self.use_bias,
                name="conv"
            )
        elif self.conv_type == "dilated":
            conv = nn.Conv(
                self.features,
                (self.kernel_size,),
                padding="SAME",
                kernel_dilation=(self.dilation_rate,),
                use_bias=self.use_bias,
                name="conv"
            )
        else:  # separable
            # Convolución por canales
            depthwise = nn.Conv(
                x.shape[-1],
                (self.kernel_size,),
                padding="SAME",
                feature_group_count=x.shape[-1],
                use_bias=self.use_bias,
                name="depthwise"
            )
            # Convolución punto a punto
            pointwise = nn.Conv(
                self.features,
                (1,),
                padding="SAME",
                use_bias=self.use_bias,
                name="pointwise"
            )
            conv = lambda x: pointwise(depthwise(x))
            
        # Aplicar convolución
        output = conv(x)
        
        # Dropout en entrenamiento
        if training:
            output = nn.Dropout(self.dropout_rate)(output, deterministic=False, rng=rng)
            
        # Calcular métricas
        metrics = self._compute_metrics(x, output)
            
        return {
            "output": output,
            "metrics": metrics,
            "training": training
        }

    def _compute_metrics(
        self,
        x: jnp.ndarray,
        output: jnp.ndarray
    ) -> Dict[str, jnp.ndarray]:
        """Calcula métricas de convolución.
        
        Args:
            x: Tensor de entrada
            output: Tensor de salida
            
        Returns:
            Dict con métricas:
                - receptive_field: Campo receptivo efectivo
                - feature_correlation: Correlación entre características
                - gradient_norm: Norma del gradiente
        """
        # Campo receptivo efectivo
        if self.conv_type == "dilated":
            receptive_field = self.kernel_size * self.dilation_rate
        else:
            receptive_field = self.kernel_size
            
        # Correlación entre características
        feature_correlation = jnp.mean(
            jnp.corrcoef(output.reshape(-1, self.features), rowvar=False)
        )
        
        # Norma del gradiente
        gradient_norm = jnp.linalg.norm(output - x, axis=-1).mean(axis=-1)
        
        return {
            "receptive_field": jnp.array(receptive_field),
            "feature_correlation": feature_correlation,
            "gradient_norm": gradient_norm
        } 