"""
Implementación de capas cuánticas para CapibaraGPT.
Incluye QuantumEmbedding con diferentes modos de operación.
"""

from typing import Optional, Dict, Any, Union, Tuple, List
import jax #type: ignore
import jax.numpy as jnp #type: ignore
from flax import linen as nn #type: ignore
from capibara.core.interfaces.ilayer import ILayer
from pydantic import BaseModel, Field #type: ignore
from functools import partial
import logging
import pennylane as qml #type: ignore
import numpy as np #type: ignore
from dataclasses import dataclass
from config.quantum_config import VQbitConfig
import time
from collections import OrderedDict
from layers.base import BaseLayer, LayerConfig

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# --------------------------------------------------
# Helper para cálculo de entropía
# --------------------------------------------------
def _calculate_shannon_entropy(vectors: jnp.ndarray, epsilon: float = 1e-9) -> jnp.ndarray:
    """
    Calcula la entropía de Shannon para cada vector en un batch.
    Normaliza los vectores para que sumen 1 (como una distribución de probabilidad).
    """
    # Normalizar para que se parezca a una distribución (ej. softmax)
    p = nn.softmax(vectors, axis=-1)
    # Calcular entropía: -sum(p * log(p))
    log_p = jnp.log(p + epsilon) # Añadir epsilon para estabilidad numérica
    entropy = -jnp.sum(p * log_p, axis=-1)
    return entropy

# --------------------------------------------------
# Capa QuantumEmbedding Mejorada
# --------------------------------------------------
class QuantumEmbedding(nn.Module, ILayer):
    """
    Capa base para embeddings cuánticos.
    Maneja la lógica de backends y ensemble.
    """
    hidden_size: int
    backend: str = "jax"
    
    def __call__(self, x):
        return self.quantum_transform(x)

    def setup(self):
        self._result_cache: OrderedDict = OrderedDict()  # LRU cache
        self.MAX_CACHE_SIZE: int = 1000
        self._quantum_metrics: Dict[str, List[float]] = {
            "entropy": [],
            "coherence": [],
            "entanglement": []
        }

    def quantum_transform(self, x: jnp.ndarray) -> jnp.ndarray:
        """
        Transformación cuántica base usando JAX
        """
        # Normalización y preparación
        x = self._prepare_quantum_state(x)
        
        # Simulación de operaciones cuánticas
        x = self._apply_quantum_gates(x)
        
        # Medición y métricas
        x = self._measure_quantum_state(x)
        
        return x

    def _prepare_quantum_state(self, x: jnp.ndarray) -> jnp.ndarray:
        """Prepara el estado cuántico inicial"""
        # Normalización
        norm = jnp.sqrt(jnp.sum(jnp.abs(x)**2, axis=-1, keepdims=True))
        x = x / (norm + 1e-7)
        
        # Convertir a estado cuántico
        return jnp.exp(1j * x * jnp.pi)

    def _apply_quantum_gates(self, x: jnp.ndarray) -> jnp.ndarray:
        """Aplica operaciones cuánticas simuladas"""
        # Hadamard-like operation
        x = (x + jnp.roll(x, 1, axis=-1)) / jnp.sqrt(2.0)
        
        # Phase operation
        phase = jnp.exp(2j * jnp.pi * jnp.arange(x.shape[-1]) / x.shape[-1])
        x = x * phase
        
        # Entanglement simulation
        x = jnp.fft.fft(x, axis=-1)
        
        return x

    def _measure_quantum_state(self, x: jnp.ndarray) -> jnp.ndarray:
        """Realiza medición y calcula métricas"""
        # Probabilidades
        probs = jnp.abs(x)**2
        
        # Calcular métricas
        entropy = self._calculate_quantum_entropy(probs)
        coherence = self._calculate_quantum_coherence(x)
        
        # Actualizar métricas
        self._quantum_metrics["entropy"].append(float(entropy.mean()))
        self._quantum_metrics["coherence"].append(float(coherence.mean()))
        
        return jnp.real(x)

    def _calculate_quantum_entropy(self, probs: jnp.ndarray) -> jnp.ndarray:
        """Calcula la entropía de von Neumann"""
        return -jnp.sum(probs * jnp.log2(probs + 1e-7), axis=-1)

    def _calculate_quantum_coherence(self, state: jnp.ndarray) -> jnp.ndarray:
        """Calcula la coherencia cuántica"""
        return jnp.sum(jnp.abs(state), axis=-1) - 1.0

class QuantumConfig(LayerConfig):
    """Configuración específica para QuantumL.
    
    Args:
        num_qubits: Número de qubits
        backend: Backend cuántico preferido
        shots: Número de shots para mediciones
    """
    num_qubits: int = 4
    backend: str = "default.qubit"
    shots: int = 1000

class QuantumL(BaseLayer):
    """
    Capa cuántica avanzada para modelos de lenguaje.

    QuantumL permite la integración de operaciones cuánticas simuladas en arquitecturas de deep learning,
    soportando múltiples backends (PennyLane, Qiskit, Cirq, JAX puro) y configuraciones de qubits.
    Esta capa puede ser utilizada para enriquecer los embeddings y las representaciones internas del modelo
    con propiedades inspiradas en la computación cuántica, como la superposición, el entrelazamiento y la medición probabilística.

    Características principales:
      - Soporte para múltiples backends cuánticos (simulación).
      - Métricas detalladas de entropía, coherencia y uso de caché.
      - Ejecución eficiente y caché de resultados para grandes lotes.
      - Configuración flexible del número de qubits y shots.

    Args:
        config (QuantumConfig): Configuración de la capa cuántica, incluyendo número de qubits, backend y shots.

    Ejemplo de uso:
        >>> config = QuantumConfig(hidden_size=512, num_qubits=4, backend="default.qubit")
        >>> layer = QuantumL(config)
        >>> output = layer(x, training=True, rng=key)

    Returns:
        Dict[str, Any]: Diccionario con:
            - "output": Tensor procesado tras operaciones cuánticas.
            - "metrics": Métricas cuánticas relevantes (entropía, shots, tamaño de caché, etc.).
    """
    
    config: QuantumConfig
    
    def setup(self):
        """Inicializa QuantumL."""
        super().setup()
        
        # Dispositivo cuántico
        self.dev = qml.device(
            self.config.backend,
            wires=self.config.num_qubits,
            shots=self.config.shots
        )
        
        # Caché para resultados
        self.cache = {}
        
    def run_pennylane_enhanced(self, params: jnp.ndarray) -> jnp.ndarray:
        """Implementación mejorada de circuito cuántico.
        
        Args:
            params: Parámetros del circuito
            
        Returns:
            Tensor con resultados
        """
        @qml.qnode(self.dev, interface="jax")
        def circuit(p):
            # Rotaciones en Y y Z
            for i in range(self.config.num_qubits):
                qml.RY(p[i], wires=i)
                qml.RZ(p[i+self.config.num_qubits], wires=i)
                
            # Entrelazamiento
            for i in range(self.config.num_qubits-1):
                qml.CNOT(wires=[i, i+1])
                
            # Medición
            return qml.expval(qml.PauliZ(0))
            
        return jax.vmap(circuit)(params)
        
    def __call__(
        self,
        x: jnp.ndarray,
        training: bool = False,
        rng: Optional[jax.random.PRNGKey] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Aplica QuantumL.
        
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
            
        # Preparar parámetros
        batch_size, seq_len, _ = x.shape
        params = x.reshape(batch_size * seq_len, -1)
        
        # Verificar caché
        cache_key = jax.tree_util.tree_structure(params)
        if cache_key in self.cache:
            output = self.cache[cache_key]
        else:
            # Ejecutar circuito
            output = self.run_pennylane_enhanced(params)
            self.cache[cache_key] = output
            
        # Reshape de vuelta
        output = output.reshape(batch_size, seq_len, -1)
        
        # Métricas específicas
        metrics = {
            "quantum_ops": self.config.num_qubits * 2,  # RY + RZ
            "shots": self.config.shots,
            "cache_size": len(self.cache)
        }
        
        # Combinar con métricas base
        base_output = self._base_call(output, training=training, rng=rng)
        base_output["metrics"].update(metrics)
        
        return base_output

class QuantumLargeScaleEmbedding(nn.Module, ILayer):
    """
    Embedding cuántico para modelos de gran escala (>5TB)
    Cada parámetro simula un qubit con múltiples estados
    """
    hidden_size: int
    num_quantum_parameters: int = Field(
        ...,  # Ejemplo: 5 * 10^12 para 5TB
        description="Número de parámetros a usar como qubits"
    )
    states_per_qubit: int = Field(
        default=32,
        description="Estados posibles por qubit (16 o 32)"
    )
    chunk_size: int = 1024 * 1024  # 1M parámetros por chunk

    def setup(self):
        """Initialize model parameters and sublayers."""
        super().setup()  # Llamar al setup de ILayer primero
        
        self.total_quantum_states = self.num_quantum_parameters * self.states_per_qubit
        self.effective_qubits = self.total_quantum_states // 32
        self._setup_parameter_mapping()

    def _setup_parameter_mapping(self):
        """Configura el mapeo de parámetros a estados cuánticos"""
        self.parameter_ranges = jnp.linspace(0, 2*jnp.pi, self.states_per_qubit)
        self.basis_states = self._create_basis_states()

    def _create_basis_states(self) -> jnp.ndarray:
        """Crea estados base para la simulación"""
        states = []
        for i in range(self.states_per_qubit):
            state = jnp.zeros(self.states_per_qubit)
            state = state.at[i].set(1.0)
            states.append(state)
        return jnp.stack(states)

    @partial(jax.jit, static_argnums=(0,))
    def _process_quantum_chunk(self, chunk: jnp.ndarray) -> jnp.ndarray:
        """Procesa un chunk de parámetros como qubits"""
        # Mapear parámetros a estados cuánticos
        quantum_states = self._parameters_to_quantum_states(chunk)
        
        # Aplicar operaciones cuánticas
        quantum_states = self._apply_quantum_operations(quantum_states)
        
        # Medir y reducir dimensionalidad
        return self._measure_and_reduce(quantum_states)

    def _parameters_to_quantum_states(self, params: jnp.ndarray) -> jnp.ndarray:
        """Convierte parámetros en estados cuánticos"""
        # Discretizar parámetros a índices de estados
        indices = jnp.digitize(params, self.parameter_ranges)
        
        # Convertir a estados cuánticos
        states = jnp.take(self.basis_states, indices, axis=0)
        
        return states

    def _apply_quantum_operations(self, states: jnp.ndarray) -> jnp.ndarray:
        """Aplica operaciones cuánticas a los estados"""
        # Hadamard
        states = jnp.einsum('i,ij->ij', 
                           1/jnp.sqrt(self.states_per_qubit),
                           jnp.ones_like(states))
        
        # Fase
        phase = jnp.exp(2j * jnp.pi * jnp.arange(self.states_per_qubit) 
                       / self.states_per_qubit)
        states = states * phase
        
        return states

    def _measure_and_reduce(self, states: jnp.ndarray) -> jnp.ndarray:
        """Mide estados y reduce dimensionalidad"""
        # Calcular probabilidades
        probs = jnp.abs(states)**2
        
        # Reducir dimensionalidad manteniendo información cuántica
        reduced = jnp.mean(probs, axis=-1)
        
        return reduced

    def __call__(
        self,
        x: jnp.ndarray,
        training: bool = False,
        rng: Optional[jax.random.PRNGKey] = None,
        **kwargs
    ) -> Dict[str, Any]:
        # Procesar chunks y obtener resultado
        combined = self._process_quantum_chunk(x)
        output = nn.Dense(self.hidden_size)(combined)
        
        metrics = {
            "input_shape": x.shape,
            "output_shape": output.shape,
            "effective_qubits": self.effective_qubits
        }
        
        return {
            "output": output,
            "metrics": metrics,
            "training": training
        }

    def get_quantum_metrics(self) -> Dict[str, float]:
        """Retorna métricas cuánticas"""
        return {
            "entropy_mean": np.mean(self._quantum_metrics["entropy"]),
            "coherence_mean": np.mean(self._quantum_metrics["coherence"]),
            "effective_qubits": self.effective_qubits,
            "total_quantum_states": self.total_quantum_states
        }

class DifferentiableQuantumEmbedding(nn.Module):
    """
    Capa cuántica diferenciable que permite backpropagation
    a través de operaciones cuánticas.
    """
    hidden_size: int
    num_qubits: int
    qubit_dim: int
    backend: str = "jax"

    @partial(jax.custom_vjp)
    def quantum_forward(self, x):
        """Forward pass cuántico diferenciable"""
        if self.backend == "pennylane":
            return self._pennylane_forward(x)
        return self._default_forward(x)

    def quantum_forward_fwd(self, x):
        """Forward pass con información para gradientes"""
        y = self.quantum_forward(x)
        # Guardamos información necesaria para backward
        return y, (x, y)

    def quantum_forward_bwd(self, res, grad):
        """Backward pass personalizado"""
        x, y = res
        
        # Cálculo de gradientes personalizado según el backend
        if self.backend == "pennylane":
            return (self._pennylane_gradient(x),)
        
        # Gradiente por defecto usando JAX
        return (jax.grad(self._default_forward)(x) * grad,)

    def _pennylane_forward(self, x):
        """Forward pass usando PennyLane"""
        dev = qml.device("default.qubit", wires=self.num_qubits)
        
        @qml.qnode(dev, interface="jax")
        def circuit(inputs):
            # Codificación de amplitud
            for i in range(self.num_qubits):
                qml.RY(inputs[i], wires=i)
            
            # Entrelazamiento
            for i in range(self.num_qubits - 1):
                qml.CNOT(wires=[i, i + 1])
            
            # Medición
            return [qml.expval(qml.PauliZ(i)) for i in range(self.num_qubits)]
        
        return jax.vmap(circuit)(x)

    def _pennylane_gradient(self, x):
        """
        Cálculo de gradiente mejorado para PennyLane
        """
        def value_and_grad(params):
            value = self.run_pennylane_enhanced(params)
            return value, jax.grad(self.run_pennylane_enhanced)(params)
        
        return jax.custom_vjp(
            self.run_pennylane_enhanced,
            value_and_grad,
            lambda g, ans, x: (g,)
        )

    def _default_forward(self, x):
        """Forward pass por defecto usando JAX"""
        # Simulación de superposición
        x = jnp.sin(x) * jnp.cos(x)
        
        # Simulación de entrelazamiento
        x = self._quantum_reshape(x)
        x = jnp.fft.fft(x.astype(jnp.complex64), axis=-2)
        return jnp.real(x)

    def __call__(self, x):
        # 1. Preparación de entrada
        x = self.input_preparation(x)
        
        # 2. Forward pass cuántico diferenciable
        quantum_out = self.quantum_forward(x)
        
        # 3. Post-procesamiento
        return self.post_process(quantum_out)

    def input_preparation(self, x):
        """Prepara los inputs para el circuito cuántico"""
        # Normalización y reshape
        x = nn.LayerNorm()(x)
        return self._quantum_reshape(x)

    def post_process(self, x):
        """Post-procesa las salidas del circuito"""
        # Aplicar transformaciones finales
        x = self._quantum_restore_shape(x)
        return nn.Dense(self.hidden_size)(x)

    @property
    def gradients_available(self):
        """Verifica si los gradientes están disponibles"""
        return {
            "pennylane": True,
            "qiskit": False,  # Qiskit requiere configuración adicional
            "cirq": True,
            "jax": True
        }.get(self.backend, False)

    def _quantum_reshape(self, x):
        # Corrección para manejar batches y secuencias
        batch_size, seq_len, _ = x.shape
        return jnp.reshape(x, (batch_size, seq_len, self.num_qubits, self.qubit_dim))
    
    def _quantum_restore_shape(self, x):
        # Restauración preservando dimensiones de batch y secuencia
        batch_size, seq_len, _, _ = x.shape
        return jnp.reshape(x, (batch_size, seq_len, self.hidden_size)) 

@dataclass
class QuantumBackendMetrics:
    success_rate: float = 0.0
    error_rate: float = 0.0
    execution_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    shots: int = 0

class QuantumBackendManager:
    """Gestiona los backends cuánticos y sus métricas"""
    def __init__(self, config: VQbitConfig):
        self.config = config
        self.metrics: Dict[str, QuantumBackendMetrics] = {}
        self._init_backends()

    def _init_backends(self):
        """Inicializa los backends disponibles"""
        self.available_backends = {}
        self.metrics = {
            "qiskit": QuantumBackendMetrics(),
            "cirq": QuantumBackendMetrics(),
            "pennylane": QuantumBackendMetrics()
        }

class EnhancedQuantumEmbedding:
    def __init__(self, 
                 num_qubits: int = 8,
                 states_per_qubit: int = 32,
                 backend_priority: Optional[Dict[str, float]] = None):
        self.num_qubits = num_qubits
        self.states_per_qubit = states_per_qubit
        self.backend_priority = backend_priority or {
            "qiskit": 1.0,
            "cirq": 0.8,
            "pennylane": 0.7
        }
        self._result_cache: Dict[int, jnp.ndarray] = {}  # Inicializar el caché
        self._previous_output: Optional[jnp.ndarray] = None  # Inicializar output anterior
        self._init_metrics()

    def _init_metrics(self):
        """Inicializa métricas de rendimiento"""
        self.metrics = {backend: QuantumBackendMetrics() for backend in self.backend_priority}
        self.current_backend = self._select_optimal_backend()

    def _quantum_transform_qiskit(self, x: jnp.ndarray) -> jnp.ndarray:
        """
        Transformación cuántica usando Qiskit con optimizaciones
        """
        try:
            from qiskit import QuantumCircuit, Aer, transpile, execute #type: ignore
            from qiskit.quantum_info import Statevector #type: ignore
            from qiskit.providers.aer import QasmSimulator #type: ignore
            import time

            start_time = time.time()
            backend = Aer.get_backend('aer_simulator')
            results = []

            for batch in x:
                # Crear circuito
                circ = QuantumCircuit(self.num_qubits)
                
                # Codificación de amplitud
                for i in range(self.num_qubits):
                    circ.ry(float(batch[i]), i)
                    circ.rz(float(batch[i]), i)
                
                # Entrelazamiento
                for i in range(self.num_qubits - 1):
                    circ.cx(i, i + 1)
                
                # Optimización del circuito
                circ = transpile(circ, backend, optimization_level=3)
                
                # Simulación
                if self.states_per_qubit == 32:
                    # Usar simulación de estado vectorial para más precisión
                    state = Statevector.from_instruction(circ)
                    probs = state.probabilities()
                else:
                    # Simulación más rápida para 16 estados
                    job = execute(circ, backend, shots=1000)
                    counts = job.result().get_counts()
                    probs = self._counts_to_probabilities(counts)
                
                results.append(probs[:self.num_qubits])

            # Actualizar métricas
            execution_time = (time.time() - start_time) * 1000
            self.metrics["qiskit"].execution_time_ms = execution_time
            self.metrics["qiskit"].shots += len(x)

            return jnp.array(results)

        except ImportError:
            logger.error("Qiskit no está instalado")
            return self._fallback_transform(x)

    def _quantum_transform_cirq(self, x: jnp.ndarray) -> jnp.ndarray:
        """
        Transformación cuántica usando Cirq con optimizaciones
        """
        try:
            import cirq #type: ignore #type: ignore
            import time

            start_time = time.time()
            qubits = cirq.LineQubit.range(self.num_qubits)
            results = []

            for batch in x:
                # Crear circuito
                circuit = cirq.Circuit()
                
                # Codificación de estados
                for i, q in enumerate(qubits):
                    circuit.append([
                        cirq.ry(batch[i])(q),
                        cirq.rz(batch[i])(q)
                    ])
                
                # Entrelazamiento optimizado
                for i in range(self.num_qubits - 1):
                    circuit.append(cirq.CNOT(qubits[i], qubits[i + 1]))
                
                # Optimización del circuito
                circuit = cirq.optimize_for_target_gateset(circuit)
                
                # Simulación
                if self.states_per_qubit == 32:
                    simulator = cirq.Simulator(dtype=np.complex128)
                else:
                    simulator = cirq.Simulator(dtype=np.complex64)
                
                result = simulator.simulate(circuit)
                state_vector = result.final_state_vector
                results.append(np.abs(state_vector[:self.num_qubits]))

            # Actualizar métricas
            execution_time = (time.time() - start_time) * 1000
            self.metrics["cirq"].execution_time_ms = execution_time
            self.metrics["cirq"].shots += len(x)

            return jnp.array(results)

        except ImportError:
            logger.error("Cirq no está instalado")
            return self._fallback_transform(x)

    def _quantum_transform_pennylane(self, x: jnp.ndarray) -> jnp.ndarray:
        """
        Transformación cuántica usando PennyLane con soporte JAX
        """
        try:
            from pennylane import numpy as pnp
            import time

            start_time = time.time()
            
            # Dispositivo cuántico
            dev = qml.device("default.qubit", wires=self.num_qubits)
            
            @qml.qnode(dev, interface="jax")
            def quantum_circuit(inputs):
                # Codificación
                for i in range(self.num_qubits):
                    qml.RY(inputs[i], wires=i)
                    qml.RZ(inputs[i], wires=i)
                
                # Entrelazamiento
                for i in range(self.num_qubits - 1):
                    qml.CNOT(wires=[i, i + 1])
                
                # Mediciones
                return [qml.expval(qml.PauliZ(i)) for i in range(self.num_qubits)]

            # Procesamiento por lotes
            results = jax.vmap(quantum_circuit)(x)
            
            # Actualizar métricas
            execution_time = (time.time() - start_time) * 1000
            self.metrics["pennylane"].execution_time_ms = execution_time
            self.metrics["pennylane"].shots += len(x)

            return results

        except ImportError:
            logger.error("PennyLane no está instalado")
            return self._fallback_transform(x)

    def _fallback_transform(self, x: jnp.ndarray) -> jnp.ndarray:
        """Transformación fallback usando JAX puro"""
        logger.warning("Usando transformación fallback")
        return jnp.sin(x) * jnp.cos(x)

    def _select_optimal_backend(self) -> str:
        """Selecciona el mejor backend basado en métricas"""
        scores = {}
        for backend, metrics in self.metrics.items():
            if metrics.shots == 0:
                continue
                
            speed_score = 1.0 / (1.0 + metrics.execution_time_ms/1000.0)
            error_score = 1.0 - metrics.error_rate
            priority = self.backend_priority[backend]
            
            scores[backend] = (speed_score * 0.4 + error_score * 0.6) * priority
        
        return max(scores.items(), key=lambda x: x[1])[0] if scores else "qiskit"

    def _counts_to_probabilities(self, counts: Dict[str, int]) -> np.ndarray:
        """Convierte conteos en probabilidades"""
        total = sum(counts.values())
        return np.array([counts.get(format(i, f'0{self.num_qubits}b'), 0) / total 
                        for i in range(2**self.num_qubits)])

    def get_backend_methods(self) -> Dict[str, Any]:
        """Retorna los métodos de transformación disponibles"""
        return {
            "qiskit": self._quantum_transform_qiskit,
            "cirq": self._quantum_transform_cirq,
            "pennylane": self._quantum_transform_pennylane
        }

    def get_metrics(self) -> Dict[str, QuantumBackendMetrics]:
        """Retorna métricas de todos los backends"""
        return self.metrics

    def quantum_transform(self, x: jnp.ndarray) -> jnp.ndarray:
        """
        Transformación cuántica principal con selección dinámica de backend
        """
        # Verificar cache
        cache_key = hash(x.tobytes())
        if cache_key in self._result_cache:
            return self._result_cache[cache_key]

        # Seleccionar backend basado en métricas actuales
        if self.current_backend == "pennylane":
            result, grad = self._pennylane_gradient(x)
        elif self.current_backend == "qiskit":
            result, grad = self._qiskit_gradient(x)
        elif self.current_backend == "cirq":
            result, grad = self._cirq_gradient(x)
        else:
            result = self._jax_quantum_transform(x)
            grad = None

        # Guardar en cache
        self._result_cache[cache_key] = result
        return result

    def _pennylane_gradient(self, x: jnp.ndarray) -> Tuple[jnp.ndarray, jnp.ndarray]:
        """
        Cálculo de gradiente usando PennyLane con soporte JAX
        """
        import pennylane as qml
        
        # Configurar dispositivo cuántico
        dev = qml.device("default.qubit", wires=self.num_qubits)
        
        @qml.qnode(dev, interface="jax")
        def quantum_circuit(params):
            # Codificación de parámetros
            for i in range(self.num_qubits):
                qml.RY(params[i], wires=i)
                qml.RZ(params[i + self.num_qubits], wires=i)
            
            # Capa de entrelazamiento
            for i in range(self.num_qubits - 1):
                qml.CNOT(wires=[i, i + 1])
            
            # Rotaciones controladas
            for i in range(self.num_qubits - 1):
                qml.CRY(params[2*i], wires=[i, i+1])
                qml.CRZ(params[2*i + 1], wires=[i, i+1])
            
            # Mediciones en diferentes bases
            return [
                qml.expval(qml.PauliZ(i)) for i in range(self.num_qubits)
            ] + [
                qml.expval(qml.PauliX(i)) for i in range(self.num_qubits)
            ]

        # Cálculo de valor y gradiente
        value_and_grad_fn = jax.value_and_grad(quantum_circuit)
        value, grad = value_and_grad_fn(x)
        
        return value, grad

    def _qiskit_gradient(self, x: jnp.ndarray) -> Tuple[jnp.ndarray, jnp.ndarray]:
        """
        Cálculo de gradiente usando Qiskit con diferenciación automática
        """
        from qiskit import QuantumCircuit, Aer
        from qiskit.circuit import Parameter  # type: ignore
        from qiskit.quantum_info import Statevector
        
        def create_parameterized_circuit():
            circuit = QuantumCircuit(self.num_qubits)
            params = []
            
            # Crear parámetros
            for i in range(2 * self.num_qubits):
                params.append(Parameter(f'θ_{i}'))
            
            # Codificación de parámetros
            for i in range(self.num_qubits):
                circuit.ry(params[i], i)
                circuit.rz(params[i + self.num_qubits], i)
            
            # Entrelazamiento
            for i in range(self.num_qubits - 1):
                circuit.cx(i, i + 1)
            
            return circuit, params

        # Crear circuito parametrizado
        circuit, params = create_parameterized_circuit()
        backend = Aer.get_backend('statevector_simulator')
        
        def evaluate_circuit(param_values):
            # Asignar valores a parámetros
            parameter_dict = dict(zip(params, param_values))
            bound_circuit = circuit.bind_parameters(parameter_dict)
            
            # Simular
            state = Statevector.from_instruction(bound_circuit)
            return jnp.array(state.data)

        # Cálculo numérico del gradiente
        eps = 1e-7
        value = evaluate_circuit(x)
        grads = []
        
        for i in range(len(x)):
            x_plus = x.at[i].add(eps)
            x_minus = x.at[i].add(-eps)
            grad_i = (evaluate_circuit(x_plus) - evaluate_circuit(x_minus)) / (2 * eps)
            grads.append(grad_i)
        
        return value, jnp.stack(grads)

    def _cirq_gradient(self, x: jnp.ndarray) -> Tuple[jnp.ndarray, jnp.ndarray]:
        """
        Cálculo de gradiente usando Cirq con diferenciación automática
        """
        import cirq
        
        # Crear qubits
        qubits = cirq.LineQubit.range(self.num_qubits)
        
        def create_circuit(params):
            circuit = cirq.Circuit()
            
            # Codificación de parámetros
            for i, qubit in enumerate(qubits):
                circuit.append([
                    cirq.ry(params[i])(qubit),
                    cirq.rz(params[i + self.num_qubits])(qubit)
                ])
            
            # Entrelazamiento
            for i in range(len(qubits) - 1):
                circuit.append(cirq.CNOT(qubits[i], qubits[i + 1]))
                
            # Rotaciones controladas
            for i in range(len(qubits) - 1):
                circuit.append([
                    cirq.ControlledGate(cirq.ry(params[2*i]))(qubits[i], qubits[i+1]),
                    cirq.ControlledGate(cirq.rz(params[2*i + 1]))(qubits[i], qubits[i+1])
                ])
            
            return circuit

        def simulate_circuit(params):
            circuit = create_circuit(params)
            simulator = cirq.Simulator()
            result = simulator.simulate(circuit)
            return jnp.array(result.final_state_vector)

        # Cálculo de gradiente usando JAX
        value_and_grad_fn = jax.value_and_grad(
            lambda p: jnp.sum(jnp.abs(simulate_circuit(p)))
        )
        value, grad = value_and_grad_fn(x)
        
        return value, grad

    @partial(jax.jit, static_argnums=(0,))
    def quantum_forward(self, x: jnp.ndarray) -> jnp.ndarray:
        """
        Forward pass cuántico optimizado con JIT y métricas
        """
        start_time = time.time()
        
        # Transformación principal
        result = self.quantum_transform(x)
        
        # Calcular métricas
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        
        # Actualizar métricas del backend actual
        self.metrics[self.current_backend].execution_time_ms = execution_time
        self.metrics[self.current_backend].shots += 1
        
        # Calcular error (si hay valor previo disponible)
        if hasattr(self, '_previous_output'):
            error = float(jnp.mean(jnp.abs(result - self._previous_output)))
            self.metrics[self.current_backend].error_rate = error
        
        self._previous_output = result
        
        return result

    def _jax_quantum_transform(self, x: jnp.ndarray) -> jnp.ndarray:
        """
        Transformación cuántica usando JAX como backend por defecto
        """
        # Simulación básica de operaciones cuánticas usando JAX
        x = jnp.sin(x) * jnp.cos(x)  # Simulación de superposición
        x = jnp.fft.fft(x, axis=-1)  # Simulación de entrelazamiento
        return jnp.real(x)

# Ejemplo de uso
if __name__ == "__main__":
    # Configuración
    embedding = EnhancedQuantumEmbedding(
        num_qubits=4,
        states_per_qubit=32,
        backend_priority={
            "qiskit": 1.0,
            "cirq": 0.8,
            "pennylane": 0.7
        }
    )

    # Datos de prueba
    test_data = jnp.array([[0.1, 0.2, 0.3, 0.4]])
    
    # Probar cada backend
    backends = embedding.get_backend_methods()
    for name, transform in backends.items():
        try:
            result = transform(test_data)
            print(f"{name} resultado:", result.shape)
            metrics = embedding.metrics[name]
            print(f"{name} tiempo: {metrics.execution_time_ms:.2f}ms")
        except Exception as e:
            print(f"{name} error:", str(e)) 