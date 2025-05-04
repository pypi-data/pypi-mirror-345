"""
Neural network module for BARX.

This module provides neural network layers and utilities for building
and training neural networks.
"""

import numpy as np
from typing import List, Tuple, Optional, Union, Callable, Dict, Any
from .tensor import Tensor, T

# Try to import Rust kernels, fallback to NumPy if unavailable
try:
    from ._rust_kernels import relu as _rust_relu
    from ._rust_kernels import softmax as _rust_softmax
    _HAS_RUST_KERNELS = True
except ImportError:
    _HAS_RUST_KERNELS = False
    import logging
    logging.warning("Rust kernels not available in nn module, using NumPy fallback.")

class Module:
    """
    Base class for all neural network modules.
    
    All custom models should subclass this and implement the forward method.
    """
    
    def __init__(self):
        self._modules = {}
        self._parameters = {}
        self._buffers = {}
        self._training = True
        
    def __call__(self, *args, **kwargs):
        """Call forward method."""
        return self.forward(*args, **kwargs)
    
    def forward(self, *args, **kwargs):
        """
        Forward pass logic.
        
        Should be overridden by all subclasses.
        """
        raise NotImplementedError("Subclasses must implement forward method.")
    
    def register_module(self, name: str, module: 'Module'):
        """
        Register a child module.
        
        Args:
            name: Name of the module
            module: Module to register
        """
        self._modules[name] = module
        setattr(self, name, module)
        
    def register_parameter(self, name: str, param: Tensor):
        """
        Register a parameter.
        
        Args:
            name: Name of the parameter
            param: Parameter tensor to register
        """
        self._parameters[name] = param
        setattr(self, name, param)
        
    def register_buffer(self, name: str, buffer: Tensor):
        """
        Register a buffer (non-trainable tensor).
        
        Args:
            name: Name of the buffer
            buffer: Buffer tensor to register
        """
        self._buffers[name] = buffer
        setattr(self, name, buffer)
        
    def parameters(self):
        """
        Get all parameters of the module and its submodules.
        
        Returns:
            List of all parameter tensors
        """
        params = list(self._parameters.values())
        for module in self._modules.values():
            params.extend(module.parameters())
        return params
    
    def eval(self):
        """Set the module to evaluation mode."""
        self._training = False
        for module in self._modules.values():
            module.eval()
            
    def train(self, mode=True):
        """Set the module to training mode."""
        self._training = mode
        for module in self._modules.values():
            module.train(mode)
            
    def zero_grad(self):
        """Reset gradients of all parameters."""
        for param in self.parameters():
            if param.requires_grad and param.grad is not None:
                param.zero_grad()
                
    def __repr__(self):
        """String representation of the module."""
        lines = [self.__class__.__name__ + '(']
        for key, module in self._modules.items():
            mod_str = repr(module)
            mod_str = "  " + mod_str.replace('\n', '\n  ')
            lines.append(f"({key}): {mod_str}")
        lines.append(')')
        return '\n'.join(lines)


class Linear(Module):
    """
    Linear (fully connected) layer.
    
    Applies a linear transformation: y = xW^T + b
    """
    
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        """
        Initialize linear layer.
        
        Args:
            in_features: Size of input features
            out_features: Size of output features
            bias: Whether to use bias (default: True)
        """
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        # Xavier initialization with float32 dtype
        weight_data = T.randn(out_features, in_features).data.astype(np.float32) * np.sqrt(2.0 / (in_features + out_features))
        weight = T.from_numpy(weight_data, requires_grad=True)
        self.register_parameter("weight", weight)
        
        if bias:
            bias_data = np.zeros(out_features, dtype=np.float32)
            self.register_parameter("bias", T.from_numpy(bias_data, requires_grad=True))
        else:
            self.register_buffer("bias", None)
            
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape (..., in_features)
            
        Returns:
            Output tensor of shape (..., out_features)
        """
        # Ensure input is float32
        if x.data.dtype != np.float32:
            x = T.from_numpy(x.data.astype(np.float32), requires_grad=x.requires_grad)
            
        output = x.dot(self.weight.T)
        if self.bias is not None:
            output = output + self.bias
        return output
    
    def __repr__(self):
        return f"Linear(in_features={self.in_features}, out_features={self.out_features}, bias={self.bias is not None})"


class ReLU(Module):
    """
    Rectified Linear Unit (ReLU) activation function.
    
    Applies the rectified linear unit function element-wise: max(0, x)
    """
    
    def __init__(self, inplace: bool = False):
        """
        Initialize ReLU.
        
        Args:
            inplace: Whether to modify input in-place (not used in this implementation)
        """
        super().__init__()
        self.inplace = inplace
        
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor with ReLU applied
        """
        # Ensure input is float32
        if x.data.dtype != np.float32:
            x = T.from_numpy(x.data.astype(np.float32), requires_grad=x.requires_grad)

        if _HAS_RUST_KERNELS:
            try:
                result_data = _rust_relu(x.data)
                result = Tensor(result_data)
            except Exception:
                # Fallback to NumPy implementation
                result = Tensor(np.maximum(0, x.data))
        else:
            # NumPy implementation
            result = Tensor(np.maximum(0, x.data))
            
        if x.requires_grad:
            result.requires_grad = True
            result._prev = {x}
            
            def _backward_relu(grad):
                # Gradient of ReLU: 1 if x > 0, 0 otherwise
                x_grad = grad * (x.data > 0).astype(np.float32)
                if x.grad is None:
                    x.grad = x_grad
                else:
                    x.grad += x_grad
                    
            result._grad_fn = _backward_relu
            
        return result
        
    def __repr__(self):
        return f"ReLU(inplace={self.inplace})"


class Softmax(Module):
    """
    Softmax activation function.
    
    Applies the softmax function to the input tensor along the specified dimension.
    """
    
    def __init__(self, dim: int = -1):
        """
        Initialize Softmax.
        
        Args:
            dim: Dimension along which to apply softmax (default: -1)
        """
        super().__init__()
        self.dim = dim
        
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor with softmax applied
        """
        # Ensure input is float32
        if x.data.dtype != np.float32:
            x = T.from_numpy(x.data.astype(np.float32), requires_grad=x.requires_grad)
            
        # Convert negative axis to positive
        dim = self.dim if self.dim >= 0 else len(x.shape) + self.dim
        
        if _HAS_RUST_KERNELS and len(x.shape) == 2 and dim == 1:
            try:
                result_data = _rust_softmax(x.data, dim)
                result = Tensor(result_data)
            except Exception:
                # Fallback to NumPy implementation
                # NumPy implementation for numerical stability
                exp_x = np.exp(x.data - np.max(x.data, axis=dim, keepdims=True))
                result = Tensor(exp_x / np.sum(exp_x, axis=dim, keepdims=True))
        else:
            # NumPy implementation for numerical stability
            exp_x = np.exp(x.data - np.max(x.data, axis=dim, keepdims=True))
            result = Tensor(exp_x / np.sum(exp_x, axis=dim, keepdims=True))
            
        if x.requires_grad:
            result.requires_grad = True
            result._prev = {x}
            
            def _backward_softmax(grad):
                # This is a simplified version and not correct for all cases
                # The full Jacobian would be complex to compute
                # Approximate gradient as if softmax were an element-wise operation
                # This works in common cases where gradients from higher layers have
                # special structure (e.g., one-hot encoding in cross-entropy loss)
                x_grad = grad * result.data * (1 - result.data)
                if x.grad is None:
                    x.grad = x_grad
                else:
                    x.grad += x_grad
                    
            result._grad_fn = _backward_softmax
            
        return result
    
    def __repr__(self):
        return f"Softmax(dim={self.dim})"


class Sequential(Module):
    """
    Sequential container of modules.
    
    Modules will be executed in the order they are passed to the constructor.
    """
    
    def __init__(self, *modules):
        """
        Initialize Sequential.
        
        Args:
            *modules: Variable length list of modules to add
        """
        super().__init__()
        for idx, module in enumerate(modules):
            self.register_module(str(idx), module)
            
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass through all modules in sequence.
        
        Args:
            x: Input tensor
            
        Returns:
            Output after applying all modules
        """
        for module in self._modules.values():
            x = module(x)
        return x
        
    def __repr__(self):
        module_str = ", ".join(repr(module) for module in self._modules.values())
        return f"Sequential({module_str})"


class Conv2d(Module):
    """
    2D convolution layer.
    
    Applies a 2D convolution over an input tensor.
    """
    
    def __init__(self, 
                 in_channels: int, 
                 out_channels: int, 
                 kernel_size: Union[int, Tuple[int, int]], 
                 stride: Union[int, Tuple[int, int]] = 1, 
                 padding: Union[int, Tuple[int, int]] = 0, 
                 bias: bool = True):
        """
        Initialize Conv2d.
        
        Args:
            in_channels: Number of input channels
            out_channels: Number of output channels
            kernel_size: Size of the convolving kernel
            stride: Stride of the convolution (default: 1)
            padding: Zero-padding added to both sides of the input (default: 0)
            bias: Whether to add bias (default: True)
        """
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        
        if isinstance(kernel_size, int):
            kernel_size = (kernel_size, kernel_size)
        self.kernel_size = kernel_size
        
        if isinstance(stride, int):
            stride = (stride, stride)
        self.stride = stride
        
        if isinstance(padding, int):
            padding = (padding, padding)
        self.padding = padding
        
        # Initialize weight with Kaiming initialization
        fan_in = in_channels * kernel_size[0] * kernel_size[1]
        std = np.sqrt(2.0 / fan_in)
        weight = T.randn(out_channels, in_channels, *kernel_size, requires_grad=True) * std
        self.register_parameter("weight", weight)
        
        if bias:
            self.register_parameter("bias", T.zeros(out_channels, requires_grad=True))
        else:
            self.register_buffer("bias", None)
            
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape (N, C_in, H, W)
            
        Returns:
            Output tensor of shape (N, C_out, H_out, W_out)
        """
        # Apply padding if needed
        if self.padding[0] > 0 or self.padding[1] > 0:
            # TODO: Implement proper padding
            pass
            
        output = x.conv2d(self.weight, stride=self.stride[0])
        
        if self.bias is not None:
            # Add bias to each output channel
            # TODO: Implement proper bias addition for conv output
            pass
            
        return output
        
    def __repr__(self):
        return (f"Conv2d(in_channels={self.in_channels}, "
                f"out_channels={self.out_channels}, "
                f"kernel_size={self.kernel_size}, "
                f"stride={self.stride}, "
                f"padding={self.padding}, "
                f"bias={self.bias is not None})")


class Dropout(Module):
    """
    Dropout layer.
    
    Randomly zeros some elements of the input tensor with probability p.
    """
    
    def __init__(self, p: float = 0.5, inplace: bool = False):
        """
        Initialize Dropout.
        
        Args:
            p: Probability of an element to be zeroed (default: 0.5)
            inplace: Whether to modify input in-place (not used in this implementation)
        """
        super().__init__()
        self.p = p
        self.inplace = inplace
        
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor with dropout applied
        """
        if not self._training or self.p == 0:
            return x
            
        mask = np.random.binomial(1, 1 - self.p, size=x.data.shape) / (1 - self.p)
        result = Tensor(x.data * mask)
        
        if x.requires_grad:
            result.requires_grad = True
            result._prev = {x}
            
            def _backward_dropout(grad):
                if x.grad is None:
                    x.grad = grad * mask
                else:
                    x.grad += grad * mask
                    
            result._grad_fn = _backward_dropout
            
        return result
        
    def __repr__(self):
        return f"Dropout(p={self.p})"


class BatchNorm2d(Module):
    """
    Batch Normalization for 2D inputs (e.g., images).
    
    Applies Batch Normalization over a 4D input (N, C, H, W).
    """
    
    def __init__(self, num_features: int, eps: float = 1e-5, momentum: float = 0.1):
        """
        Initialize BatchNorm2d.
        
        Args:
            num_features: Number of features/channels
            eps: Value added to denominator for numerical stability (default: 1e-5)
            momentum: Value for running_mean and running_var computation (default: 0.1)
        """
        super().__init__()
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum
        
        self.register_parameter("weight", T.ones(num_features, requires_grad=True))
        self.register_parameter("bias", T.zeros(num_features, requires_grad=True))
        
        self.register_buffer("running_mean", T.zeros(num_features))
        self.register_buffer("running_var", T.ones(num_features))
        
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape (N, C, H, W)
            
        Returns:
            Normalized output tensor
        """
        if self._training:
            # Calculate batch statistics
            batch_mean = np.mean(x.data, axis=(0, 2, 3), keepdims=True)
            batch_var = np.var(x.data, axis=(0, 2, 3), keepdims=True)
            
            # Update running statistics
            self.running_mean.data = (1 - self.momentum) * self.running_mean.data + self.momentum * batch_mean.squeeze()
            self.running_var.data = (1 - self.momentum) * self.running_var.data + self.momentum * batch_var.squeeze()
            
            # Normalize
            x_norm = (x.data - batch_mean) / np.sqrt(batch_var + self.eps)
        else:
            # Use running statistics
            mean = self.running_mean.data.reshape(1, -1, 1, 1)
            var = self.running_var.data.reshape(1, -1, 1, 1)
            x_norm = (x.data - mean) / np.sqrt(var + self.eps)
        
        # Scale and shift
        weight = self.weight.data.reshape(1, -1, 1, 1)
        bias = self.bias.data.reshape(1, -1, 1, 1)
        result_data = weight * x_norm + bias
        
        result = Tensor(result_data)
        
        if x.requires_grad:
            result.requires_grad = True
            result._prev = {x}
            
            # TODO: Implement proper backprop for batch norm
            # This is complex due to the multiple operations and batch statistics
            
        return result
        
    def __repr__(self):
        return f"BatchNorm2d(num_features={self.num_features}, eps={self.eps}, momentum={self.momentum})"


class MaxPool2d(Module):
    """
    2D max pooling layer.
    
    Applies a 2D max pooling over an input tensor.
    """
    
    def __init__(self, 
                 kernel_size: Union[int, Tuple[int, int]], 
                 stride: Optional[Union[int, Tuple[int, int]]] = None, 
                 padding: Union[int, Tuple[int, int]] = 0):
        """
        Initialize MaxPool2d.
        
        Args:
            kernel_size: Size of the pooling window
            stride: Stride of the pooling window (default: kernel_size)
            padding: Zero-padding added to both sides of the input (default: 0)
        """
        super().__init__()
        if isinstance(kernel_size, int):
            kernel_size = (kernel_size, kernel_size)
        self.kernel_size = kernel_size
        
        if stride is None:
            stride = kernel_size
        elif isinstance(stride, int):
            stride = (stride, stride)
        self.stride = stride
        
        if isinstance(padding, int):
            padding = (padding, padding)
        self.padding = padding
        
    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape (N, C, H, W)
            
        Returns:
            Output tensor of shape (N, C, H_out, W_out)
        """
        # Simple implementation for now
        N, C, H, W = x.data.shape
        
        H_out = (H + 2 * self.padding[0] - self.kernel_size[0]) // self.stride[0] + 1
        W_out = (W + 2 * self.padding[1] - self.kernel_size[1]) // self.stride[1] + 1
        
        # Apply padding if needed
        if self.padding[0] > 0 or self.padding[1] > 0:
            padded = np.pad(x.data, ((0, 0), (0, 0), 
                                    (self.padding[0], self.padding[0]), 
                                    (self.padding[1], self.padding[1])), 'constant')
        else:
            padded = x.data
            
        # Perform max pooling
        result_data = np.zeros((N, C, H_out, W_out))
        
        for n in range(N):
            for c in range(C):
                for i in range(H_out):
                    for j in range(W_out):
                        h_start = i * self.stride[0]
                        w_start = j * self.stride[1]
                        h_end = min(h_start + self.kernel_size[0], H + 2 * self.padding[0])
                        w_end = min(w_start + self.kernel_size[1], W + 2 * self.padding[1])
                        
                        result_data[n, c, i, j] = np.max(padded[n, c, h_start:h_end, w_start:w_end])
                        
        result = Tensor(result_data)
        
        if x.requires_grad:
            result.requires_grad = True
            result._prev = {x}
            
            # TODO: Implement proper backprop for max pooling
            # This requires tracking the max indices
            
        return result
        
    def __repr__(self):
        return f"MaxPool2d(kernel_size={self.kernel_size}, stride={self.stride}, padding={self.padding})"
