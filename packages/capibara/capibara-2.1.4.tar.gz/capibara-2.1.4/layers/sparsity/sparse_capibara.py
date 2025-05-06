"""Implementación de SparseCapibara con esparsidad dinámica.

Este módulo implementa diferentes tipos de esparsidad con tracking
de métricas y soporte para cuantización.
"""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from typing import Dict, Any, Optional, Tuple, Literal, List # type: ignore
from interfaces.ilayer import ILayer # type: ignore

class SparseCapibara(nn.Module, ILayer):
    """
    Capa de esparsidad dinámica configurable para arquitecturas profundas.

    Esta capa implementa esparsidad neuronal, estructurada o no estructurada, permitiendo controlar la densidad de activación de las neuronas o patrones. Incluye adaptación dinámica del umbral de esparsidad y soporte opcional para cuantización de pesos/salidas.

    Tipos de esparsidad soportados
    -----------------------------
    - **Neuronal:** Apaga neuronas según su importancia media.
    - **Estructurada:** Aplica patrones fijos de esparsidad.
    - **No estructurada:** Máscara libre sobre la activación.

    Fórmulas relevantes
    -------------------
    - **Importancia de neuronas:**  
      :math:`I_j = \\frac{1}{N} \sum_{i=1}^N |x_{ij}|`
    - **Umbral adaptativo:**  
      :math:`\\tau_{t+1} = (1-\eta)\\tau_t + \eta \cdot \\text{percentil}(I, 1-\rho)`
      donde :math:`\eta` es la tasa de adaptación y :math:`\rho` el objetivo de esparsidad.

    Parámetros
    ----------
    hidden_size : int
        Dimensión del espacio oculto.
    sparsity_type : {'neuronal', 'structured', 'unstructured'}
        Tipo de esparsidad a aplicar.
    sparsity_target : float
        Proporción objetivo de activación (0-1).
    sparsity_adaptation : float
        Tasa de adaptación del umbral.
    use_quantization : bool
        Si se activa, cuantiza la salida.
    quant_bits : int
        Número de bits para cuantización.
    dropout_rate : float
        Tasa de dropout.

    Métricas devueltas
    ------------------
    - sparsity_level
    - quantization_error
    - output_norm

    Ejemplo
    -------
    >>> capa = SparseCapibara(hidden_size=256, sparsity_type="neuronal", sparsity_target=0.7)
    >>> out = capa(x, training=True, rng=key)
    """
    hidden_size: int
    sparsity_type: Literal["neuronal", "structured", "unstructured"] = "neuronal"
    sparsity_target: float = 0.5
    sparsity_adaptation: float = 0.01
    use_quantization: bool = False
    quant_bits: int = 8
    dropout_rate: float = 0.1

    def setup(self):
        """Inicializa parámetros y variables."""
        # Inicializar threshold para esparsidad neuronal
        if self.sparsity_type == "neuronal":
            self.threshold = self.variable(
                "sparsity",
                "threshold",
                lambda: jnp.array(0.0)
            )
            
        # Inicializar máscara para esparsidad no estructurada
        if self.sparsity_type == "unstructured":
            self.mask = self.variable(
                "sparsity",
                "mask",
                lambda: jnp.ones((self.hidden_size,))
            )

    @nn.compact
    def __call__(
        self,
        x: jnp.ndarray,
        training: bool = False,
        rng: Optional[jax.random.PRNGKey] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Aplica esparsidad dinámica con métricas.
        
        Args:
            x: Tensor de entrada (batch_size, seq_len, hidden_dim)
            training: Modo de entrenamiento
            rng: Key aleatoria para dropout
            **kwargs: Argumentos adicionales
            
        Returns:
            Dict con:
                - output: Salida esparsa
                - metrics: Métricas de esparsidad
                - training: Estado de entrenamiento
        """
        if training and rng is None:
            raise ValueError("Se requiere rng en modo entrenamiento")
            
        # Normalización
        x = nn.LayerNorm(name="norm")(x)
        
        # Proyección
        x = nn.Dense(self.hidden_size, name="projection")(x)
        
        # Aplicar esparsidad
        x, mask = self._apply_sparsity(x, training)
        
        # Cuantización opcional
        if self.use_quantization:
            x = self._quantize(x)
        
        # Dropout en entrenamiento
        if training:
            x = nn.Dropout(self.dropout_rate)(x, deterministic=False, rng=rng)
            
        # Calcular métricas
        metrics = self._compute_metrics(x, mask)
            
        return {
            "output": x,
            "metrics": metrics,
            "training": training
        }

    def _apply_sparsity(
        self,
        x: jnp.ndarray,
        training: bool
    ) -> Tuple[jnp.ndarray, jnp.ndarray]:
        """Aplica esparsidad según tipo.
        
        Args:
            x: Tensor de entrada
            training: Modo de entrenamiento
            
        Returns:
            Tuple con:
                - Tensor esparso
                - Máscara de esparsidad
        """
        if self.sparsity_type == "neuronal":
            return self._neuronal_sparsity(x, training)
        elif self.sparsity_type == "structured":
            return self._structured_sparsity(x, training)
        else:
            return self._unstructured_sparsity(x, training)

    def _neuronal_sparsity(
        self,
        x: jnp.ndarray,
        training: bool
    ) -> Tuple[jnp.ndarray, jnp.ndarray]:
        """Esparsidad a nivel de neuronas.
        
        Args:
            x: Tensor de entrada
            training: Modo de entrenamiento
            
        Returns:
            Tuple con tensor y máscara
        """
        # Calcular importancia de neuronas
        importance = jnp.mean(jnp.abs(x), axis=0)
        
        # Actualizar threshold
        if training:
            new_threshold = jnp.percentile(
                importance,
                100 * (1 - self.sparsity_target)
            )
            self.threshold.value = (
                (1 - self.sparsity_adaptation) * self.threshold.value +
                self.sparsity_adaptation * new_threshold
            )
            
        # Aplicar máscara
        mask = importance > self.threshold.value
        return x * mask, mask

    def _structured_sparsity(
        self,
        x: jnp.ndarray,
        training: bool
    ) -> Tuple[jnp.ndarray, jnp.ndarray]:
        """Esparsidad estructurada.
        
        Args:
            x: Tensor de entrada
            training: Modo de entrenamiento
            
        Returns:
            Tuple con tensor y máscara
        """
        # Patrones de esparsidad
        patterns = self.param(
            "patterns",
            nn.initializers.lecun_normal(),
            (self.hidden_size // 4, self.hidden_size)
        )
        
        # Aplicar patrones
        mask = jnp.any(patterns > 0, axis=0)
        return x * mask, mask

    def _unstructured_sparsity(
        self,
        x: jnp.ndarray,
        training: bool
    ) -> Tuple[jnp.ndarray, jnp.ndarray]:
        """Esparsidad no estructurada.
        
        Args:
            x: Tensor de entrada
            training: Modo de entrenamiento
            
        Returns:
            Tuple con tensor y máscara
        """
        # Actualizar máscara
        if training:
            new_mask = jax.random.bernoulli(
                self.make_rng("sparsity"),
                p=1-self.sparsity_target,
                shape=(self.hidden_size,)
            )
            self.mask.value = (
                (1 - self.sparsity_adaptation) * self.mask.value +
                self.sparsity_adaptation * new_mask
            )
            
        return x * self.mask.value, self.mask.value

    def _quantize(self, x: jnp.ndarray) -> jnp.ndarray:
        """Aplica cuantización.
        
        Args:
            x: Tensor a cuantizar
            
        Returns:
            Tensor cuantizado
        """
        scale = (2 ** (self.quant_bits - 1)) - 1
        return jnp.round(x * scale) / scale

    def _compute_metrics(
        self,
        x: jnp.ndarray,
        mask: jnp.ndarray
    ) -> Dict[str, jnp.ndarray]:
        """Calcula métricas de esparsidad.
        
        Args:
            x: Tensor esparso
            mask: Máscara de esparsidad
            
        Returns:
            Dict con métricas:
                - sparsity_level: Nivel de esparsidad
                - masked_values: Histograma de valores enmascarados
                - importance_dist: Distribución de importancia
        """
        # Nivel de esparsidad
        sparsity_level = 1 - jnp.mean(mask)
        
        # Histograma de valores enmascarados
        masked_values = jnp.histogram(
            x * (1 - mask),
            bins=10,
            range=(-1, 1)
        )[0]
        
        # Distribución de importancia
        importance_dist = jnp.mean(jnp.abs(x), axis=0)
        
        return {
            "sparsity_level": sparsity_level,
            "masked_values": masked_values,
            "importance_dist": importance_dist
        }

class SparseConvCapibara(SparseCapibara):
    """
    Versión convolucional de SparseCapibara.
    
    Extiende SparseCapibara con soporte para convoluciones
    y esparsidad en el dominio espacial.
    """
    kernel_size: int
    conv_type: Literal["standard", "dilated", "separable"] = "standard"
    dilation_rate: int = 1

    def setup(self):
        """Inicializa parámetros y variables."""
        super().setup()
        
        # Inicializar convolución
        if self.conv_type == "standard":
            self.conv = nn.Conv(
                self.hidden_size,
                (self.kernel_size,),
                padding="SAME",
                name="conv"
            )
        elif self.conv_type == "dilated":
            self.conv = nn.Conv(
                self.hidden_size,
                (self.kernel_size,),
                padding="SAME",
                kernel_dilation=(self.dilation_rate,),
                name="conv"
            )
        else:
            # Separable
            self.depthwise = nn.Conv(
                self.hidden_size,
                (self.kernel_size,),
                padding="SAME",
                feature_group_count=self.hidden_size,
                name="depthwise"
            )
            self.pointwise = nn.Conv(
                self.hidden_size,
                (1,),
                padding="SAME",
                name="pointwise"
            )

    def _apply_sparsity(
        self,
        x: jnp.ndarray,
        training: bool
    ) -> Tuple[jnp.ndarray, jnp.ndarray]:
        """Aplica esparsidad convolucional.
        
        Args:
            x: Tensor de entrada
            training: Modo de entrenamiento
            
        Returns:
            Tuple con tensor y máscara
        """
        # Aplicar convolución
        if self.conv_type == "separable":
            x = self.pointwise(self.depthwise(x))
        else:
            x = self.conv(x)
        
        # Aplicar esparsidad
        return super()._apply_sparsity(x, training)