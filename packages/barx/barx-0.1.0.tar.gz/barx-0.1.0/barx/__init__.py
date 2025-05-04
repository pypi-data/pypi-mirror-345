"""
BARX: Fast, CPU-only AI framework for Python developers.

BARX enables Python developers to build, train, and run AI models
without GPU requirements, utilizing efficient Rust/SIMD kernels 
for performance-critical operations.
"""

__version__ = "0.1.0"

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import main modules to make them available at top level
from . import tensor
from . import nn
from . import optim
from . import llm
from . import data

# Check if Rust kernels are available
try:
    from . import _rust_kernels
    _HAS_RUST_KERNELS = True
except ImportError:
    logging.warning("Rust kernels not available, falling back to NumPy implementations.")
    _HAS_RUST_KERNELS = False

__all__ = ['tensor', 'nn', 'optim', 'llm', 'data']
