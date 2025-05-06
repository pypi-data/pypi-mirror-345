"""
Módulo de gestión de personalidad para CapibaraModel.

Adjusts the output based on a set of personality traits, combining
text encoding with trait vectors.
"""

import jax  # type: ignore
import jax.numpy as jnp  # type: ignore
from flax import linen as nn  # type: ignore
import logging
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field
from jax.experimental import debugger #type: ignore

from capibara_model.interfaces.imodules import IModule, ModuleOutput # type: ignore
from capibara_model.modules.personality.contextual_activation import ContextualActivation, ContextualConfig
from capibara_model.core.optimizer import distributed_jit, MODEL_SHARDING, REPLICATED

logger = logging.getLogger(__name__)

class PersonalityConfig(BaseModel):
    """Configuración del módulo de personalidad."""
    hidden_size: int = Field(default=256, gt=0)
    num_heads: int = Field(default=8, gt=0)
    num_traits: int = Field(default=4, gt=0)
    dropout_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    activation_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    score_network_size: int = Field(default=128, gt=0)
    trait_initialization_std: float = Field(default=0.02, gt=0.0)

class PersonalityManager(nn.Module, IModule):
    """
    Adjusts responses based on personality traits.

    Attributes:
        config (PersonalityConfig): Configuration for the module.
    """
    config: PersonalityConfig

    def setup(self):
        """Initialize encoding layers, trait parameters, and an activation module."""
        # Encoding layers
        self.text_encoder = nn.Dense(self.config.hidden_size)
        self.trait_encoder = nn.Dense(self.config.hidden_size)

        # Trainable traits
        self.traits = self.param(
            'traits',
            nn.initializers.normal(self.config.trait_initialization_std),
            (self.config.num_traits, self.config.hidden_size)
        )

        # Adjustment network
        self.adjustment_network = nn.Sequential([
            nn.Dense(self.config.score_network_size),
            nn.relu,
            nn.Dropout(self.config.dropout_rate),
            nn.Dense(self.config.hidden_size),
            nn.LayerNorm(),
            nn.Dense(self.config.hidden_size)
        ])

        # Contextual activation
        activation_config = ContextualConfig(
            hidden_size=self.config.hidden_size,
            num_heads=self.config.num_heads,
            initial_threshold=self.config.activation_threshold,
            dropout_rate=self.config.dropout_rate
        )
        self.activation = ContextualActivation(config=activation_config)

        # Auxiliary layers
        self.norm = nn.LayerNorm()
        self.dropout = nn.Dropout(rate=self.config.dropout_rate)

    def _expand_traits(self, traits: jnp.ndarray, batch_size: int, seq_len: int) -> jnp.ndarray:
        """
        Expande los rasgos para que coincidan con las dimensiones del texto.
        
        Args:
            traits: Tensor de forma (num_traits, hidden_size)
            batch_size: Tamaño del batch del texto
            seq_len: Longitud de secuencia del texto
            
        Returns:
            Tensor expandido de forma (batch_size, seq_len, hidden_size)
        """
        # Promedio de rasgos para cada posición de secuencia
        traits_mean = jnp.mean(traits, axis=0)  # (hidden_size,)
        
        # Expandir a las dimensiones necesarias
        traits_expanded = jnp.tile(
            traits_mean[None, None, :],  # (1, 1, hidden_size)
            (batch_size, seq_len, 1)     # Expandir a (batch_size, seq_len, hidden_size)
        )
        
        return traits_expanded

    def _apply_personality(
        self,
        x: jnp.ndarray,
        traits: jnp.ndarray,
        training: bool = False
    ) -> Dict[str, jnp.ndarray]:
        """
        Apply personality traits to the input x.

        Args:
            x (jnp.ndarray): shape (batch, seq_len, hidden_size).
            traits (jnp.ndarray): shape (num_traits, hidden_size) or (batch, seq_len, hidden_size).
            training (bool): Whether in training mode.

        Returns:
            Dict with:
              - 'output': The final adjusted output,
              - 'traits': The encoded trait vectors,
              - 'activation_score': Score from ContextualActivation,
              - 'is_activated': Boolean mask from ContextualActivation,
              - 'is_active': Final activation state
        """
        # Encode input
        x_enc = self.text_encoder(x)
        
        # Expand traits if needed
        if traits.ndim == 2:  # (num_traits, hidden_size)
            traits = self._expand_traits(traits, x.shape[0], x.shape[1])
        
        t_enc = self.trait_encoder(traits)

        # Norm + dropout
        x_enc = self.norm(x_enc)
        t_enc = self.norm(t_enc)
        if training:
            x_enc = self.dropout(x_enc, deterministic=not training)
            t_enc = self.dropout(t_enc, deterministic=not training)

        # Contextual activation between x_enc and t_enc
        activation_out = self.activation(x_enc, t_enc, training)
        activation_score = activation_out["score"]
        is_activated = activation_out["is_active"]

        # Combine features
        combined = jnp.concatenate([
            x_enc,
            t_enc,
            x_enc * t_enc,
            activation_score[..., None]  # Add activation score as feature
        ], axis=-1)

        # Calculate adjusted output
        adjusted = self.adjustment_network(combined)
        
        # Final activation depends on both adjustment quality and contextual activation
        adjustment_score = jnp.mean(adjusted, axis=-1)
        is_adjusted = adjustment_score > self.config.activation_threshold
        is_active = jnp.logical_and(is_activated, is_adjusted)

        return {
            'output': adjusted,
            'traits': t_enc,
            'activation_score': activation_score,
            'is_activated': is_activated,
            'adjustment_score': adjustment_score,
            'is_adjusted': is_adjusted,
            'is_active': is_active
        }

    @distributed_jit(in_specs=MODEL_SHARDING, out_specs=REPLICATED)
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> ModuleOutput:
        """
        Forward pass for personality adjustment.

        Args:
            x (jnp.ndarray): shape (batch, seq_len, hidden_size).
            context (jnp.ndarray, optional): If None, uses self.traits param.
            training (bool): Whether in training mode.
            **kwargs: Additional arguments.

        Returns:
            ModuleOutput with results and metrics
        """
        with debugger.breakpoint_on_error():
            try:
                logger.debug(f"Input shape: x={x.shape}")
                
                # Validate input
                if x.ndim != 3:
                    raise ValueError(f"Expected 3D input, got shape {x.shape}")

                # Use default traits if no context provided
                traits = context if context is not None else self.traits
                
                # Apply personality
                result = self._apply_personality(x, traits, training)

                # Calculate metrics
                metrics = {
                    'activation_mean': jnp.mean(result['activation_score']),
                    'activation_std': jnp.std(result['activation_score']),
                    'adjustment_mean': jnp.mean(result['adjustment_score']),
                    'adjustment_std': jnp.std(result['adjustment_score']),
                    'is_activated_ratio': jnp.mean(result['is_activated']),
                    'is_adjusted_ratio': jnp.mean(result['is_adjusted']),
                    'is_active_ratio': jnp.mean(result['is_active']),
                    'trait_norm': jnp.linalg.norm(result['traits'])
                }

                logger.debug(f"Output shape: {result['output'].shape}")
                
                return {
                    "output": x,  # Mantenemos la entrada original
                    "is_active": result['is_active'],
                    "score": result['adjustment_score'],
                    "metrics": metrics
                }

            except Exception as e:
                logger.error(f"Error en PersonalityManager: {str(e)}")
                raise
