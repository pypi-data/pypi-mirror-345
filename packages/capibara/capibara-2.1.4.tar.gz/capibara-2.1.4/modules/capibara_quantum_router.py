"""
Quantum Router for CapibaraGPT – gestiona VQbits dinámicos y preentrenados.
"""

from typing import Dict
import jax 
import jax.numpy as jnp
from flax import linen as nn #type: ignore
from capibara_model.modules.quantumL import DifferentiableQuantumEmbedding
from capibara_model.modules.quantum_config import VQbitConfig
import numpy as np
import logging
from functools import partial

logger = logging.getLogger(__name__)

class CapibaraQuantumRouter(nn.Module):
    config: VQbitConfig
    total_vqbits: int
    hidden_size: int

    def setup(self):
        dynamic_vqbits = int(self.total_vqbits * 0.15)
        pretrained_vqbits = int(self.total_vqbits * 0.15)

        self.dynamic_vqbits = DifferentiableQuantumEmbedding(
            hidden_size=self.hidden_size,
            num_qubits=dynamic_vqbits,
            qubit_dim=self.hidden_size // max(dynamic_vqbits, 1),
            backend="ensemble"
        )

        self.pretrained_vqbits = DifferentiableQuantumEmbedding(
            hidden_size=self.hidden_size,
            num_qubits=pretrained_vqbits,
            qubit_dim=self.hidden_size // max(pretrained_vqbits, 1),
            backend="ensemble"
        )

        self.context_encoder = nn.Sequential([
            nn.Dense(512),
            nn.LayerNorm(),
            nn.relu,
            nn.Dense(1),
            nn.sigmoid
        ])

        self._init_router_state()

    def _init_router_state(self):
        self._context_cache = {}
        self._routing_stats = {"dynamic_hits": 0, "pretrained_hits": 0, "mixed_hits": 0}
        self.routing_state = {
            "context_history": [],
            "weight_history": [],
            "performance_metrics": {
                "dynamic": [],
                "pretrained": []
            }
        }

    @partial(jax.jit, static_argnums=(0,))
    def _compute_context_weight(self, context_embedding: jnp.ndarray) -> float:
        cache_key = hash(context_embedding.tobytes())
        if cache_key in self._context_cache:
            return self._context_cache[cache_key]

        weight = self.context_encoder(context_embedding)
        weight = jnp.clip(weight, 0.0, 1.0)
        self._context_cache[cache_key] = float(weight)
        return weight

    def _update_routing_stats(self, weight: float):
        if weight < 0.2:
            self._routing_stats["dynamic_hits"] += 1
        elif weight > 0.8:
            self._routing_stats["pretrained_hits"] += 1
        else:
            self._routing_stats["mixed_hits"] += 1

    def _adaptive_mixing(self, x_dyn: jnp.ndarray, x_pre: jnp.ndarray, α: float) -> jnp.ndarray:
        dyn_coherence = jnp.mean(jnp.abs(x_dyn))
        pre_coherence = jnp.mean(jnp.abs(x_pre))
        coherence_ratio = dyn_coherence / (dyn_coherence + pre_coherence)
        α_adjusted = α * coherence_ratio

        self.routing_state["performance_metrics"]["dynamic"].append(float(dyn_coherence))
        self.routing_state["performance_metrics"]["pretrained"].append(float(pre_coherence))

        return (1 - α_adjusted) * x_dyn + α_adjusted * x_pre

    def __call__(self, x: jnp.ndarray, context: jnp.ndarray, training: bool = False) -> jnp.ndarray:
        x_dyn = self.dynamic_vqbits(x)
        x_pre = self.pretrained_vqbits(x)
        α = self._compute_context_weight(context)

        if training:
            self.routing_state["context_history"].append(context)
            self.routing_state["weight_history"].append(float(α))
            self._update_routing_stats(α)
            self._maintain_cache()

        return self._adaptive_mixing(x_dyn, x_pre, α)

    def _maintain_cache(self):
        if len(self._context_cache) > 1000:
            self._context_cache.clear()
        if len(self.routing_state["context_history"]) > 1000:
            self.routing_state["context_history"] = self.routing_state["context_history"][-1000:]
            self.routing_state["weight_history"] = self.routing_state["weight_history"][-1000:]

    def get_routing_metrics(self) -> Dict:
        total_hits = sum(self._routing_stats.values())
        return {
            "routing_distribution": {
                k: v / total_hits if total_hits > 0 else 0
                for k, v in self._routing_stats.items()
            },
            "average_weight": np.mean(self.routing_state["weight_history"])
            if self.routing_state["weight_history"] else 0,
            "dynamic_performance": np.mean(
                self.routing_state["performance_metrics"]["dynamic"]
            ),
            "pretrained_performance": np.mean(
                self.routing_state["performance_metrics"]["pretrained"]
            )
        }
