"""Pipeline multimodal que integra visión, cuántico y conversación."""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
from typing import Dict, Any, Optional # type: ignore
from modules.capivision import Capivision
from modules.capibara_quantum_router import CapibaraQuantumRouter
from modules.contextual_router import ContextualRouter
from modules.personality.conversation_manager import ConversationManager

class MultimodalPipeline(nn.Module):
    """Pipeline que integra módulos de visión, cuántico y conversación.
    
    Args:
        config: Configuración del pipeline
    """
    config: Dict[str, Any]
    
    def setup(self):
        """Inicializa módulos."""
        self.vision = Capivision(self.config["vision"])
        self.quantum_router = CapibaraQuantumRouter(self.config["quantum"])
        self.contextual_router = ContextualRouter(self.config["contextual"])
        self.conversation = ConversationManager(self.config["conversation"])
        
    def __call__(
        self,
        x: jnp.ndarray,
        context: Optional[Dict[str, Any]] = None,
        training: bool = False
    ) -> Dict[str, Any]:
        """Procesa entrada a través de todos los módulos.
        
        Args:
            x: Tensor de entrada (batch, seq_len, hidden_size)
            context: Contexto opcional
            training: Modo entrenamiento
            
        Returns:
            Dict con output final y métricas agregadas
        """
        # Procesar entrada visual
        visual_result = self.vision(x, context, training)
        
        # Enrutar a través de router cuántico
        quantum_result = self.quantum_router(
            visual_result["output"],
            context,
            training
        )
        
        # Enrutar contextualmente
        contextual_result = self.contextual_router(
            quantum_result["output"],
            context,
            training
        )
        
        # Generar respuesta conversacional
        conversation_result = self.conversation(
            contextual_result["output"],
            context,
            training
        )
        
        # Combinar métricas
        metrics = {
            **visual_result["metrics"],
            **quantum_result["metrics"],
            **contextual_result["metrics"],
            **conversation_result["metrics"]
        }
        
        return {
            "output": conversation_result["output"],
            "metrics": metrics
        } 