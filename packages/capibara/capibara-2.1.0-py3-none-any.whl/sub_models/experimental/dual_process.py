"""Módulo de Pensamiento Dual Procesado - Versión Altamente Optimizada"""

from typing import Dict, Any, Tuple, Optional
import jax #type: ignore
import jax.numpy as jnp #type: ignore
from flax import linen as nn #type: ignore
from flax.struct import dataclass #type: ignore
from interfaces.isub_models import ISubModel #type: ignore

@dataclass
class System2State:
    """Estado del Sistema 2 para procesamiento iterativo."""
    representation: jnp.ndarray
    steps_taken: jnp.ndarray

class DualProcessThinkingFinal(nn.Module, ISubModel):
    """Versión optimizada final con:
    - Cálculo correcto de importancia
    - Uso eficiente de capas LayerNorm
    - Código limpio sin importaciones innecesarias
    - Configuración precisa de dimensionalidad
    """
    
    hidden_size: int = 512
    max_system2_cycles: int = 6
    activation_threshold: float = 0.35
    num_system1_heads: int = 2
    num_system2_heads: int = 8
    dropout_rate: float = 0.1

    def setup(self):
        # System 1 - Componentes
        self.s1_attn = nn.MultiHeadDotProductAttention(
            num_heads=self.num_system1_heads,
            dropout_rate=self.dropout_rate
        )
        self.s1_norm = nn.LayerNorm()
        
        # System 2 - Componentes
        self.s2_attn = nn.MultiHeadDotProductAttention(
            num_heads=self.num_system2_heads,
            dropout_rate=self.dropout_rate
        )
        self.s2_mlp = self._build_mlp()
        self.s2_norm1 = nn.LayerNorm()
        self.s2_norm2 = nn.LayerNorm()
        
        # Proyección de importancia
        self.importance_proj = nn.Dense(1)

    def _build_mlp(self) -> nn.Module:
        """Construye el MLP con dropout configurado correctamente."""
        return nn.Sequential([
            nn.Dense(self.hidden_size * 4),
            nn.gelu,
            nn.Dropout(rate=self.dropout_rate),
            nn.Dense(self.hidden_size)
        ])

    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Procesamiento dual con dimensionalidad corregida."""
        # System 1 - Procesamiento rápido
        x = self.s1_norm(x + self.s1_attn(
            inputs_q=x,
            inputs_kv=x,
            deterministic=not training
        ))
        
        # Cálculo de importancia corregido
        importance = self._compute_importance(x)
        use_system2 = importance > self.activation_threshold
        
        # System 2 - Procesamiento condicional
        x, steps = self._process_conditionally(x, use_system2, training)
        
        return {
            "output": x,
            "metrics": self._collect_metrics(importance, use_system2, steps)
        }

    def _compute_importance(self, x: jnp.ndarray) -> jnp.ndarray:
        """Cálculo corregido de importancia."""
        pooled = jnp.mean(x, axis=1)  # (batch_size, hidden_size)
        importance = jax.nn.sigmoid(self.importance_proj(pooled))
        return importance.squeeze(-1)  # (batch_size,)

    def _process_conditionally(self, x: jnp.ndarray, mask: jnp.ndarray,
                             training: bool) -> Tuple[jnp.ndarray, jnp.ndarray]:
        """Procesamiento condicional optimizado con LayerNorm correcto."""
        def system2_step(carry, _):
            state = carry
            attn_out = self.s2_attn(
                inputs_q=state.representation[None],
                inputs_kv=state.representation[None],
                deterministic=not training
            )[0]
            x_i = self.s2_norm1(state.representation + attn_out)
            
            mlp_out = self.s2_mlp(x_i[None], training=training)[0]
            x_i = self.s2_norm2(x_i + mlp_out)
            
            return System2State(x_i, state.steps_taken + 1), None
        
        def process_element(x_i, active_i):
            initial_state = System2State(x_i, jnp.array(0, dtype=jnp.int32))
            final_state, _ = jax.lax.cond(
                active_i,
                lambda: jax.lax.scan(
                    system2_step,
                    initial_state,
                    None,
                    length=self.max_system2_cycles
                ),
                lambda: (initial_state, None)
            )
            return final_state.representation, final_state.steps_taken
        
        return jax.vmap(process_element)(x, mask)

    def _collect_metrics(self, importance: jnp.ndarray,
                        use_system2: jnp.ndarray,
                        steps: jnp.ndarray) -> Dict[str, jnp.ndarray]:
        """Métricas mejoradas."""
        return {
            "importance": importance,
            "system2_activated": use_system2.astype(jnp.float32),
            "system2_steps": steps.astype(jnp.float32),
            "compute_savings": 1 - jnp.mean(use_system2),
            "avg_steps": jnp.mean(steps),
            "max_importance": jnp.max(importance),
            "min_importance": jnp.min(importance)
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del modelo."""
        return {
            "model_type": "dual_process_final",
            "hidden_size": self.hidden_size,
            "max_system2_cycles": self.max_system2_cycles,
            "activation_threshold": self.activation_threshold
        }

    def validate_input(self, x: jnp.ndarray) -> None:
        """Valida el formato de entrada."""
        if x.ndim != 3:
            raise ValueError(f"La entrada debe ser 3D (batch, seq_len, dim), se obtuvo {x.ndim}D")
        if x.shape[-1] != self.hidden_size:
            raise ValueError(f"La dimensión de entrada debe ser {self.hidden_size}, se obtuvo {x.shape[-1]}") 