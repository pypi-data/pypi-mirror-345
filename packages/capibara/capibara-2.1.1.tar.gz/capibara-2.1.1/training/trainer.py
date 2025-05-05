"""Módulo de entrenamiento y evaluación para CapibaraModel."""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
import optax # type: ignore
from flax import linen as nn # type: ignore
from typing import Dict, Any, Optional, Tuple # type: ignore
import logging # type: ignore
from ..core.config import CapibaraConfig # type: ignore
from ..core.interfaces.isub_models import ISubModel # type: ignore
from ..utils.monitoring import ResourceMonitor # type: ignore   

logger = logging.getLogger(__name__)

class CapibaraTrainer(nn.Module):
    """Entrenador para el modelo Capibara con soporte para submodelos y pensamiento dual."""
    
    config: CapibaraConfig
    submodels: Dict[str, ISubModel]
    hidden_size: int
    use_context: bool = False
    
    def setup(self):
        """Inicializa el entrenador."""
        self.dropout = nn.Dropout(rate=self.config.dropout_rate)
        self.fusion = nn.Dense(self.hidden_size)
        self.attention = nn.SelfAttention(num_heads=8)
        
        # Adaptadores de dimensión
        self.adapters = {
            name: nn.Dense(self.hidden_size)
            for name in self.submodels.keys()
        }
        
        # Optimizador adaptativo
        self.optimizer = optax.chain(
            optax.clip_by_global_norm(1.0),
            optax.adamw(
                learning_rate=self.config.learning_rate,
                weight_decay=self.config.weight_decay
            )
        )
        
        # Monitor de recursos
        self.resource_monitor = ResourceMonitor(self.config)
    
    def _preprocess_input(self, x: jnp.ndarray) -> jnp.ndarray:
        """Preprocesa la entrada para asegurar formato 3D."""
        if x.ndim == 2:
            return x[None, :, :]  # Agrega dimensión de batch
        return x
        
    def _adapt_dimensions(self, x: jnp.ndarray, target_size: int, name: str) -> jnp.ndarray:
        """Adapta las dimensiones del tensor al tamaño objetivo."""
        if x.shape[-1] != target_size:
            return self.adapters[name](x)
        return x
        
    def _process_submodel_output(
        self,
        name: str,
        result: Any,
        context: Optional[jnp.ndarray] = None
    ) -> Tuple[jnp.ndarray, Dict[str, Any]]:
        """Procesa la salida de un submodelo según su tipo."""
        metrics = {}
        
        if isinstance(result, tuple):
            # Submodelos con estado
            output, state = result
            metrics[f"{name}_state"] = state
        elif isinstance(result, dict):
            # Submodelos con métricas
            output = result.get("output", result)
            metrics.update(result.get("metrics", {}))
        else:
            # Salida directa
            output = result
            
        # Adaptar dimensiones si es necesario
        output = self._adapt_dimensions(output, self.hidden_size, name)
        
        return output, metrics
        
    def train_step(
        self,
        state: Any,
        batch: Dict[str, jnp.ndarray]
    ) -> Tuple[Any, Dict[str, jnp.ndarray]]:
        """Paso de entrenamiento con pérdida adaptativa."""
        def loss_fn(params):
            # Forward pass
            outputs = self.apply(
                params,
                batch["input"],
                training=True
            )
            
            # Cálculo de pérdidas
            base_loss = jnp.mean((outputs["output"] - batch["target"]) ** 2)
            dual_loss = jnp.mean((outputs["metrics"]["dual_process_importance"] - 0.5) ** 2)
            
            # Pérdida total
            total_loss = base_loss + 0.1 * dual_loss
            
            return total_loss, outputs["metrics"]
        
        # Cálculo de gradientes y actualización
        grad_fn = jax.value_and_grad(loss_fn, has_aux=True)
        (loss, metrics), grads = grad_fn(state.params)
        state = state.apply_gradients(grads=grads)
        
        # Monitoreo de recursos
        self.resource_monitor.log_metric('training_loss', float(loss))
        self.resource_monitor.log_metric('gradient_norm', float(jnp.linalg.norm(grads)))
        
        return state, {"loss": loss, **metrics}
        
    def evaluate(
        self,
        state: Any,
        batch: Dict[str, jnp.ndarray]
    ) -> Dict[str, jnp.ndarray]:
        """Evaluación del modelo."""
        outputs = self.apply(
            state.params,
            batch["input"],
            training=False
        )
        
        # Métricas de evaluación
        metrics = {
            "accuracy": jnp.mean(jnp.argmax(outputs["output"], axis=-1) == batch["target"]),
            "compute_savings": outputs["metrics"]["compute_savings"],
            "avg_importance": jnp.mean(outputs["metrics"]["dual_process_importance"]),
            "avg_steps": jnp.mean(outputs["metrics"]["dual_process_steps"])
        }
        
        # Monitoreo de recursos
        self.resource_monitor.log_metric('evaluation_accuracy', float(metrics["accuracy"]))
        
        return metrics
        
    def get_submodel_metrics(self, submodel_name: str) -> Dict[str, Any]:
        """Obtiene métricas de un submodelo específico."""
        if submodel_name in self.submodels:
            submodel = self.submodels[submodel_name]
            if hasattr(submodel, "get_metrics"):
                return submodel.get_metrics()
        return {}
        
    def get_all_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de todos los submodelos."""
        return {
            name: submodel.get_metrics() if hasattr(submodel, "get_metrics") else {}
            for name, submodel in self.submodels.items()
        } 