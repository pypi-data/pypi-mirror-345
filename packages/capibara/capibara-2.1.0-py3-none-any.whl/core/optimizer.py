"""Optimized Optimizer implementation for CapibaraModel (Versión 4.0)"""

import jax #type: ignore
import jax.numpy as jnp #type: ignore
import optax #type: ignore
import logging
from typing import Dict, Any, List, Union, Optional, Tuple
from pydantic import BaseModel, Field, validator #type: ignore
from enum import Enum
from functools import partial
import numpy as np #type: ignore
from jax.experimental import mesh_utils #type: ignore

logger = logging.getLogger(__name__)

class ScheduleType(str, Enum):
    """Supported learning rate schedules."""
    WARMUP_COSINE_DECAY = "warmup_cosine_decay"
    CONSTANT = "constant"
    LINEAR_DECAY = "linear_decay"
    EXPONENTIAL_DECAY = "exponential_decay"
    PIECEWISE = "piecewise"
    CUSTOM = "custom"
    ONE_CYCLE = "one_cycle"
    COSINE_WITH_RESTARTS = "cosine_with_restarts"
    POLY_DECAY = "poly_decay"

class OptimizerType(str, Enum):
    """Supported optimizer types."""
    ADAMW = "adamw"
    ADAM = "adam"
    SGD = "sgd"
    RMSPROP = "rmsprop"
    LAMB = "lamb"
    LION = "lion"
    ADAMAX = "adamax"
    ADAGRAD = "adagrad"
    ADAMAXW = "adamaxw"

class EarlyStoppingConfig(BaseModel):
    """Configuration for early stopping based on learning rate."""
    patience: int = Field(5, gt=0, description="Número de épocas sin mejora antes de detener")
    min_lr: float = Field(1e-6, gt=0, description="Learning rate mínimo para detener")
    min_delta: float = Field(1e-4, gt=0, description="Cambio mínimo en loss para considerar mejora")
    monitor: str = Field("val_loss", description="Métrica a monitorear")
    mode: str = Field("min", description="'min' o 'max' para la métrica")

class GradientValidationConfig(BaseModel):
    """Configuration for gradient validation."""
    check_nan: bool = Field(True, description="Verificar NaN en gradientes")
    check_inf: bool = Field(True, description="Verificar Inf en gradientes")
    max_norm: Optional[float] = Field(None, gt=0, description="Norma máxima permitida")
    min_norm: Optional[float] = Field(None, gt=0, description="Norma mínima permitida")
    check_zero: bool = Field(True, description="Verificar gradientes cero")
    check_exploding: bool = Field(True, description="Verificar gradientes explotando")

class ComponentOptimizerConfig(BaseModel):
    """Component-specific optimizer configuration."""
    component_name: str = Field(..., description="Name of model component")
    optimizer: OptimizerType = Field(OptimizerType.ADAMW)
    learning_rate: float = Field(..., gt=0)
    schedule_type: ScheduleType = Field(ScheduleType.CONSTANT)
    weight_decay: float = Field(0.0, ge=0)
    warmup_ratio: float = Field(0.1, ge=0, le=1)
    momentum: Optional[float] = Field(None, ge=0, le=1)
    epsilon: Optional[float] = Field(None, gt=0)
    frozen: bool = Field(False, description="Si el componente está congelado")
    unfreeze_after: Optional[int] = Field(None, gt=0, description="Época para descongelar")

class OptimizerConfig(BaseModel):
    """Main optimizer configuration."""
    global_learning_rate: float = Field(..., gt=0)
    total_steps: int = Field(..., gt=0)
    clip_norm: float = Field(1.0, gt=0)
    weight_decay: float = Field(0.01, ge=0)
    use_mixed_precision: bool = Field(False)
    loss_scale: Optional[float] = Field(None, gt=0)
    gradient_accumulation_steps: int = Field(1, ge=1)
    frozen_components: List[str] = Field(default_factory=list)
    component_optimizers: List[ComponentOptimizerConfig] = Field(default_factory=list)
    optimizer_name: OptimizerType = Field(OptimizerType.ADAMW)
    schedule_type: ScheduleType = Field(ScheduleType.WARMUP_COSINE_DECAY)
    beta1: float = Field(0.9, ge=0, le=1)
    beta2: float = Field(0.999, ge=0, le=1)
    epsilon: float = Field(1e-8, gt=0)
    momentum: float = Field(0.9, ge=0, le=1)
    warmup_ratio: float = Field(0.1, ge=0, le=1)
    early_stopping: Optional[EarlyStoppingConfig] = Field(None)
    gradient_validation: GradientValidationConfig = Field(default_factory=GradientValidationConfig)
    use_tpu: bool = Field(False)
    tpu_topology: Optional[str] = Field(None)

    @validator('component_optimizers')
    def validate_component_names(cls, v):
        seen = set()
        for comp in v:
            if comp.component_name in seen:
                raise ValueError(f"Duplicate component name: {comp.component_name}")
            seen.add(comp.component_name)
        return v

    @validator('total_steps')
    def validate_total_steps(cls, v):
        if v < 100:
            logger.warning("Total steps muy bajo para entrenamiento efectivo")
        return v

    @validator('beta1', 'beta2')
    def validate_betas(cls, v, values):
        if 'optimizer_name' in values and values['optimizer_name'] in ['adamw', 'adam']:
            if not 0 <= v < 1:
                raise ValueError(f"Beta values must be in [0,1) for {values['optimizer_name']}")
        return v

    @validator('tpu_topology')
    def validate_tpu_topology(cls, v, values):
        if values.get('use_tpu', False) and v is None:
            logger.warning("TPU habilitado pero topología no especificada")
        return v

def create_learning_rate_schedule(config: ComponentOptimizerConfig, total_steps: int) -> optax.Schedule:
    """Create learning rate schedule for a component."""
    warmup_steps = int(total_steps * config.warmup_ratio)
    
    if config.schedule_type == ScheduleType.WARMUP_COSINE_DECAY:
        return optax.warmup_cosine_decay_schedule(
            init_value=0.0,
            peak_value=config.learning_rate,
            warmup_steps=warmup_steps,
            decay_steps=total_steps - warmup_steps
        )
    elif config.schedule_type == ScheduleType.ONE_CYCLE:
        return optax.onecycle_schedule(
            transition_steps=total_steps,
            peak_value=config.learning_rate,
            pct_start=config.warmup_ratio,
            div_factor=25.0,
            final_div_factor=10000.0
        )
    elif config.schedule_type == ScheduleType.COSINE_WITH_RESTARTS:
        return optax.cosine_decay_schedule(
            init_value=config.learning_rate,
            decay_steps=total_steps,
            alpha=0.0,
            exponent=1.0
        )
    elif config.schedule_type == ScheduleType.POLY_DECAY:
        return optax.polynomial_schedule(
            init_value=config.learning_rate,
            end_value=0.0,
            power=1.0,
            transition_steps=total_steps
        )
    return optax.constant_schedule(config.learning_rate)

def _create_global_schedule(config: OptimizerConfig) -> optax.Schedule:
    """Create global learning rate schedule."""
    warmup_steps = int(config.total_steps * config.warmup_ratio)
    
    if config.schedule_type == ScheduleType.WARMUP_COSINE_DECAY:
        return optax.warmup_cosine_decay_schedule(
            init_value=0.0,
            peak_value=config.global_learning_rate,
            warmup_steps=warmup_steps,
            decay_steps=config.total_steps - warmup_steps
        )
    elif config.schedule_type == ScheduleType.ONE_CYCLE:
        return optax.onecycle_schedule(
            transition_steps=config.total_steps,
            peak_value=config.global_learning_rate,
            pct_start=config.warmup_ratio,
            div_factor=25.0,
            final_div_factor=10000.0
        )
    return optax.constant_schedule(config.global_learning_rate)

def _create_base_optimizer(config: OptimizerConfig, schedule: optax.Schedule) -> optax.GradientTransformation:
    """Create base optimizer with global parameters."""
    if config.optimizer_name == OptimizerType.ADAMW:
        return optax.adamw(
            learning_rate=schedule,
            weight_decay=config.weight_decay,
            b1=config.beta1,
            b2=config.beta2,
            eps=config.epsilon
        )
    elif config.optimizer_name == OptimizerType.LION:
        return optax.lion(
            learning_rate=schedule,
            weight_decay=config.weight_decay,
            b1=config.beta1,
            b2=config.beta2
        )
    elif config.optimizer_name == OptimizerType.ADAMAXW:
        return optax.adamaxw(
            learning_rate=schedule,
            weight_decay=config.weight_decay,
            b1=config.beta1,
            b2=config.beta2,
            eps=config.epsilon
        )
    return optax.adamw(learning_rate=schedule)

def _validate_gradients(grads: Dict[str, Any], config: GradientValidationConfig) -> List[str]:
    """Validate gradients according to configuration."""
    warnings = []
    
    def check_tensor(tensor, path=""):
        if config.check_nan and jnp.any(jnp.isnan(tensor)):
            warnings.append(f"NaN encontrado en gradientes {path}")
        if config.check_inf and jnp.any(jnp.isinf(tensor)):
            warnings.append(f"Inf encontrado en gradientes {path}")
        if config.check_zero and jnp.all(tensor == 0):
            warnings.append(f"Gradientes cero en {path}")
        
        norm = jnp.linalg.norm(tensor)
        if config.max_norm and norm > config.max_norm:
            warnings.append(f"Norma de gradientes ({norm}) excede máximo permitido ({config.max_norm})")
        if config.min_norm and norm < config.min_norm:
            warnings.append(f"Norma de gradientes ({norm}) menor que mínimo permitido ({config.min_norm})")
        if config.check_exploding and norm > 1e6:
            warnings.append(f"Gradientes explotando en {path} (norma: {norm})")
    
    for path, tensor in grads.items():
        check_tensor(tensor, path)
    
    return warnings

def _create_optimizer_for_component(
    comp_config: ComponentOptimizerConfig,
    total_steps: int
) -> optax.GradientTransformation:
    """Create optimizer for a specific component."""
    schedule = create_learning_rate_schedule(comp_config, total_steps)
    
    if comp_config.optimizer == OptimizerType.ADAMW:
        return optax.adamw(
            learning_rate=schedule,
            weight_decay=comp_config.weight_decay,
            eps=comp_config.epsilon or 1e-8
        )
    elif comp_config.optimizer == OptimizerType.LION:
        return optax.lion(
            learning_rate=schedule,
            weight_decay=comp_config.weight_decay
        )
    elif comp_config.optimizer == OptimizerType.ADAMAXW:
        return optax.adamaxw(
            learning_rate=schedule,
            weight_decay=comp_config.weight_decay,
            eps=comp_config.epsilon or 1e-8
        )
    return optax.adamw(learning_rate=schedule)

def create_optimizer(config: OptimizerConfig) -> optax.GradientTransformation:
    """Create complete optimizer with advanced features."""
    optimizers = {}
    labels = {}
    
    # Global schedule and base optimizer
    global_schedule = _create_global_schedule(config)
    base_optimizer = _create_base_optimizer(config, global_schedule)
    optimizers['base'] = base_optimizer

    # Handle frozen components
    for comp_name in config.frozen_components:
        if comp_name in labels:
            logger.warning(f"Component {comp_name} is both frozen and optimized")
        optimizers[comp_name] = optax.set_to_zero()
        labels[comp_name] = comp_name

    # Component-specific optimizers
    for comp in config.component_optimizers:
        if comp.component_name in config.frozen_components:
            logger.warning(f"Component {comp.component_name} is both frozen and optimized")
        optimizers[comp.component_name] = _create_optimizer_for_component(comp, config.total_steps)
        labels[comp.component_name] = comp.component_name

    # Build optimization chain
    chain = [optax.zero_nans()]  # Early NaN handling
    
    if config.gradient_accumulation_steps > 1:
        chain.append(optax.MultiSteps(config.gradient_accumulation_steps))
    
    if config.use_mixed_precision:
        chain.append(optax.scale_by_float32())
        if config.loss_scale:
            chain.append(optax.scale_by_loss_scale(config.loss_scale))
        else:
            chain.append(optax.DynamicLossScale())

    # TPU-specific optimizations
    if config.use_tpu:
        if config.tpu_topology:
            try:
                topology = mesh_utils.create_device_mesh((config.tpu_topology,))
                logger.info(f"TPU topology configurada: {topology}")
            except Exception as e:
                logger.error(f"Error configurando topología TPU: {str(e)}")
        chain.append(optax.scale_by_adam(eps_root=config.epsilon))

    chain.extend([
        optax.clip_by_global_norm(config.clip_norm),
        optax.multi_transform(optimizers, labels)
    ])

    logger.info(f"Optimizer created with {len(config.component_optimizers)} specialized components")
    logger.debug(f"Optimizer chain: {chain}")
    
    return optax.chain(*chain)

def create_optimizer_from_capibara_config(capibara_config: Dict) -> optax.GradientTransformation:
    """Create optimizer from Capibara's main configuration."""
    training_config = capibara_config['training']
    
    optimizer_config = OptimizerConfig(
        global_learning_rate=training_config['learning_rate'],
        total_steps=training_config['total_steps'],
        clip_norm=training_config.get('clip_norm', 1.0),
        weight_decay=training_config.get('weight_decay', 0.01),
        use_mixed_precision=training_config.get('mixed_precision', False),
        gradient_accumulation_steps=training_config.get('gradient_accumulation_steps', 1),
        frozen_components=training_config.get('frozen_components', []),
        component_optimizers=[
            ComponentOptimizerConfig(**comp)
            for comp in training_config.get('component_optimizers', [])
        ],
        optimizer_name=training_config.get('optimizer', 'adamw'),
        schedule_type=training_config.get('schedule_type', 'warmup_cosine_decay'),
        beta1=training_config.get('beta1', 0.9),
        beta2=training_config.get('beta2', 0.999),
        epsilon=training_config.get('epsilon', 1e-8),
        momentum=training_config.get('momentum', 0.9),
        warmup_ratio=training_config.get('warmup_ratio', 0.1),
        early_stopping=training_config.get('early_stopping'),
        gradient_validation=training_config.get('gradient_validation', {}),
        use_tpu=training_config.get('use_tpu', False),
        tpu_topology=training_config.get('tpu_topology')
    )
    
    return create_optimizer(optimizer_config)

@partial(jax.jit, static_argnames=('optimizer',))
def update_step(
    params: Dict[str, Any],
    grads: Dict[str, Any],
    opt_state: optax.OptState,
    optimizer: optax.GradientTransformation,
    config: OptimizerConfig
) -> Tuple[Dict[str, Any], optax.OptState, Dict[str, Any]]:
    """Update step with gradient validation and logging."""
    # Validar gradientes
    gradient_warnings = _validate_gradients(grads, config.gradient_validation)
    if gradient_warnings:
        logger.warning("Problemas con gradientes:\n" + "\n".join(gradient_warnings))
    
    # Aplicar actualización
    updates, new_opt_state = optimizer.update(grads, opt_state)
    new_params = optax.apply_updates(params, updates)
    
    # Logging de actualización
    update_info = {
        'gradient_norm': jnp.linalg.norm(jnp.array([jnp.linalg.norm(g) for g in jax.tree_util.tree_leaves(grads)])),
        'update_norm': jnp.linalg.norm(jnp.array([jnp.linalg.norm(u) for u in jax.tree_util.tree_leaves(updates)])),
        'gradient_warnings': gradient_warnings
    }
    
    return new_params, new_opt_state, update_info

__all__ = [
    'create_optimizer',
    'create_optimizer_from_capibara_config',
    'OptimizerConfig',
    'ComponentOptimizerConfig',
    'ScheduleType',
    'OptimizerType',
    'update_step'
]