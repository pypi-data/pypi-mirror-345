"""
Contextual Router Module for CapibaraGPT

Combina activación contextual y enrutamiento cuántico
para decidir si se activa CapibaraQuantumRouter dinámicamente.
"""

from typing import Optional
from flax import linen as nn #type: ignore
import jax.numpy as jnp#type: ignore
import logging

from .contextual_activation import ContextualActivation, ContextualConfig 
from .capibara_quantum_router import CapibaraQuantumRouter
from config import CapibaraConfig

logger = logging.getLogger(__name__)

class ContextualRouter(nn.Module):
    """
    Enrutador contextual que decide dinámicamente si activar el router cuántico.
    """
    config: CapibaraConfig
    hidden_size: int
    total_vqbits: int

    def setup(self):
        # Módulo de activación contextual con atención y umbral dinámico
        self.activation_module = ContextualActivation(ContextualConfig(
            hidden_size=self.hidden_size,
            num_heads=4,
            initial_threshold=0.4,
            dropout_rate=0.1,
            use_attention=True,
            dynamic_threshold=True
        ))

        # Router cuántico con VQbits dinámicos y preentrenados
        self.quantum_router = CapibaraQuantumRouter(
            config=self.config.quantum_vqbit_config,
            total_vqbits=self.total_vqbits,
            hidden_size=self.hidden_size
        )

    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False
    ) -> jnp.ndarray:
        """
        Decide si enrutar por QuantumRouter o pasar la entrada sin modificar.
        """
        if context is None:
            logger.warning("⚠️ No se proporcionó contexto. Se omite activación cuántica.")
            return x
        
        activation_result = self.activation_module(x, context, training=training)
        is_active = activation_result["is_active"]

        if jnp.mean(is_active) > 0.5:
            logger.info("✅ Activando CapibaraQuantumRouter según contexto.")
            return self.quantum_router(x, context, training=training)
        else:
            logger.info("🛑 Contexto no relevante. Ruta directa sin transformación cuántica.")
            return x
