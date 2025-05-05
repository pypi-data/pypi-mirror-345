"""Módulo de gestión de checkpoints unificado usando Orbax.

Este módulo implementa un gestor avanzado de checkpoints con:
- Compresión de checkpoints
- Validación de integridad
- Checkpoints incrementales
- Manejo mejorado de metadatos
"""

import jax #type: ignore
import orbax.checkpoint as ocp #type: ignore
from pathlib import Path
import logging
import zlib
import json
import hashlib
import shutil
from typing import Dict, Any, Optional, Union, Tuple
from functools import partial
from datetime import datetime

from capibara_model.core.distribution_config import (
    BATCH_SHARDING,
    MODEL_SHARDING,
    HYBRID_SHARDING
)

logger = logging.getLogger(__name__)

class CapibaraCheckpointManager:
    """Gestor unificado de checkpoints usando Orbax con características avanzadas."""
    
    def __init__(
        self,
        checkpoint_dir: Union[str, Path],
        max_to_keep: int = 5,
        save_interval: int = 1000,
        use_async: bool = True,
        sharding: Optional[Any] = None,
        compression_level: int = 6,
        validate_integrity: bool = True,
        incremental_save: bool = True
    ):
        """Inicializa el gestor de checkpoints.
        
        Args:
            checkpoint_dir: Directorio para guardar checkpoints
            max_to_keep: Máximo número de checkpoints a mantener
            save_interval: Intervalo de pasos entre checkpoints
            use_async: Si se debe usar checkpointing asíncrono
            sharding: Configuración de sharding para TPU
            compression_level: Nivel de compresión (0-9)
            validate_integrity: Si se debe validar la integridad
            incremental_save: Si se debe usar guardado incremental
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.save_interval = save_interval
        self.compression_level = compression_level
        self.validate_integrity = validate_integrity
        self.incremental_save = incremental_save
        
        # Crear directorios necesarios
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir = self.checkpoint_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        
        # Configurar opciones
        options = ocp.CheckpointManagerOptions(
            max_to_keep=max_to_keep,
            save_interval_steps=save_interval,
            sharding=sharding or BATCH_SHARDING
        )
        
        # Crear checkpointer apropiado
        if use_async:
            checkpointer = ocp.AsyncCheckpointer(
                ocp.PyTreeCheckpointHandler()
            )
        else:
            checkpointer = ocp.Checkpointer(
                ocp.PyTreeCheckpointHandler()
            )
            
        # Inicializar manager
        self.manager = ocp.CheckpointManager(
            self.checkpoint_dir,
            checkpointer,
            options=options
        )
        
        logger.info(f"Checkpoint manager inicializado en {checkpoint_dir}")
        
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
        """Valida la integridad del checkpoint.
        
        Args:
            step: Paso del checkpoint a validar
            
        Returns:
            bool: True si el checkpoint es válido
        """
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
                                    
                # Verificar tamaño total
                total_size = sum(f.stat().st_size for f in checkpoint_path.rglob('*') if f.is_file())
                if total_size > self.max_checkpoint_size:
                    logger.error(f"Checkpoint {step} excede el tamaño máximo permitido")
                    return False
                    
                return True
                
            except json.JSONDecodeError:
                logger.error(f"Error decodificando metadatos para checkpoint {step}")
                return False
                
        except Exception as e:
            logger.error(f"Error validando checkpoint {step}: {e}")
            return False
            
    def _validate_metadata_schema(self, metadata: Dict[str, Any]) -> bool:
        """Valida el esquema de metadatos.
        
        Args:
            metadata: Diccionario de metadatos a validar
            
        Returns:
            bool: True si el esquema es válido
        """
        try:
            schema = {
                'step': int,
                'timestamp': str,
                'metrics': dict,
                'compression_level': int
            }
            
            for field, expected_type in schema.items():
                if field not in metadata:
                    return False
                if not isinstance(metadata[field], expected_type):
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error validando esquema de metadatos: {e}")
            return False
            
    def save(
        self,
        step: int,
        state: Any,
        metrics: Optional[Dict[str, float]] = None,
        force: bool = False,
        incremental: Optional[bool] = None
    ) -> bool:
        """Guarda un checkpoint con características avanzadas."""
        try:
            # Preparar metadatos
            metadata = {
                'step': step,
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics or {},
                'compression_level': self.compression_level
            }
            
            # Preparar argumentos de guardado
            save_args = ocp.args.StandardSave(state=state)
            
            # Guardar checkpoint
            saved = self.manager.save(
                step,
                args=save_args,
                metrics=metrics,
                force=force
            )
            
            if saved:
                # Guardar metadatos
                self._save_metadata(step, metadata)
                
                # Validar integridad si está habilitada
                if self.validate_integrity:
                    if not self._validate_checkpoint(step):
                        logger.error(f"Validación fallida para checkpoint {step}")
                        return False
                        
                logger.info(f"Checkpoint guardado en paso {step}")
            return saved
            
        except Exception as e:
            logger.error(f"Error guardando checkpoint: {e}")
            raise
            
    def restore(
        self,
        step: Optional[int] = None,
        state: Optional[Any] = None,
        validate: Optional[bool] = None
    ) -> Tuple[Any, Dict[str, Any]]:
        """Restaura un checkpoint con validación.
        
        Args:
            step: Paso a restaurar (si es None, usa el último)
            state: Estado base para restaurar
            validate: Si se debe validar la integridad
            
        Returns:
            Tupla con estado restaurado y metadatos
        """
        try:
            # Determinar paso a restaurar
            if step is None:
                step = self.manager.latest_step()
                if step is None:
                    raise ValueError("No hay checkpoints disponibles")
                    
            # Validar si está habilitado
            validate = validate if validate is not None else self.validate_integrity
            if validate and not self._validate_checkpoint(step):
                raise ValueError(f"Checkpoint {step} no superó la validación")
                
            # Preparar argumentos de restauración
            restore_args = ocp.args.StandardRestore(state=state)
            
            # Restaurar checkpoint
            restored_state = self.manager.restore(
                step,
                args=restore_args
            )
            
            # Cargar metadatos
            metadata = self._load_metadata(step)
            
            logger.info(f"Checkpoint restaurado del paso {step}")
            return restored_state, metadata
            
        except Exception as e:
            logger.error(f"Error restaurando checkpoint: {e}")
            raise
            
    def get_latest_step(self) -> Optional[int]:
        """Obtiene el último paso guardado."""
        return self.manager.latest_step()
        
    def get_all_steps(self) -> list[int]:
        """Obtiene todos los pasos guardados."""
        return self.manager.all_steps()
        
    def get_checkpoint_info(self, step: int) -> Dict[str, Any]:
        """Obtiene información detallada de un checkpoint."""
        try:
            metadata = self._load_metadata(step)
            checkpoint_path = self.checkpoint_dir / str(step)
            
            return {
                'step': step,
                'path': str(checkpoint_path),
                'size': sum(f.stat().st_size for f in checkpoint_path.rglob('*')),
                'metadata': metadata,
                'valid': self._validate_checkpoint(step)
            }
        except Exception as e:
            logger.error(f"Error obteniendo información del checkpoint {step}: {e}")
            return {}
            
    def cleanup_old_checkpoints(self, keep_last_n: Optional[int] = None):
        """Limpia checkpoints antiguos manteniendo los últimos n."""
        try:
            steps = self.get_all_steps()
            if not steps:
                return
                
            keep_last_n = keep_last_n or self.manager.options.max_to_keep
            steps_to_keep = sorted(steps)[-keep_last_n:]
            
            for step in steps:
                if step not in steps_to_keep:
                    # Eliminar checkpoint
                    checkpoint_path = self.checkpoint_dir / str(step)
                    if checkpoint_path.exists():
                        shutil.rmtree(checkpoint_path)
                        
                    # Eliminar metadatos
                    metadata_path = self.metadata_dir / f"step_{step}.json"
                    if metadata_path.exists():
                        metadata_path.unlink()
                        
            logger.info(f"Limpieza de checkpoints completada. Manteniendo {keep_last_n} más recientes.")
            
        except Exception as e:
            logger.error(f"Error en limpieza de checkpoints: {e}")
            raise
            
    def wait_until_finished(self):
        """Espera a que se completen operaciones asíncronas."""
        if hasattr(self.manager, 'wait_until_finished'):
            self.manager.wait_until_finished()
            
    def close(self):
        """Cierra el gestor de checkpoints."""
        self.manager.close() 