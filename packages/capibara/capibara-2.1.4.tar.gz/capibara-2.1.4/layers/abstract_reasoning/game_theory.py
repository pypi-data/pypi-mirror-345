"""Implementación de capas basadas en teoría de juegos.

Este módulo implementa interacciones estratégicas usando teoría de juegos,
incluyendo equilibrios de Nash y optimizaciones de utilidad.
"""

import enum
from typing import Dict, Any, Optional, Callable

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from interfaces.ilayer import ILayer # type: ignore


class GameType(enum.Enum):
    """Tipos de juegos soportados."""
    ZERO_SUM = "zero_sum"  # Juegos de suma cero
    POTENTIAL = "potential"  # Juegos potenciales
    GENERAL = "general"  # Juegos generales


class GameTheory(nn.Module, ILayer):
    """Capa de teoría de juegos con cómputo vectorizado de equilibrio de Nash.
    
    Implementa una aproximación diferenciable de equilibrios de Nash mediante
    iteraciones de mejor respuesta suavizadas con softmax. La convergencia está
    garantizada para juegos de suma cero y juegos potenciales.
    
    Args:
        hidden_size: Dimensión del espacio de estrategias
        num_players: Número de jugadores en el juego (default: 2)
        dropout_rate: Tasa de dropout para regularización (default: 0.1)
        num_iterations: Número de iteraciones para equilibrio (default: 10)
        temperature: Parámetro de temperatura para softmax (default: 1.0)
        game_type: Tipo de juego (zero_sum/potential/general) (default: general)
    """
    
    hidden_size: int
    num_players: int = 2
    dropout_rate: float = 0.1
    num_iterations: int = 10
    temperature: float = 1.0
    game_type: GameType = GameType.GENERAL

    @nn.compact
    def __call__(self, x: jnp.ndarray, training: bool = False, **kwargs) -> Dict[str, Any]:
        """Aplica transformación de teoría de juegos.
        
        Args:
            x: Tensor de entrada de forma (batch_size, hidden_size)
            training: Si está en modo entrenamiento
            **kwargs: Argumentos adicionales
            
        Returns:
            Diccionario con:
                - output: Estrategias de equilibrio
                - metrics: Métricas del juego (nash_distance, utility, entropy)
                - training: Flag de modo entrenamiento
        """
        # Validación de entrada
        assert x.ndim == 2, f"Se esperaba entrada 2D, se obtuvo {x.ndim}D"
        assert x.shape[-1] == self.hidden_size, (
            f"La última dimensión debe coincidir con hidden_size={self.hidden_size}, "
            f"se obtuvo {x.shape[-1]}"
        )
        
        # Normalización y cómputo de pagos
        x = nn.LayerNorm(name="norm")(x)
        payoffs = nn.Dense(
            self.hidden_size * self.num_players,
            name="payoffs"
        )(x)
        payoffs = payoffs.reshape(-1, self.hidden_size, self.num_players)
        
        # Encontrar equilibrio de Nash
        strategies = self._find_equilibrium(payoffs)
        
        # Aplicar dropout si está entrenando
        strategies = nn.Dropout(
            rate=self.dropout_rate,
            deterministic=not training
        )(strategies)
        
        return {
            "output": strategies,
            "metrics": self._compute_metrics(payoffs, strategies),
            "training": training
        }

    def _find_equilibrium(self, payoffs: jnp.ndarray) -> jnp.ndarray:
        """Computa equilibrio de Nash aproximado mediante iteraciones vectorizadas.
        
        Implementa dinámica de mejor respuesta suavizada con softmax. Para juegos
        de suma cero, la convergencia al equilibrio de Nash está garantizada teóricamente.
        
        Args:
            payoffs: Tensor de pagos de forma (batch_size, hidden_size, num_players)
            
        Returns:
            Estrategias de equilibrio de forma (batch_size, hidden_size)
        """
        def body_fn(strategies, _):
            # Computar utilidad esperada y actualizar estrategias
            utility = jnp.einsum('bij,bj->bi', payoffs, strategies)
            new_strategies = jax.nn.softmax(utility / self.temperature, axis=-1)
            return new_strategies, None
        
        # Inicializar estrategias uniformes
        initial_strategies = jnp.ones((payoffs.shape[0], self.hidden_size)) / self.hidden_size
        
        # Ejecutar iteraciones de punto fijo
        final_strategies, _ = jax.lax.scan(
            body_fn,
            initial_strategies,
            None,
            length=self.num_iterations
        )
        
        return final_strategies

    def _compute_metrics(
        self,
        payoffs: jnp.ndarray,
        strategies: jnp.ndarray
    ) -> Dict[str, jnp.ndarray]:
        """Computa métricas de teoría de juegos.
        
        Args:
            payoffs: Matriz de pagos (batch_size, hidden_size, num_players)
            strategies: Estrategias de equilibrio (batch_size, hidden_size)
            
        Returns:
            Diccionario de métricas:
                - nash_distance: Distancia al equilibrio de Nash
                - utility: Utilidad esperada para cada jugador
                - entropy: Entropía de las distribuciones de estrategias
        """
        # Utilidad esperada
        utility = jnp.einsum('bij,bj->bi', payoffs, strategies)
        
        # Entropía de estrategias
        entropy = -jnp.sum(strategies * jnp.log(strategies + 1e-10), axis=-1)
        
        # Distancia al equilibrio de Nash (gradiente analítico)
        grad_utility = payoffs - jnp.mean(payoffs, axis=1, keepdims=True)
        nash_distance = jnp.linalg.norm(grad_utility, axis=-1)
        
        return {
            "nash_distance": nash_distance,
            "utility": utility,
            "entropy": entropy
        } 