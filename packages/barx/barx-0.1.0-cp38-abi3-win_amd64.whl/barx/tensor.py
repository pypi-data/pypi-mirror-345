"""
Tensor operations module for BARX.

This module provides the core tensor functionality, including creation,
manipulation, and mathematical operations.
"""

import numpy as np
import logging
from typing import List, Tuple, Union, Optional, Any, Callable

# Try to import Rust kernels, fallback to NumPy if unavailable
try:
    from ._rust_kernels import matmul_kernel as _rust_matmul
    from ._rust_kernels import conv2d as _rust_conv2d
    _HAS_RUST_KERNELS = True
except ImportError:
    _HAS_RUST_KERNELS = False
    logging.warning("Rust kernels not available in tensor module, using NumPy fallback.")

class Tensor:
    """
    The core tensor class for BARX.
    
    Wraps NumPy arrays and provides automatic differentiation capabilities.
    """
    
    def __init__(self, data, requires_grad=False):
        """
        Initialize a new Tensor.
        
        Args:
            data: Input data (NumPy array, Python list, or scalar)
            requires_grad: Whether the tensor requires gradients
        """
        if isinstance(data, Tensor):
            self.data = data.data
        elif isinstance(data, np.ndarray):
            self.data = data
        else:
            self.data = np.array(data, dtype=np.float32)
            
        self.requires_grad = requires_grad
        self.grad = None
        self._grad_fn = None
        self._backward_hooks = []
        
        # For autograd
        self._prev = set()
        self.shape = self.data.shape
        self.dtype = self.data.dtype
        
    def backward(self, grad=None):
        """
        Compute gradients through backpropagation.
        
        Args:
            grad: Gradient from upstream operations (default: ones_like)
        """
        if grad is None:
            grad = np.ones_like(self.data)
            
        if self.grad is None:
            self.grad = grad
        else:
            self.grad += grad
            
        if self._grad_fn is not None:
            self._grad_fn(grad)
            
        for hook in self._backward_hooks:
            hook(self, grad)
    
    def zero_grad(self):
        """Reset gradients to None."""
        self.grad = None
    
    # Basic operations with autograd support
    def __add__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        result = Tensor(self.data + other.data)
        
        if self.requires_grad or other.requires_grad:
            result.requires_grad = True
            result._prev = {self, other}
            
            def _backward_add(grad):
                if self.requires_grad:
                    if self.grad is None:
                        self.grad = grad
                    else:
                        self.grad += grad
                if other.requires_grad:
                    if other.grad is None:
                        other.grad = grad
                    else:
                        other.grad += grad
                        
            result._grad_fn = _backward_add
        
        return result
    
    def __mul__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        result = Tensor(self.data * other.data)
        
        if self.requires_grad or other.requires_grad:
            result.requires_grad = True
            result._prev = {self, other}
            
            def _backward_mul(grad):
                if self.requires_grad:
                    self_grad = grad * other.data
                    if self.grad is None:
                        self.grad = self_grad
                    else:
                        self.grad += self_grad
                        
                if other.requires_grad:
                    other_grad = grad * self.data
                    if other.grad is None:
                        other.grad = other_grad
                    else:
                        other.grad += other_grad
                        
            result._grad_fn = _backward_mul
            
        return result
    
    def __sub__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        return self + (other * -1)
    
    def __truediv__(self, other):
        other = other if isinstance(other, Tensor) else Tensor(other)
        return self * (other ** -1)
    
    def __pow__(self, power):
        result = Tensor(self.data ** power)
        
        if self.requires_grad:
            result.requires_grad = True
            result._prev = {self}
            
            def _backward_pow(grad):
                self_grad = grad * power * (self.data ** (power - 1))
                if self.grad is None:
                    self.grad = self_grad
                else:
                    self.grad += self_grad
                    
            result._grad_fn = _backward_pow
            
        return result
    
    def __matmul__(self, other):
        return self.dot(other)
        
    def dot(self, other):
        """
        Matrix multiplication operation.
        
        Uses Rust kernel if available, otherwise falls back to NumPy.
        
        Args:
            other: The tensor to multiply with
            
        Returns:
            A new tensor with the result of the matrix multiplication
        """
        other = other if isinstance(other, Tensor) else Tensor(other)
        
        # Ensure both arrays are float32
        self_data = self.data.astype(np.float32) if self.data.dtype != np.float32 else self.data
        other_data = other.data.astype(np.float32) if other.data.dtype != np.float32 else other.data
        
        # Use Rust kernel if available and shapes are compatible
        if _HAS_RUST_KERNELS and len(self.shape) == 2 and len(other.shape) == 2:
            try:
                result_data = _rust_matmul(self_data, other_data)
            except Exception:
                # Fallback to NumPy if the Rust kernel fails
                result_data = self_data @ other_data
        else:
            result_data = self_data @ other_data
            
        result = Tensor(result_data)
        
        if self.requires_grad or other.requires_grad:
            result.requires_grad = True
            result._prev = {self, other}
            
            def _backward_dot(grad):
                if self.requires_grad:
                    self_grad = grad @ other.data.T
                    if self.grad is None:
                        self.grad = self_grad
                    else:
                        self.grad += self_grad
                        
                if other.requires_grad:
                    other_grad = self.data.T @ grad
                    if other.grad is None:
                        other.grad = other_grad
                    else:
                        other.grad += other_grad
                        
            result._grad_fn = _backward_dot
            
        return result
    
    def mean(self):
        """Compute the mean of all elements in the tensor."""
        result = Tensor(np.mean(self.data))
        
        if self.requires_grad:
            result.requires_grad = True
            result._prev = {self}
            
            def _backward_mean(grad):
                self_grad = np.ones_like(self.data) * grad / self.data.size
                if self.grad is None:
                    self.grad = self_grad
                else:
                    self.grad += self_grad
                    
            result._grad_fn = _backward_mean
            
        return result
    
    def sum(self, axis=None, keepdims=False):
        """Compute sum along the specified axis."""
        result = Tensor(np.sum(self.data, axis=axis, keepdims=keepdims))
        
        if self.requires_grad:
            result.requires_grad = True
            result._prev = {self}
            
            def _backward_sum(grad):
                if axis is None:
                    self_grad = np.ones_like(self.data) * grad
                else:
                    self_grad = np.expand_dims(grad, axis=axis) * np.ones_like(self.data)
                
                if self.grad is None:
                    self.grad = self_grad
                else:
                    self.grad += self_grad
                    
            result._grad_fn = _backward_sum
            
        return result
    
    def transpose(self):
        """Transpose the tensor."""
        result = Tensor(self.data.T)
        
        if self.requires_grad:
            result.requires_grad = True
            result._prev = {self}
            
            def _backward_transpose(grad):
                if self.grad is None:
                    self.grad = grad.T
                else:
                    self.grad += grad.T
                    
            result._grad_fn = _backward_transpose
            
        return result
    
    @property
    def T(self):
        """Transpose property."""
        return self.transpose()
    
    def reshape(self, *shape):
        """Reshape the tensor to the specified shape."""
        if len(shape) == 1 and isinstance(shape[0], (tuple, list)):
            shape = shape[0]
            
        result = Tensor(self.data.reshape(shape))
        
        if self.requires_grad:
            result.requires_grad = True
            result._prev = {self}
            
            def _backward_reshape(grad):
                if self.grad is None:
                    self.grad = grad.reshape(self.shape)
                else:
                    self.grad += grad.reshape(self.shape)
                    
            result._grad_fn = _backward_reshape
            
        return result
    
    def conv2d(self, kernel, stride=1, padding=0):
        """
        2D convolution operation.
        
        Args:
            kernel: Convolution kernel tensor
            stride: Stride size (default: 1)
            padding: Padding size (default: 0)
            
        Returns:
            A new tensor with the result of the convolution
        """
        kernel = kernel if isinstance(kernel, Tensor) else Tensor(kernel)
        
        # Simple padding implementation
        if padding > 0:
            padded = np.pad(self.data, ((0, 0), (0, 0), (padding, padding), (padding, padding)), 'constant')
        else:
            padded = self.data
            
        # Get input dimensions
        N, C, H, W = padded.shape
        F, C_, HH, WW = kernel.shape
        
        assert C == C_, "Input and kernel channels must match"
        
        # Calculate output dimensions
        H_out = (H - HH) // stride + 1
        W_out = (W - WW) // stride + 1
        
        # Use Rust kernel if available
        if _HAS_RUST_KERNELS:
            result_data = _rust_conv2d(padded, kernel.data, stride)
        else:
            # Fallback to NumPy implementation
            result_data = np.zeros((N, F, H_out, W_out))
            
            for n in range(N):
                for f in range(F):
                    for i in range(0, H - HH + 1, stride):
                        for j in range(0, W - WW + 1, stride):
                            result_data[n, f, i//stride, j//stride] = np.sum(
                                padded[n, :, i:i+HH, j:j+WW] * kernel.data[f]
                            )
        
        result = Tensor(result_data)
        
        if self.requires_grad or kernel.requires_grad:
            result.requires_grad = True
            result._prev = {self, kernel}
            
            def _backward_conv2d(grad):
                # TODO: Implement proper backprop for conv2d
                # This is simplified and not correct for all cases
                pass
                
            result._grad_fn = _backward_conv2d
            
        return result
    
    def __repr__(self):
        return f"Tensor({self.data}, requires_grad={self.requires_grad})"


# Static methods as interface for tensor creation
class T:
    """
    Static interface for tensor operations.
    
    Provides convenient methods for creating and manipulating tensors.
    """
    
    @staticmethod
    def tensor(data, requires_grad=False):
        """Create a new tensor from data."""
        return Tensor(data, requires_grad=requires_grad)
    
    @staticmethod
    def zeros(*shape, requires_grad=False):
        """Create a tensor filled with zeros."""
        if len(shape) == 1 and isinstance(shape[0], (tuple, list)):
            shape = shape[0]
        return Tensor(np.zeros(shape), requires_grad=requires_grad)
    
    @staticmethod
    def ones(*shape, requires_grad=False):
        """Create a tensor filled with ones."""
        if len(shape) == 1 and isinstance(shape[0], (tuple, list)):
            shape = shape[0]
        return Tensor(np.ones(shape), requires_grad=requires_grad)
    
    @staticmethod
    def randn(*shape, requires_grad=False):
        """Create a tensor filled with random values from standard normal distribution."""
        if len(shape) == 1 and isinstance(shape[0], (tuple, list)):
            shape = shape[0]
        return Tensor(np.random.randn(*shape), requires_grad=requires_grad)
    
    @staticmethod
    def uniform(*shape, low=0.0, high=1.0, requires_grad=False):
        """Create a tensor filled with random values from uniform distribution."""
        if len(shape) == 1 and isinstance(shape[0], (tuple, list)):
            shape = shape[0]
        return Tensor(np.random.uniform(low, high, shape), requires_grad=requires_grad)
    
    @staticmethod
    def arange(start, end=None, step=1, requires_grad=False):
        """Create a 1-D tensor with values from start to end with step size."""
        return Tensor(np.arange(start, end, step), requires_grad=requires_grad)
    
    @staticmethod
    def from_numpy(array, requires_grad=False):
        """Create a tensor from a NumPy array."""
        return Tensor(array, requires_grad=requires_grad)

# Alias for backward compatibility
tensor = T.tensor
zeros = T.zeros
ones = T.ones
randn = T.randn
