"""Módulo de entrenamiento de CapibaraGPT.

Este módulo contiene las implementaciones para el entrenamiento del modelo,
incluyendo optimizaciones para TPU y entrenamiento distribuido.
"""

from .train_unified import (
    TrainingState,
    train_step,
    validate_step,
    train_model
)

__all__ = [
    'TrainingState',
    'train_step',
    'validate_step',
    'train_model'
] 