"""Pipeline centralizado para módulos de personalidad."""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from typing import Dict, Any, Sequence, Optional # type: ignore
from .base_config import BasePersonalityConfig

class PersonalityPipeline(nn.Module):
    """Pipeline que orquesta módulos de personalidad en secuencia.
    
    Args:
        config: Configuración base
        modules: Secuencia de módulos a ejecutar
    """
    config: BasePersonalityConfig
    modules: Sequence[nn.Module]
    
    def setup(self):
        """Inicializa pipeline."""
        self.norm = nn.LayerNorm()
        
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[Dict[str, Any]] = None,
        training: bool = False
    ) -> Dict[str, Any]:
        """Ejecuta módulos en secuencia.
        
        Args:
            x: Tensor de entrada (batch, seq_len, hidden_size)
            context: Contexto opcional para módulos
            training: Modo entrenamiento
            
        Returns:
            Dict con output final y métricas agregadas
        """
        # Normalizar entrada
        x = self.norm(x)
        
        # Métricas acumuladas
        all_metrics = {}
        current_output = x
        
        # Ejecutar módulos en secuencia
        for i, module in enumerate(self.modules):
            # Ejecutar módulo
            result = module(current_output, context, training)
            
            # Actualizar output
            current_output = result["output"]
            
            # Acumular métricas
            for k, v in result.get("metrics", {}).items():
                all_metrics[f"module_{i}_{k}"] = v
                
        # Métricas finales
        all_metrics.update({
            "final_norm": jnp.linalg.norm(current_output),
            "num_modules": len(self.modules)
        })
        
        return {
            "output": current_output,
            "metrics": all_metrics
        } 