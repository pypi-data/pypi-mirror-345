"""
Utility functions and helpers for BARX.

This module provides miscellaneous utility functions for
various tasks in the BARX framework.
"""

import os
import sys
import logging
import time
import numpy as np
from typing import List, Dict, Any, Union, Optional, Tuple
from .tensor import Tensor

def seed_all(seed: int):
    """
    Set random seeds for reproducibility.
    
    Args:
        seed: Seed value for random number generators
    """
    np.random.seed(seed)
    # Add other RNG seeds if more libraries are used

def benchmark_op(op_func, *args, n_runs: int = 100, warmup: int = 10):
    """
    Benchmark the execution time of an operation.
    
    Args:
        op_func: Function to benchmark
        *args: Arguments to pass to the function
        n_runs: Number of runs for timing (default: 100)
        warmup: Number of warmup runs (default: 10)
        
    Returns:
        Dictionary with timing statistics
    """
    # Warmup runs
    for _ in range(warmup):
        _ = op_func(*args)
        
    # Timed runs
    times = []
    for _ in range(n_runs):
        start = time.time()
        _ = op_func(*args)
        end = time.time()
        times.append((end - start) * 1000)  # Convert to ms
        
    return {
        'mean_ms': np.mean(times),
        'median_ms': np.median(times),
        'min_ms': np.min(times),
        'max_ms': np.max(times),
        'std_ms': np.std(times)
    }

def compare_with_numpy(barx_tensor: Tensor, numpy_array: np.ndarray, rtol: float = 1e-5, atol: float = 1e-8):
    """
    Compare a BARX tensor with a NumPy array for approximate equality.
    
    Args:
        barx_tensor: BARX tensor
        numpy_array: NumPy array
        rtol: Relative tolerance (default: 1e-5)
        atol: Absolute tolerance (default: 1e-8)
        
    Returns:
        True if the values are approximately equal, False otherwise
    """
    return np.allclose(barx_tensor.data, numpy_array, rtol=rtol, atol=atol)

def memory_usage():
    """
    Get current memory usage of the process.
    
    Returns:
        Memory usage in megabytes
    """
    try:
        import psutil
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        return mem_info.rss / (1024 * 1024)  # Convert to MB
    except ImportError:
        logging.warning("psutil not available, can't get memory usage")
        return 0.0

def quantize_matrix(matrix: np.ndarray, bits: int = 8):
    """
    Quantize a matrix to reduced precision.
    
    Args:
        matrix: Input matrix to quantize
        bits: Number of bits for quantization (default: 8)
        
    Returns:
        Tuple of (quantized_matrix, scale)
    """
    # Calculate scale (max absolute value / (2^(bits-1) - 1))
    max_val = np.max(np.abs(matrix))
    max_quantized = (1 << (bits - 1)) - 1
    scale = max_val / max_quantized
    
    # Quantize
    if bits == 8:
        quantized = np.clip(np.round(matrix / scale), -127, 127).astype(np.int8)
    elif bits == 16:
        quantized = np.clip(np.round(matrix / scale), -32767, 32767).astype(np.int16)
    else:
        raise ValueError(f"Unsupported quantization bits: {bits}")
        
    return quantized, scale

def dequantize_matrix(quantized_matrix: np.ndarray, scale: float):
    """
    Dequantize a matrix back to floating point.
    
    Args:
        quantized_matrix: Quantized matrix
        scale: Scale factor used during quantization
        
    Returns:
        Dequantized matrix
    """
    return quantized_matrix.astype(np.float32) * scale

class ProgressBar:
    """
    Simple progress bar for tracking training/evaluation progress.
    """
    
    def __init__(self, total: int, width: int = 40, prefix: str = '', suffix: str = ''):
        """
        Initialize progress bar.
        
        Args:
            total: Total number of items
            width: Bar width in characters (default: 40)
            prefix: Text to display before the bar (default: '')
            suffix: Text to display after the bar (default: '')
        """
        self.total = total
        self.width = width
        self.prefix = prefix
        self.suffix = suffix
        self.iteration = 0
        self.start_time = time.time()
        
    def update(self, iteration: Optional[int] = None):
        """
        Update the progress bar.
        
        Args:
            iteration: Current iteration (default: None, increments by 1)
        """
        if iteration is not None:
            self.iteration = iteration
        else:
            self.iteration += 1
            
        percent = self.iteration / self.total
        filled_width = int(self.width * percent)
        bar = '█' * filled_width + '-' * (self.width - filled_width)
        
        elapsed = time.time() - self.start_time
        if percent > 0:
            eta = elapsed / percent - elapsed
        else:
            eta = 0
            
        # Format the time values
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
        eta_str = time.strftime("%H:%M:%S", time.gmtime(eta))
        
        # Print the progress bar
        message = f'\r{self.prefix} |{bar}| {percent:.1%} {self.iteration}/{self.total} [{elapsed_str}<{eta_str}] {self.suffix}'
        print(message, end='', flush=True)
        
        # Print a newline when complete
        if self.iteration == self.total:
            print()
