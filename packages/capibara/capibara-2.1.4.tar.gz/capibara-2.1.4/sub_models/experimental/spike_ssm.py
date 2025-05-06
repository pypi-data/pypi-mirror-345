"""
Spike-SSM implementation for CapibaraModel.

This module defines a spiking state-space model (SSM) that processes
sequential data with spiking neurons. It maintains a hidden state,
a membrane voltage, and spike indicators for each timestep.
"""

import jax  # type: ignore
import jax.numpy as jnp  # type: ignore
from flax import linen as nn  # type: ignore
import logging
from typing import NamedTuple, Tuple, Optional, Dict, Any, Union
from pydantic import BaseModel, Field #type: ignore
from interfaces.isub_models import ISubModel
from functools import partial

logger = logging.getLogger(__name__)

class SpikeState(NamedTuple):
    """
    State for a spiking neuron.

    Attributes:
        hidden (jnp.ndarray): Hidden state of shape (batch, hidden_size).
        voltage (jnp.ndarray): Membrane voltage of shape (batch, hidden_size).
        spikes (jnp.ndarray): Spike indicators of shape (batch, hidden_size).
    """
    hidden: jnp.ndarray
    voltage: jnp.ndarray
    spikes: jnp.ndarray


class SpikeSSMConfig(BaseModel):
    hidden_size: int = Field(..., gt=0)
    tau: float = Field(default=10.0, gt=0)
    threshold: float = Field(default=1.0)
    reset_value: float = Field(default=0.0)
    dropout_rate: float = Field(default=0.1, ge=0, lt=1)


class SpikeSSM(nn.Module, ISubModel):
    """
    Modelo de espacio de estados con neuronas spiking (SSM).
    
    Parámetros:
        hidden_size (int): Dimensión del estado oculto
        tau (float): Constante de tiempo para actualización (>0)
        threshold (float): Umbral de voltaje para generación de spikes
        reset_value (float): Valor de reset post-spike
        dropout_rate (float): Tasa de dropout (0-1)
    
    Ejemplo:
        model = SpikeSSM(hidden_size=64, tau=10.0)
        output = model(input_sequence)
    """
    hidden_size: int
    tau: float = 10.0
    threshold: float = 1.0
    reset_value: float = 0.0
    dropout_rate: float = 0.1

    def setup(self):
        """
        Initialize the sub-layers:
          - input_proj: transforms the input at each timestep
          - hidden_proj: transforms the hidden state from the previous timestep
          - output: final projection of the spiking outputs
        """
        self.input_proj = nn.Dense(self.hidden_size)
        self.hidden_proj = nn.Dense(self.hidden_size)
        self.output = nn.Dense(self.hidden_size)

        # Aux layers
        self.norm = nn.LayerNorm()
        self.dropout = nn.Dropout(rate=self.dropout_rate)

    @partial(jax.jit, static_argnums=(0,))
    def _spike_step(
        self,
        x: jnp.ndarray,
        state: SpikeState,
        training: bool = False
    ) -> Tuple[jnp.ndarray, SpikeState]:
        """
        Single spiking step update.

        Args:
            x (jnp.ndarray): shape (batch, hidden_size) for this timestep's input.
            state (SpikeState): the previous state (hidden, voltage, spikes).
            training (bool): whether dropout is active.

        Returns:
            spikes (jnp.ndarray): shape (batch, hidden_size), 1.0 where new spike occurred.
            new_state (SpikeState): updated state after applying the SSM and spiking logic.
        """
        # Project the current input and the previous hidden state
        input_current = self.input_proj(x)
        hidden_current = self.hidden_proj(state.hidden)

        if training:
            input_current = self.dropout(input_current, deterministic=not training)
            hidden_current = self.dropout(hidden_current, deterministic=not training)

        # Update hidden state
        # Example: dH = (-H + input + hidden_current) / tau
        d_hidden = jnp.clip(
            (-state.hidden + input_current + hidden_current) / self.tau,
            -100, 100
        )
        new_hidden = state.hidden + d_hidden

        # Update voltage
        # v_{t+1} = v_t + (-v_t + new_hidden)/tau
        dv = (-state.voltage + new_hidden) / self.tau
        new_voltage = state.voltage + dv

        # Check for spikes
        spikes = (new_voltage >= self.threshold).astype(jnp.float32)

        # Reset voltage where spikes occurred
        new_voltage = jnp.where(spikes > 0, self.reset_value, new_voltage)

        new_state = SpikeState(hidden=new_hidden, voltage=new_voltage, spikes=spikes)
        return spikes, new_state

    def validate_input(self, x: jnp.ndarray) -> None:
        if jnp.any(jnp.isnan(x)) or jnp.any(jnp.isinf(x)):
            raise ValueError("Input contains NaN or Inf values")
        
        if x.shape[-1] != self.hidden_size:
            raise ValueError(
                f"Input dimension {x.shape[-1]} does not match hidden_size {self.hidden_size}"
            )

    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> Union[jnp.ndarray, Tuple[jnp.ndarray, SpikeState]]:
        """
        Forward pass: scans over the time dimension, applying the spiking SSM step.

        Args:
            x (jnp.ndarray): shape (batch, seq_len, input_dim).
            context: Optional context tensor (unused)
            training (bool): whether in training mode (dropout).
            **kwargs: Additional arguments

        Returns:
            Union[jnp.ndarray, Tuple[jnp.ndarray, SpikeState]]:
                - Output tensor, or
                - Tuple of (output, final_state)
        """
        try:
            logger.debug(f"Input shape: {x.shape}")
            
            if x.ndim != 3:
                raise ValueError(
                    f"SpikeSSM expects 3D input (batch, seq_len, dim), got {x.shape}."
                )
            batch_size, seq_len, dim = x.shape

            # Initialize state if necessary
            if kwargs.get('initial_state') is None:
                initial_state = SpikeState(
                    hidden=jnp.zeros((batch_size, self.hidden_size), dtype=x.dtype),
                    voltage=jnp.zeros((batch_size, self.hidden_size), dtype=x.dtype),
                    spikes=jnp.zeros((batch_size, self.hidden_size), dtype=jnp.float32)
                )

            # We'll scan across seq_len
            def scan_fn(carry: SpikeState, x_t: jnp.ndarray):
                spikes, new_state = self._spike_step(x_t, carry, training)
                return new_state, spikes

            # Transpose x to (seq_len, batch, dim)
            x_t = jnp.swapaxes(x, 0, 1)
            final_state, spike_collection = jax.lax.scan(scan_fn, initial_state, x_t)
            # spike_collection => shape (seq_len, batch, hidden_size)

            # Re-transpose spikes to (batch, seq_len, hidden_size)
            spike_collection = jnp.swapaxes(spike_collection, 0, 1)

            # Final output projection
            outputs = self.output(spike_collection)

            logger.debug(f"Output shape: {outputs.shape}")
            
            # Return according to ISubModel interface
            if kwargs.get('return_state', False):
                return outputs, final_state
            return outputs

        except ValueError as ve:
            logger.error(f"Input validation error: {ve}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise RuntimeError("Forward pass failed") from e
