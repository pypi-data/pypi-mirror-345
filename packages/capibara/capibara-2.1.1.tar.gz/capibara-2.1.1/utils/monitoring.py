"""Sistema de monitoreo en tiempo real para CapibaraGPT."""
import time
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Callable, List
from dataclasses import dataclass, field
import threading
from queue import Queue
import numpy as np #type: ignore
import jax.numpy as jnp #type: ignore
from ..core.config import CapibaraConfig #type: ignore

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Punto de datos para una métrica."""
    timestamp: float
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    """Configuración de alerta para una métrica."""
    threshold: float
    callback: Callable[[Any], None]

class RealTimeMonitor:
    """Monitor en tiempo real para métricas de entrenamiento."""
    
    def __init__(self, save_dir: Optional[Path] = None):
        """Inicializa el monitor."""
        self.save_dir = Path(save_dir) if save_dir else Path.cwd() / "logs"
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics: Dict[str, list[MetricPoint]] = {}
        self.alerts: Dict[str, Alert] = {}
        self.is_running = False
        self._queue: Queue = Queue()
        self._thread: Optional[threading.Thread] = None
    
    def start(self):
        """Inicia el monitoreo en un hilo separado."""
        if self.is_running:
            return
        
        self.is_running = True
        self._thread = threading.Thread(target=self._process_queue)
        self._thread.daemon = True
        self._thread.start()
        logger.info("Monitor iniciado")
    
    def stop(self):
        """Detiene el monitoreo."""
        self.is_running = False
        if self._thread:
            self._queue.put(None)  # Señal de terminación
            self._thread.join()
            self._thread = None
        logger.info("Monitor detenido")
    
    def set_alert(self, metric_name: str, threshold: float, callback: Callable):
        """Configura una alerta para una métrica."""
        self.alerts[metric_name] = Alert(threshold, callback)
        logger.debug(f"Alerta configurada para {metric_name} (umbral: {threshold})")
    
    def log_metric(self, name: str, value: float, metadata: Dict[str, Any] = {}):
        """Registra un valor de métrica."""
        point = MetricPoint(
            timestamp=time.time(),
            value=value,
            metadata=metadata or {}
        )
        self._queue.put((name, point))
    
    def _process_queue(self):
        """Procesa la cola de métricas en un hilo separado."""
        while self.is_running:
            try:
                item = self._queue.get(timeout=1.0)
                if item is None:  # Señal de terminación
                    break
                    
                name, point = item
                if name not in self.metrics:
                    self.metrics[name] = []
                
                self.metrics[name].append(point)
                self._check_alerts(name, point)
                
                # Guardar periódicamente
                if len(self.metrics[name]) % 100 == 0:
                    self._save_metrics()
                    
            except Exception as e:
                logger.error(f"Error procesando métrica: {str(e)}")
    
    def _check_alerts(self, name: str, point: MetricPoint):
        """Verifica si se deben activar alertas."""
        if name in self.alerts:
            alert = self.alerts[name]
            if point.value > alert.threshold:
                try:
                    alert.callback(point)
                except Exception as e:
                    logger.error(f"Error en callback de alerta: {str(e)}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Genera un resumen de las métricas."""
        summary = {}
        for name, points in self.metrics.items():
            values = [p.value for p in points]
            if not values:
                continue
                
            summary[name] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "count": len(values),
                "last_value": float(values[-1])
            }
        
        return summary
    
    def _save_metrics(self):
        """Guarda las métricas en disco."""
        try:
            summary = self.get_summary()
            save_path = self.save_dir / "metrics_summary.json"
            with open(save_path, 'w') as f:
                json.dump(summary, f, indent=2)
        except Exception as e:
            logger.error(f"Error guardando métricas: {str(e)}")
    
    def __del__(self):
        """Limpieza al destruir el objeto."""
        if self.is_running:
            self.stop() 

class ResourceMonitor:
    """Monitor de recursos en tiempo real con soporte para TPU"""
    
    def __init__(self, config: CapibaraConfig):
        self.config = config
        self.is_running = False
        self.metrics: Dict[str, List[float]] = {
            'memory_usage': [],
            'tpu_utilization': [],
            'training_loss': [],
            'tpu_memory': [],
            'tpu_throughput': []
        }
        self._tpu_metrics: Dict[str, List[float]] = {}
    
    def start(self):
        """Inicia el monitoreo de recursos."""
        self.is_running = True
        self.metrics = {}
        if self.config.use_tpu:
            self._initialize_tpu_metrics()
    
    def _initialize_tpu_metrics(self):
        """Inicializa métricas específicas de TPU."""
        self._tpu_metrics = {
            'core_utilization': [],
            'memory_bandwidth': [],
            'interconnect_usage': []
        }
    
    def log_tpu_metric(self, name: str, value: float):
        """Registra una métrica específica de TPU."""
        if not self.is_running or not self.config.use_tpu:
            return
        self._tpu_metrics[name].append(value)
    
    def log_metric(self, name: str, value: float, metadata: Optional[Dict] = None):
        """Registra una métrica con metadata opcional."""
        if not self.is_running:
            return
            
        self.metrics[name].append(value)
        
        # Logging adicional para TPU
        if self.config.use_tpu and name in ['memory_usage', 'throughput']:
            self._log_tpu_specific_metrics(value, metadata)
    
    def _log_tpu_specific_metrics(self, value: float, metadata: Optional[Dict]):
        """Registra métricas específicas de TPU."""
        if metadata and 'tpu_info' in metadata:
            tpu_info = metadata['tpu_info']
            self.log_tpu_metric('core_utilization', tpu_info.get('core_utilization', 0))
            self.log_tpu_metric('memory_bandwidth', tpu_info.get('memory_bandwidth', 0))
            self.log_tpu_metric('interconnect_usage', tpu_info.get('interconnect_usage', 0))
    
    def get_tpu_metrics(self) -> Dict[str, List[float]]:
        """Obtiene todas las métricas de TPU."""
        return self._tpu_metrics 
