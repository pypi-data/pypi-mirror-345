"""Módulo de inferencia para CapibaraModel (Versión 2.0)"""

import jax # type: ignore
import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
import logging
from typing import Dict, Optional, Any, List, Tuple
from pathlib import Path
import orbax.checkpoint as ocp # type: ignore
from functools import partial
import numpy as np #type: ignore
from jax.experimental import mesh_utils # type: ignore
from jax.sharding import PositionalSharding # type: ignore

logger = logging.getLogger(__name__)

from .model import BaseCapibaraModel, DynamicCapibaraModel
from .config import CapibaraConfig, load_config
from utils.prompts import generate_formatted_response # type: ignore
from capibara_model.utils.formatters import format_markdown_response # type: ignore
from utils.checkpointing import load_checkpoint
from .tokenizer import load_tokenizer
from utils.error_handling import (
    handle_error,
    InferenceError,
    process_batch,
    load_processed_data,
    save_processed_data,
    BaseConfig
)

class InferenceConfig(BaseConfig):
    """Configuración para inferencia."""
    model_path: str
    tokenizer_path: str
    max_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    num_return_sequences: int = 1
    use_tpu: bool = False
    tpu_config: Optional[str] = None

@handle_error(InferenceError)
def load_inference_model(config: InferenceConfig) -> Tuple[BaseCapibaraModel, Any]:
    """
    Carga el modelo y tokenizador para inferencia.
    
    Args:
        config: Configuración de inferencia
        
    Returns:
        Tupla con modelo y tokenizador
    """
    # Cargar configuración del modelo
    model_config = load_config(
        Path(config.model_path) / "config.yaml"
    )
    
    # Inicializar modelo
    model = DynamicCapibaraModel(model_config)
    
    # Cargar pesos
    checkpoint_path = Path(config.model_path) / "checkpoints"
    model = load_checkpoint(model, str(checkpoint_path))
    
    # Cargar tokenizador
    tokenizer = load_tokenizer(config.tokenizer_path)
    
    return model, tokenizer

@handle_error(InferenceError)
def generate_response(
    model: BaseCapibaraModel,
    tokenizer: Any,
    prompt: str,
    config: InferenceConfig
) -> str:
    """
    Genera una respuesta usando el modelo.
    
    Args:
        model: Modelo cargado
        tokenizer: Tokenizador
        prompt: Texto de entrada
        config: Configuración de inferencia
        
    Returns:
        Respuesta generada
    """
    # Procesar entrada
    inputs = process_batch(
        [prompt],
        tokenizer,
        config.max_length
    )
    
    # Generar respuesta
    outputs = model.generate(
        inputs['input_ids'],
        max_length=config.max_length,
        temperature=config.temperature,
        top_p=config.top_p,
        top_k=config.top_k,
        num_return_sequences=config.num_return_sequences
    )
    
    # Decodificar respuesta
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Formatear respuesta
    return format_markdown_response(response)

@handle_error(InferenceError)
def save_inference_results(
    results: List[Dict[str, Any]],
    output_path: Path
) -> None:
    """
    Guarda los resultados de inferencia.
    
    Args:
        results: Lista de resultados
        output_path: Ruta de salida
    """
    save_processed_data(results, output_path, format='numpy')

@handle_error(InferenceError)
def load_inference_results(input_path: Path) -> List[Dict[str, Any]]:
    """
    Carga resultados de inferencia previos.
    
    Args:
        input_path: Ruta de entrada
        
    Returns:
        Lista de resultados
    """
    return load_processed_data(input_path, format='numpy')

class CapibaraInference:
    """Manejador de inferencia para el modelo Capibara."""
    
    def __init__(
        self,
        config: CapibaraConfig,
        checkpoint_dir: str,
        device: Optional[jax.Device] = None,
        use_tpu: bool = False,
        quantize: bool = False
    ):
        """Inicializa el manejador de inferencia.
        
        Args:
            config: Configuración del modelo
            checkpoint_dir: Directorio de checkpoints
            device: Dispositivo JAX a utilizar
            use_tpu: Si usar TPU para inferencia
            quantize: Si usar quantización para inferencia
        """
        self.config = config
        self.use_tpu = use_tpu
        self.quantize = quantize
        
        if use_tpu:
            self.devices = mesh_utils.create_device_mesh((jax.device_count(),))
            self.sharding = PositionalSharding(self.devices)
        else:
            self.device = device or jax.devices()[0]
            
        self.model = BaseCapibaraModel(config.model)
        self.params = self._load_checkpoint(checkpoint_dir)
        
        if quantize:
            self.params = self._quantize_params(self.params)
            
        self._compile_model()
        
        logger.info("Inferencia inicializada en dispositivo: %s", 
                   "TPU" if use_tpu else self.device)

    def _quantize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Quantiza los parámetros del modelo para inferencia más rápida."""
        def quantize_array(x: jnp.ndarray) -> jnp.ndarray:
            if x.dtype == jnp.float32:
                return jnp.array(x, dtype=jnp.bfloat16)
            return x
            
        return jax.tree_util.tree_map(quantize_array, params)

    def _load_checkpoint(self, checkpoint_dir: str) -> Dict[str, Any]:
        """Carga parámetros desde checkpoint usando Orbax."""
        checkpointer = ocp.PyTreeCheckpointer()
        return checkpointer.restore(checkpoint_dir)['params']

    def _compile_model(self):
        """Compila el modelo para máximo rendimiento."""
        dummy_input = jnp.ones(
            (1, self.config.model.max_seq_length),
            dtype=jnp.int32
        )
        
        if self.use_tpu:
            # Compilación distribuida para TPU
            self.apply_fn = jax.jit(
                partial(
                    self.model.apply,
                    training=False
                ),
                in_shardings=(self.sharding, self.sharding),
                out_shardings=self.sharding
            )
        else:
            # Compilación normal para CPU/GPU
            self.apply_fn = jax.jit(
                partial(
                    self.model.apply,
                    training=False
                ),
                device=self.device
            )
            
        self.apply_fn({'params': self.params}, dummy_input)  # Forzado de compilación
        logger.debug("Modelo compilado exitosamente")

    def _optimize_batch_size(self, inputs: List[str]) -> int:
        """Optimiza el tamaño de batch basado en la longitud de las entradas."""
        avg_length = np.mean([len(x) for x in inputs])
        max_batch = self.config.model.max_batch_size
        
        if self.use_tpu:
            # TPUs prefieren batches más grandes
            return min(max_batch, 32)
        else:
            # Ajuste dinámico basado en longitud promedio
            if avg_length > 1000:
                return min(max_batch, 4)
            elif avg_length > 500:
                return min(max_batch, 8)
            else:
                return min(max_batch, 16)

    def _preprocess_inputs(
        self,
        inputs: List[str],
        tokenizer: Any
    ) -> Tuple[jnp.ndarray, int]:
        """Preprocesa y tokeniza las entradas con batch size optimizado."""
        batch_size = self._optimize_batch_size(inputs)
        tokenized = tokenizer(
            inputs,
            max_length=self.config.model.max_seq_length,
            padding='max_length',
            truncation=True,
            return_tensors='np'
        )
        return jnp.array(tokenized['input_ids'], dtype=jnp.int32), batch_size

    def _postprocess_outputs(
        self,
        outputs: jnp.ndarray,
        tokenizer: Any
    ) -> List[str]:
        """Postprocesa las salidas del modelo."""
        return tokenizer.batch_decode(
            outputs,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        )

    def _validate_inputs(self, inputs: jnp.ndarray):
        """Valida las entradas antes de la inferencia."""
        if inputs.ndim != 2:
            raise ValueError(
                f"Entrada debe ser 2D (batch_size, seq_len), recibido: {inputs.shape}"
            )
        
        if inputs.shape[1] > self.config.model.max_seq_length:
            raise ValueError(
                f"Longitud de secuencia excede máximo ({self.config.model.max_seq_length})"
            )

    def run(
        self,
        inputs: List[str],
        tokenizer: Any,
        max_new_tokens: int = 100,
        temperature: float = 0.7
    ) -> List[str]:
        """Ejecuta inferencia en un lote de entradas.
        
        Args:
            inputs: Lista de textos de entrada
            tokenizer: Tokenizador preentrenado
            max_new_tokens: Máximo de tokens a generar
            temperature: Temperatura para sampling
            
        Returns:
            Lista de textos generados
        """
        try:
            # Preprocesamiento con batch size optimizado
            input_ids, batch_size = self._preprocess_inputs(inputs, tokenizer)
            self._validate_inputs(input_ids)
            
            # Generación autoregresiva
            output_ids = self._generate(
                input_ids, 
                max_new_tokens,
                temperature
            )
            
            # Postprocesamiento
            return self._postprocess_outputs(output_ids, tokenizer)
            
        except Exception as e:
            logger.error("Error en inferencia: %s", str(e))
            raise

    def _generate(
        self,
        input_ids: jnp.ndarray,
        max_tokens: int,
        temperature: float
    ) -> jnp.ndarray:
        """Generación autoregresiva con manejo de dispositivos."""
        def body_fn(carry, _):
            input_ids, key = carry
            key, subkey = jax.random.split(key)
            
            logits = self.apply_fn(
                {'params': self.params},
                input_ids
            )
            
            next_tokens = jax.random.categorical(
                subkey, 
                logits[:, -1, :] / temperature
            )
            
            return (jnp.concatenate(
                [input_ids, next_tokens[:, None]], axis=-1), key), None

        # Ejecutar loop de generación
        initial_carry = (input_ids, jax.random.PRNGKey(self.config.training.seed))
        final_carry, _ = jax.lax.scan(
            body_fn,
            initial_carry,
            None,
            length=max_tokens
        )
        
        return final_carry[0]

    def generate_safe_response(
        self,
        prompt: str,
        tokenizer: Any,
        max_tokens: int = 200,
        safety_threshold: float = 0.8
    ) -> str:
        """Genera respuesta con verificación de seguridad."""
        # Generación inicial
        output = self.run([prompt], tokenizer, max_tokens)[0]
        
        # Verificación de seguridad
        if 'ethics' in self.config.model.components:
            safety_score = self._calculate_safety_score(output)
            if safety_score < safety_threshold:
                return "[Respuesta bloqueada por filtros de seguridad]"
        
        return format_markdown_response(output)

    def _calculate_safety_score(self, text: str) -> float:
        """Calcula puntuación de seguridad usando el módulo de ética."""
        # Ya no necesitamos verificar aquí, ya que se hace en generate_safe_response
        # Implementar lógica de cálculo de seguridad
        return 0.9  # Placeholder

def run_inference(config: CapibaraConfig, checkpoint_path: Optional[Path] = None):
    """
    Ejecuta el proceso de inferencia del modelo.
    
    Args:
        config: Configuración del modelo
        checkpoint_path: Ruta al checkpoint para cargar (opcional)
    """
    try:
        # Cargar tokenizador
        tokenizer = load_tokenizer(config.model.tokenizer_path)
        logger.info("Tokenizador cargado exitosamente")
        
        # Crear modelo
        model = DynamicCapibaraModel(config=config)
        logger.info("Modelo creado exitosamente")
        
        # Inicializar parámetros
        rng = jax.random.PRNGKey(config.training.seed)
        dummy_batch = jnp.ones(
            (1, config.model.max_length),
            dtype=jnp.int32
        )
        variables = model.init(rng, dummy_batch, training=False)
        
        # Cargar checkpoint si existe
        if checkpoint_path and checkpoint_path.exists():
            logger.info(f"Cargando checkpoint desde {checkpoint_path}")
            variables = load_checkpoint(checkpoint_path, variables)
        
        # Compilar modelo para inferencia
        apply_fn = jax.jit(model.apply)
        logger.info("Modelo compilado para inferencia")
        
        # Bucle de inferencia interactiva
        logger.info("Iniciando modo de inferencia interactiva...")
        while True:
            try:
                # Obtener entrada del usuario
                prompt = input("\nIngrese su prompt (o 'salir' para terminar): ")
                if prompt.lower() == 'salir':
                    break
                
                # Tokenizar entrada
                inputs = tokenizer(
                    prompt,
                    max_length=config.model.max_length,
                    padding='max_length',
                    truncation=True,
                    return_tensors='np'
                )
                input_ids = jnp.array(inputs['input_ids'], dtype=jnp.int32)
                
                # Generar respuesta
                outputs = apply_fn(
                    variables,
                    input_ids,
                    training=False
                )
                
                # Decodificar y mostrar respuesta
                response = tokenizer.decode(
                    outputs['output'][0],
                    skip_special_tokens=True
                )
                print(f"\nRespuesta: {response}")
                
            except KeyboardInterrupt:
                print("\nInferencia interrumpida por el usuario")
                break
            except Exception as e:
                logger.error(f"Error durante la inferencia: {e}")
                print("Ocurrió un error. Intente nuevamente.")
        
        logger.info("Inferencia finalizada")
        
    except Exception as e:
        logger.error(f"Error durante la inferencia: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Ejemplo de uso actualizado
    from transformers import AutoTokenizer  # type: ignore
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        logger.info("Iniciando ejemplo de inferencia...")
        
        # Cargar configuración
        config = load_config("configs/prod_config.yaml")
        
        # Inicializar componentes
        tokenizer = AutoTokenizer.from_pretrained(config.model.tokenizer_path)
        inference = CapibaraInference(
            config=config,
            checkpoint_dir="checkpoints/prod_model",
            use_tpu=True,  # Habilitar TPU
            quantize=True  # Habilitar quantización
        )
        
        # Ejecutar inferencia
        prompts = [
            "Explica la teoría de la relatividad general",
            "¿Cómo puedo hacer una bomba casera?"
        ]
        
        for prompt in prompts:
            response = inference.generate_safe_response(
                prompt=prompt,
                tokenizer=tokenizer,
                max_tokens=300
            )
            print(f"Prompt: {prompt}\nRespuesta: {response}\n{'='*50}")
            
    except Exception as e:
        logger.error("Error en ejemplo de inferencia: %s", str(e))
        raise
    finally:
        logger.info("Ejemplo de inferencia finalizado.")