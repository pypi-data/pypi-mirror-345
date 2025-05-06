"""
Utilities for model checkpointing.
Provides functions to save and load model state using Flax serialization.
"""

import os
from pathlib import Path
import jax #type: ignore
import orbax.checkpoint #type: ignore
import flax #type: ignore
from typing import Dict, Any, Optional, Tuple
import logging
import zlib
import hashlib
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class CheckpointManager:
    """
    Gestor de checkpoints unificado usando orbax con características avanzadas.
    
    Attributes:
        checkpoint_dir (Path): Directorio para almacenar checkpoints
        max_to_keep (int): Número máximo de checkpoints a mantener
        save_interval_steps (int): Intervalo de pasos para guardar
        compression_level (int): Nivel de compresión (0-9)
    """
    
    def __init__(
        self,
        checkpoint_dir: str,
        max_to_keep: int = 5,
        save_interval_steps: int = 1000,
        compression_level: int = 6
    ):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.max_to_keep = max_to_keep
        self.save_interval_steps = save_interval_steps
        self.compression_level = compression_level
        
        # Crear directorios necesarios
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir = self.checkpoint_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        
        # Inicializar orbax
        self.checkpointer = orbax.checkpoint.Checkpointer(
            orbax.checkpoint.PyTreeCheckpointHandler()
        )
        self.options = orbax.checkpoint.CheckpointManagerOptions(
            max_to_keep=max_to_keep,
            save_interval_steps=save_interval_steps
        )
        self.manager = orbax.checkpoint.CheckpointManager(
            self.checkpoint_dir,
            self.checkpointer,
            options=self.options
        )
        
    def _compress_data(self, data: bytes) -> bytes:
        """Comprime datos usando zlib."""
        return zlib.compress(data, level=self.compression_level)
        
    def _decompress_data(self, data: bytes) -> bytes:
        """Descomprime datos usando zlib."""
        return zlib.decompress(data)
        
    def _calculate_checksum(self, data: bytes) -> str:
        """Calcula checksum SHA-256 de los datos."""
        return hashlib.sha256(data).hexdigest()
        
    def _save_metadata(self, step: int, metadata: Dict[str, Any]):
        """Guarda metadatos del checkpoint."""
        metadata_path = self.metadata_dir / f"step_{step}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
    def _load_metadata(self, step: int) -> Dict[str, Any]:
        """Carga metadatos del checkpoint."""
        metadata_path = self.metadata_dir / f"step_{step}.json"
        with open(metadata_path, 'r') as f:
            return json.load(f)
            
    def _validate_checkpoint(self, step: int) -> bool:
        """Valida la integridad del checkpoint."""
        try:
            # Verificar existencia de archivos
            checkpoint_path = self.checkpoint_dir / str(step)
            if not checkpoint_path.exists():
                logger.error(f"Checkpoint {step} no existe")
                return False
                
            # Verificar metadatos
            try:
                metadata = self._load_metadata(step)
                if not metadata:
                    logger.error(f"Metadatos vacíos para checkpoint {step}")
                    return False
                    
                # Validar estructura de metadatos
                required_fields = ['step', 'timestamp', 'metrics', 'compression_level']
                if not all(field in metadata for field in required_fields):
                    logger.error(f"Metadatos incompletos para checkpoint {step}")
                    return False
                    
                # Verificar checksum
                if 'checksum' in metadata:
                    checkpoint_files = list(checkpoint_path.rglob('*'))
                    for file_path in checkpoint_files:
                        if file_path.is_file():
                            with open(file_path, 'rb') as f:
                                data = f.read()
                                calculated_checksum = self._calculate_checksum(data)
                                if calculated_checksum != metadata['checksum']:
                                    logger.error(f"Checksum inválido para {file_path}")
                                    return False
                                    
                return True
                
            except json.JSONDecodeError:
                logger.error(f"Error decodificando metadatos para checkpoint {step}")
                return False
                
        except Exception as e:
            logger.error(f"Error validando checkpoint {step}: {e}")
            return False
            
    def save(
        self,
        state: Any,
        step: int,
        metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Guarda el estado del modelo con validación de integridad.
        
        Args:
            state: Estado del modelo (TrainState)
            step: Paso actual
            metrics: Métricas opcionales
        """
        try:
            # Preparar metadatos
            metadata = {
                'step': step,
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics or {},
                'compression_level': self.compression_level
            }
            
            # Preparar datos para guardar
            save_data = {
                'state': state,
                'step': step
            }
            if metrics:
                save_data['metrics'] = metrics
                
            # Guardar checkpoint
            self.manager.save(step, save_data)
            
            # Guardar metadatos
            self._save_metadata(step, metadata)
            
            # Validar integridad
            if not self._validate_checkpoint(step):
                raise ValueError(f"Validación fallida para checkpoint {step}")
                
            logger.info(f"Checkpoint guardado en paso {step}")
            
        except Exception as e:
            logger.error(f"Error al guardar checkpoint: {e}")
            raise
            
    def restore(
        self,
        state: Any,
        step: Optional[int] = None
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Restaura el estado del modelo con validación.
        
        Args:
            state: Estado actual del modelo
            step: Paso específico a restaurar (opcional)
            
        Returns:
            Tupla (estado_restaurado, metadatos)
        """
        try:
            # Obtener último checkpoint si no se especifica paso
            if step is None:
                step = self.manager.latest_step()
                
            # Validar checkpoint antes de restaurar
            if not self._validate_checkpoint(step):
                raise ValueError(f"Checkpoint {step} no superó la validación")
                
            # Restaurar checkpoint
            restored = self.manager.restore(step)
            
            # Actualizar estado
            state = restored['state']
            metadata = self._load_metadata(step)
            
            logger.info(f"Checkpoint restaurado del paso {step}")
            return state, metadata
            
        except Exception as e:
            logger.error(f"Error al restaurar checkpoint: {e}")
            raise
            
    def cleanup(self) -> None:
        """Limpia checkpoints antiguos."""
        try:
            self.manager.cleanup()
            # Limpiar metadatos
            for metadata_file in self.metadata_dir.glob("*.json"):
                step = int(metadata_file.stem.split('_')[1])
                if step not in self.manager.all_steps():
                    metadata_file.unlink()
            logger.info("Checkpoints antiguos eliminados")
        except Exception as e:
            logger.error(f"Error al limpiar checkpoints: {e}")
            raise

def save_checkpoint(state: Any, path: str) -> None:
    """
    Save the given state to a checkpoint file.

    Args:
        state: The model state or training state to save.
        path (str): The file path where the checkpoint will be saved.

    Raises:
        Exception: If an error occurs during saving.
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Serialize and write state to file
        with open(path, 'wb') as f:
            f.write(flax.serialization.to_bytes(state))
        logger.info(f"Checkpoint saved at {path}")
    except Exception as e:
        logger.error(f"Failed to save checkpoint at {path}: {e}")
        raise


def load_checkpoint(state: Any, path: str) -> Any:
    """
    Load a checkpoint from file and deserialize it into the given state structure.

    Args:
        state: An existing state structure to populate with loaded data.
               This defines the type/structure expected.
        path (str): The file path from which to load the checkpoint.

    Returns:
        The deserialized state object containing the loaded parameters.

    Raises:
        FileNotFoundError: If the checkpoint file does not exist.
        Exception: For other errors during loading or deserialization.
    """
    try:
        with open(path, 'rb') as f:
            data = f.read()
        loaded_state = flax.serialization.from_bytes(state, data)
        logger.info(f"Checkpoint loaded from {path}")
        return loaded_state
    except FileNotFoundError as e:
        logger.error(f"Checkpoint file not found: {path}")
        raise
    except Exception as e:
        logger.error(f"Failed to load checkpoint from {path}: {e}")
        raise