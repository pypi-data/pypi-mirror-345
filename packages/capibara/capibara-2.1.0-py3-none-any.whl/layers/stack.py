import jax # type: ignore   
import jax.numpy as jnp # type: ignore
import flax.linen as nn # type: ignore
from typing import Optional, Tuple, List, Union
import logging
from core.interfaces import BaseLayer
from config.model_config import NeuroAdaptiveConfig

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NeuroAdaptiveStack(nn.Module):
    """Stack de capas neuroadaptativas con manejo optimizado de memoria."""
    
    config: NeuroAdaptiveConfig
    
    def setup(self):
        """Inicializa las capas del stack."""
        try:
            self.layers = [
                nn.remat(
                    nn.Dense(
                        features=self.config.hidden_size,
                        kernel_init=nn.initializers.normal(stddev=0.02),
                        bias_init=nn.initializers.zeros
                    ),
                    prevent_cse=self.config.prevent_cse,
                    static_argnums=(1,)
                ) for _ in range(self.config.num_layers)
            ]
            
            # Inicializar pesos
            self.layer_norms = [
                nn.LayerNorm(epsilon=self.config.layer_norm_eps)
                for _ in range(self.config.num_layers)
            ]
            
            logger.info(f"Stack creado con {self.config.num_layers} capas")
            
        except Exception as e:
            logger.error(f"Error inicializando stack: {str(e)}")
            raise
    
    def __call__(self,
                 hidden_states: jnp.ndarray,
                 attention_mask: Optional[jnp.ndarray] = None,
                 deterministic: bool = True) -> Tuple[jnp.ndarray, Tuple[Tuple[jnp.ndarray, ...], Tuple[jnp.ndarray, ...]]]:
        """
        Forward pass del stack con manejo optimizado de memoria.
        
        Args:
            hidden_states: Estados ocultos de entrada
            attention_mask: Máscara de atención opcional
            deterministic: Si es True, usa modo determinista
            
        Returns:
            Tupla con estados ocultos finales y estados intermedios
        """
        try:
            all_hidden_states = []
            all_attentions = []
            
            # Función para checkpointing de gradientes
            def layer_forward(layer, norm, hidden):
                # Aplicar capa
                layer_output = layer(hidden)
                
                # Aplicar normalización
                norm_output = norm(layer_output)
                
                # Aplicar dropout si está habilitado
                if self.config.dropout_rate > 0:
                    norm_output = nn.Dropout(rate=self.config.dropout_rate)(
                        norm_output, deterministic=deterministic
                    )
                
                return norm_output
            
            # Aplicar capas con remat
            current_hidden = hidden_states
            for i, (layer, norm) in enumerate(zip(self.layers, self.layer_norms)):
                # Aplicar checkpointing cada N capas
                if i % self.config.remat_frequency == 0:
                    current_hidden = jax.checkpoint(
                        layer_forward,
                        static_argnums=(2,)
                    )(layer, norm, current_hidden)
                else:
                    current_hidden = layer_forward(layer, norm, current_hidden)
                
                # Guardar estados intermedios si está configurado
                if getattr(self.config, 'output_hidden_states', False):
                    all_hidden_states.append(current_hidden)
                
                # Guardar atenciones si está configurado
                if getattr(self.config, 'output_attentions', False) and hasattr(layer, 'attention_scores'):
                    all_attentions.append(layer.attention_scores)
            
            # Logging de métricas de memoria
            if jax.config.read('jax_enable_memory_stats'):
                memory_stats = jax.memory_stats()
                logger.info(f"Uso de memoria por capa: {memory_stats}")
            
            return current_hidden, (tuple(all_hidden_states), tuple(all_attentions))
            
        except jax.errors.JAXTypeError as e:
            logger.error(f"Error de tipo en JAX: {str(e)}")
            raise
        except jax.errors.JAXRuntimeError as e:
            logger.error(f"Error de runtime en JAX: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error en forward pass: {str(e)}")
            raise 