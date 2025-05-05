"""Implementación mejorada de NeurogenesisModule.

Esta capa implementa activación estática con tracking de métricas
y test integrado.
"""

import jax #type: ignore
import jax.numpy as jnp #type: ignore
from flax import linen as nn #type: ignore
import logging
from typing import Optional, Tuple, Dict, Any, Union
from functools import partial

from interfaces.imodules import IModule
from core.config import CapibaraConfig
from layers.base import BaseLayer, LayerConfig

logger = logging.getLogger(__name__)

class NeurogenesisModuleConfig(LayerConfig):
    """Configuración específica para NeurogenesisModule.
    
    Args:
        hidden_size: Dimensión del espacio oculto
        activation_threshold: Umbral de activación
        activation_rate: Tasa de activación
        test_mode: Si True, activa modo test
    """
    def __init__(
        self,
        hidden_size: int,
        dropout_rate: float = 0.1,
        deterministic: bool = False,
        prevent_cse: bool = False,
        activation_threshold: float = 0.5,
        activation_rate: float = 0.1,
        test_mode: bool = False
    ):
        super().__init__(
            hidden_size=hidden_size,
            dropout_rate=dropout_rate,
            deterministic=deterministic,
            prevent_cse=prevent_cse
        )
        self.activation_threshold = activation_threshold
        self.activation_rate = activation_rate
        self.test_mode = test_mode

class NeurogenesisModule(BaseLayer):
    """Módulo de neurogénesis con activación estática.
    
    Implementa:
    - Activación estática con umbral
    - Tracking de métricas
    - Test integrado
    
    Ejemplo de uso:
    ```python
    config = NeurogenesisModuleConfig(
        hidden_size=512,
        activation_threshold=0.5,
        activation_rate=0.1
    )
    module = NeurogenesisModule(config)
    output = module(x, training=True, rng=key)
    ```
    """
    
    config: NeurogenesisModuleConfig
    
    def setup(self):
        """Inicializa NeurogenesisModule."""
        super().setup()
        
        # Máscara de activación
        self.activation_mask = self.param(
            "activation_mask",
            nn.initializers.bernoulli(self.config.activation_rate),
            (self.config.hidden_size,)
        )
        
        # Umbral de activación
        self.threshold = self.param(
            "threshold",
            nn.initializers.constant(self.config.activation_threshold),
            ()
        )
        
    def __call__(
        self,
        x: jnp.ndarray,
        training: bool = False,
        rng: Optional[jax.random.PRNGKey] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Aplica NeurogenesisModule.
        
        Args:
            x: Tensor de entrada (batch_size, seq_len, hidden_dim)
            training: Modo entrenamiento
            rng: Key aleatoria
            **kwargs: Argumentos adicionales
            
        Returns:
            Dict con output y métricas
        """
        if training and rng is None:
            raise ValueError("Se requiere rng en modo entrenamiento")
            
        # Congelar máscara durante entrenamiento
        if training:
            self.activation_mask = jax.lax.stop_gradient(self.activation_mask)
            
        # Aplicar activación
        mask = jnp.where(
            self.activation_mask > self.threshold,
            1.0,
            0.0
        )
        
        # Aplicar máscara
        output = x * mask[None, None, :]
        
        # Métricas específicas
        metrics = {
            "activation_rate": jnp.mean(mask),
            "threshold": self.threshold,
            "mask_norm": jnp.linalg.norm(mask)
        }
        
        # Combinar con métricas base
        base_output = self._base_call(output, training=training, rng=rng)
        base_output["metrics"].update(metrics)
        
        return base_output
        
    def test(self, x: jnp.ndarray) -> Dict[str, Any]:
        """Ejecuta test integrado.
        
        Args:
            x: Tensor de entrada
            
        Returns:
            Dict con métricas de test
        """
        if not self.config.test_mode:
            return {"test": "disabled"}
            
        # Test de activación
        activation_rate = jnp.mean(self.activation_mask > self.threshold)
        
        # Test de umbral
        threshold_test = jnp.all(self.threshold >= 0.0)
        
        return {
            "test": {
                "activation_rate": activation_rate,
                "threshold_valid": threshold_test
            }
        }

# Test del módulo
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Configuración
        batch_size = 32
        seq_len = 128
        hidden_size = 768
        
        # Inicializar módulo
        config = NeurogenesisModuleConfig(
            hidden_size=hidden_size,  # Campo heredado de LayerConfig
            dropout_rate=0.1,  # Campo heredado de LayerConfig
            deterministic=False,  # Campo heredado de LayerConfig
            prevent_cse=False,  # Campo heredado de LayerConfig
            activation_threshold=0.5,  # Campo específico de NeurogenesisConfig
            activation_rate=0.1,  # Campo específico de NeurogenesisConfig
            test_mode=True  # Campo específico de NeurogenesisConfig
        )
        module = NeurogenesisModule(config)
        
        # Datos de prueba
        key = jax.random.PRNGKey(0)
        x = jax.random.normal(key, (batch_size, seq_len, hidden_size))
        
        # Forward pass
        params = module.init(key, x, training=True)
        result = module.apply(params, x, training=True, rngs={'params': key})
        
        logger.info(f"Test exitoso - Tamaño de salida: {result['output'].shape}")
        logger.info(f"Métricas: {result}")
        
    except Exception as e:
        logger.error(f"Test fallido: {str(e)}")
        raise

# Mejorar coordinación entre SSM y Transformer
class HybridArchitecture(nn.Module):
    def __call__(self, x):
        ssm_out = self.ssm_layer(x)
        transformer_out = self.transformer_layer(x)
        return self.fusion_layer(ssm_out, transformer_out)