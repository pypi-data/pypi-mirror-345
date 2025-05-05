"""
Sub-models module for CapibaraModel.

This module provides specialized sub-models and components.
"""

from .experimental.quantum import QuantumSubModel
from .experimental.sparse import SparseSubModel
from .experimental.hybrid import HybridSubModel
from .experimental.distributed import DistributedSubModel

__all__ = [
    "QuantumSubModel",
    "SparseSubModel",
    "HybridSubModel",
    "DistributedSubModel"
]