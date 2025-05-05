"""
Layers module for CapibaraModel.

This module provides various neural network layers and components.
"""

# Capas básicas
from .self_attention import SelfAttention
from .synthetic_embedding import SyntheticEmbedding

# Capas especializadas
from .bitnet import Conv1DBlock
from .affine_quantizer import AffineQuantizer
from .game_theory import GameTheory
from .mixture_of_rookies import MixtureOfRookies
from .platonic import Platonic
from .quineana import Quineana
from .sparse_capibara import SparseCapibara

from .bitnet import Conv1DBlock
from .neurogenesis import NeurogenesisModule
from .attention import DistributedAttention


__all__ = [
    # Capas básicas
    "SelfAttention",
    "SyntheticEmbedding",
    
    # Capas especializadas
    "BitNet",
    "AffineQuantizer",
    "GameTheory",
    "MixtureOfRookies",
    "Platonic",
    "Quineana",
    "SparseCapibara",

    "Conv1DBlock",
    "NeurogenesisModule",
    "DistributedAttention"
  
    
]
