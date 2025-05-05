"""
MetaLA layer implementation for CapibaraModel.

Meta Learning Attention with dynamic decay, using a scan-based approach
for sequence processing. This version includes improved shape handling,
broadcasting for alpha, and checks to ensure dimension consistency.
"""

import jax  # type: ignore
import jax.numpy as jnp  # type: ignore
from flax import linen as nn  # type: ignore
import logging
from typing import Tuple, Optional, Any, Dict, Union

from interfaces.ilayer import ILayer
from layers.base import BaseLayer, LayerConfig

logger = logging.getLogger(__name__)

class MetaLAConfig(LayerConfig):
    """Configuración específica para MetaLA.
    
    Args:
        num_heads: Número de cabezas de atención
        decay_rate: Tasa de decay para atención
        auto_augment: Si True, activa auto-augment
    """
    num_heads: int = 8
    decay_rate: float = 0.9
    auto_augment: bool = True

class MetaLA(BaseLayer, ILayer):
    """
    Meta Learning Attention with dynamic decay.
    Implementa atención con decay dinámico y auto-augmentación.
    
    Ejemplos:
        >>> config = MetaLAConfig(hidden_size=512, num_heads=8)
        >>> layer = MetaLA(config)
        >>> output = layer(x, training=True)  # Modo entrenamiento
        >>> output = layer(x)  # Modo inferencia
    
    Args:
        hidden_size: Dimensión del espacio oculto (batch, seq_len, hidden_size)
        num_heads: Número de cabezas de atención
        decay_rate: Tasa de decay para atención
        auto_augment: Si True, activa auto-augment
    """
    config: MetaLAConfig

    def setup(self):
        """Initialize model parameters and sublayers."""
        super().setup()
        
        # Proyecciones
        self.q_proj = nn.Dense(
            self.config.hidden_size * self.config.num_heads,
            name="q_proj"
        )
        self.k_proj = nn.Dense(
            self.config.hidden_size * self.config.num_heads,
            name="k_proj"
        )
        self.v_proj = nn.Dense(
            self.config.hidden_size * self.config.num_heads,
            name="v_proj"
        )
        
        # Parámetros de decay
        self.decay = self.param(
            "decay",
            nn.initializers.constant(self.config.decay_rate),
            (self.config.num_heads,)
        )
        
        # Escala de atención
        self.scale = 1.0 / jnp.sqrt(self.config.hidden_size)
        
        # 1) Confirm dimension match if desired:
        if self.config.num_heads * self.head_dim != self.config.hidden_size:
            logger.warning(
                f"MetaLA: num_heads * head_dim = {self.config.num_heads * self.head_dim} "
                f"which does not match hidden_size={self.config.hidden_size}. "
                "Consider adding a linear mapping or adjusting dims."
            )

        # Final projection back to hidden_size
        self.to_out = nn.Dense(self.config.hidden_size)

        # Auxiliary layers
        self.norm = nn.LayerNorm()
        self.dropout = nn.Dropout(rate=self.dropout_rate)

    def _apply_attention(
        self,
        q: jnp.ndarray,
        k: jnp.ndarray,
        v: jnp.ndarray
    ) -> Tuple[jnp.ndarray, jnp.ndarray]:
        """Aplica atención con decay dinámico."""
        def update_state_attn(carry, index):
            k_i = k[index]
            v_i = v[index]
            q_i = q[index]
            
            attn_weights = jax.nn.softmax(
                jnp.einsum('bhd,bhd->bh', q_i, k_i) * self.scale
            )[..., None]
            
            new_state = (
                self.decay[None, :, None] * carry + 
                (1 - self.decay[None, :, None]) * (attn_weights * v_i)
            )
            
            return new_state, attn_weights
            
        init_state = jnp.zeros_like(v[0])
        final_state, attn_weights = jax.lax.scan(
            update_state_attn,
            init_state,
            jnp.arange(q.shape[0])
        )
        
        return final_state, attn_weights

    def _auto_augment(self, x: jnp.ndarray) -> jnp.ndarray:
        """Aplica auto-augment si está activado.
        
        Args:
            x: Tensor de entrada
            
        Returns:
            Tensor aumentado
        """
        if not self.config.auto_augment:
            return x
            
        # Aumentación basada en ruido
        noise = jax.random.normal(
            self.make_rng("augment"),
            shape=x.shape
        ) * 0.1
        
        return x + noise

    def __call__(
        self,
        x: jnp.ndarray,
        training: bool = False,
        rng: Optional[jax.random.PRNGKey] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Forward pass para MetaLA.

        Args:
            x: Tensor de entrada shape (batch_size, seq_len, hidden_size)
            training: Si estamos en modo entrenamiento
            rng: Key aleatoria para dropout y auto-augment
        
        Returns:
            Dict con:
                - output: Tensor procesado (batch_size, seq_len, hidden_size)
                - metrics: Dict con métricas de ejecución
                - attention_weights: Pesos de atención si training=True
        """
        try:
            if x.ndim != 3:
                raise ValueError(
                    f"MetaLA espera entrada 3D (batch, seq_len, hidden_size), recibido: {x.shape}"
                )

            batch_size, seq_len, dim = x.shape
            if dim != self.config.hidden_size:
                raise ValueError(
                    f"Dimensión de entrada {dim} debe coincidir con hidden_size {self.config.hidden_size}"
                )

            # Auto-augment
            x = self._auto_augment(x)
            
            # Proyecciones
            q = self.q_proj(x)
            k = self.k_proj(x)
            v = self.v_proj(x)
            
            # Reshape para atención
            q = q.reshape(batch_size, seq_len, self.config.num_heads, self.head_dim)
            k = k.reshape(batch_size, seq_len, self.config.num_heads, self.head_dim)
            v = v.reshape(batch_size, seq_len, self.config.num_heads, self.head_dim)
            
            # Aplicar atención
            attn_output, attn_weights = self._apply_attention(q, k, v)
            
            # Reshape final
            output = attn_output.reshape(batch_size, seq_len, -1)
            
            # Proyección final
            output = self.to_out(output)

            # Normalización + dropout
            output = self.norm(output)
            if training:
                output = self.dropout(output, deterministic=not training)

            # Métricas
            metrics = {
                "input_shape": x.shape,
                "output_shape": output.shape,
                "num_heads": self.config.num_heads,
                "head_dim": self.head_dim,
                "decay_mean": jnp.mean(self.decay),
                "attention_norm": jnp.linalg.norm(attn_weights)
            }

            result = {
                "output": output,
                "metrics": metrics
            }
            
            if training:
                result["attention_weights"] = attn_weights

            return result

        except Exception as e:
            logger.error(f"Error en MetaLA: {str(e)}")
            raise
