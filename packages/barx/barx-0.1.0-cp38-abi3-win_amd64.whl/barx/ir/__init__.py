"""
IR (Intermediate Representation) module for BARX.

This module provides functionality for parsing and optimizing
intermediate representations of neural network models.
"""

from .parser import Parser
from .optimizer import PassManager, OptimizationPass, ConstantFolding, OperatorFusion

__all__ = [
    'Parser', 
    'PassManager', 
    'OptimizationPass', 
    'ConstantFolding', 
    'OperatorFusion'
]
