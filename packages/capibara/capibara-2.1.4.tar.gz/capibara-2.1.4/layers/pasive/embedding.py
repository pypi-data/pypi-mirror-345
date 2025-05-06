"""Implementación de embedding distribuido para CapibaraModel."""

from typing import Optional, Dict, Any, Union, Tuple
import jax
import jax.numpy as jnp
from jax.experimental import PartitionSpec as P

from capibara_model.layers.base import Layer
from capibara_model.core.distribution_config import MODEL_SHARDING, REPLICATED

class CapibaraEmbedding(Layer):
    """Capa de embedding con soporte de distribución."""
    
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int,
        sharding_strategy: str = "model_parallel",
        name: Optional[str] = None
    ):
        """Inicializa la capa de embedding.
        
        Args:
            vocab_size: Tamaño del vocabulario
            embed_dim: Dimensión del embedding
            sharding_strategy: Estrategia de sharding
            name: Nombre opcional de la capa
        """
        super().__init__(sharding_strategy, name)
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        
        # Inicializa pesos con distribución
        self.embedding = jax.random.normal(
            jax.random.PRNGKey(0),
            (vocab_size, embed_dim)
        )
        
        # Aplica sharding a los pesos
        self.embedding = self.apply_sharding(
            self.embedding,
            MODEL_SHARDING
        )
    
    def _call_impl(
        self,
        x: jnp.ndarray,
        context: Optional[jnp.ndarray] = None,
        training: bool = False,
        **kwargs: Any
    ) -> Union[jnp.ndarray, Tuple[jnp.ndarray, Dict[str, Any]]]:
        """Implementación del forward pass.
        
        Args:
            x: Tensor de entrada de índices
            context: No usado en embedding
            training: No usado en embedding
            **kwargs: Argumentos adicionales
            
        Returns:
            Tensor de embeddings
        """
        # Obtiene embeddings
        embeddings = jnp.take(self.embedding, x)
        
        # Aplica sharding a la salida
        embeddings = self.apply_sharding(
            embeddings,
            REPLICATED
        )
        
        return embeddings
    
    def _get_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de la capa.
        
        Returns:
            Diccionario de métricas
        """
        return {
            "embedding_norm": jnp.linalg.norm(self.embedding),
            "embedding_mean": jnp.mean(self.embedding),
            "embedding_std": jnp.std(self.embedding)
        }