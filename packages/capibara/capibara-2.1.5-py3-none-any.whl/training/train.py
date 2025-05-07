"""
Módulo de entrenamiento para CapibaraModel.
"""

import logging
from pathlib import Path
from typing import Optional
import jax # type: ignore
import jax.numpy as jnp # type: ignore
import optax # type: ignore

from core.config import CapibaraConfig
from core.model import DynamicCapibaraModel
from core.optimizer import create_optimizer_from_capibara_config
from utils.checkpointing import load_checkpoint, save_checkpoint

logger = logging.getLogger(__name__)

def run_training(config: CapibaraConfig, checkpoint_path: Optional[Path] = None):
    """
    Ejecuta el proceso de entrenamiento del modelo.
    
    Args:
        config: Configuración del modelo
        checkpoint_path: Ruta al checkpoint para cargar (opcional)
    """
    try:
        # Crear modelo
        model = DynamicCapibaraModel(config=config)
        logger.info("Modelo creado exitosamente")
        
        # Crear optimizador
        optimizer = create_optimizer_from_capibara_config(config.to_dict())
        logger.info("Optimizador creado exitosamente")
        
        # Inicializar estado de entrenamiento
        rng = jax.random.PRNGKey(config.training.seed)
        dummy_batch = jnp.ones(
            (config.training.batch_size, config.model.max_length),
            dtype=jnp.int32
        )
        variables = model.init(rng, dummy_batch, training=True)
        state = optax.TrainState.create(
            apply_fn=model.apply,
            params=variables['params'],
            tx=optimizer
        )
        
        # Cargar checkpoint si existe
        if checkpoint_path and checkpoint_path.exists():
            logger.info(f"Cargando checkpoint desde {checkpoint_path}")
            state = load_checkpoint(checkpoint_path, state)
        
        # Iniciar entrenamiento
        logger.info("Iniciando entrenamiento...")
        for epoch in range(config.training.num_epochs):
            logger.info(f"Época {epoch + 1}/{config.training.num_epochs}")
            
            # Aquí iría la lógica de entrenamiento por época
            # Por ahora solo un placeholder
            logger.info("Entrenamiento en progreso...")
            
            # Guardar checkpoint periódicamente
            if (epoch + 1) % config.training.checkpoint_frequency == 0:
                checkpoint_path = config.paths.checkpoint_dir / f"checkpoint_epoch_{epoch + 1}"
                save_checkpoint(checkpoint_path, state)
                logger.info(f"Checkpoint guardado en {checkpoint_path}")
        
        logger.info("Entrenamiento completado exitosamente")
        
    except Exception as e:
        logger.error(f"Error durante el entrenamiento: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Entrenamiento de CapibaraModel")
    parser.add_argument("--config", type=str, required=True, help="Ruta al archivo de configuración")
    parser.add_argument("--output_dir", type=str, required=True, help="Directorio de salida")
    parser.add_argument("--use_tpu", action="store_true", help="Usar TPU para entrenamiento")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    run_training(
        config=CapibaraConfig.from_yaml(args.config),
        checkpoint_path=Path(args.output_dir) if args.use_tpu else None
    )