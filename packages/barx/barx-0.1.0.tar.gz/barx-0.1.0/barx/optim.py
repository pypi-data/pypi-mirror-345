"""
Optimization algorithms for BARX.

This module provides optimizers for training neural networks with
automatic differentiation support.
"""

from typing import List, Dict, Any, Optional, Union, Callable, Iterable
from .tensor import Tensor

class Optimizer:
    """
    Base class for all optimizers.
    
    All optimizers should subclass this and implement the step method.
    """
    
    def __init__(self, params: List[Tensor], defaults: Dict[str, Any] = None):
        """
        Initialize optimizer.
        
        Args:
            params: List of parameters to optimize
            defaults: Default optimizer settings
        """
        if defaults is None:
            defaults = {}
            
        self.defaults = defaults
        self.state = {}  # Optimizer state for each parameter
        self.param_groups = []
        
        param_group = {'params': list(params)}
        param_group.update(defaults)
        self.param_groups.append(param_group)
        
    def zero_grad(self):
        """Reset the gradients of all parameters."""
        for group in self.param_groups:
            for param in group['params']:
                if param.grad is not None:
                    param.grad = None
                    
    def step(self):
        """
        Perform a single optimization step.
        
        Should be overridden by all subclasses.
        """
        raise NotImplementedError("Subclasses must implement step method.")


class SGD(Optimizer):
    """
    Stochastic Gradient Descent optimizer.
    
    Implements SGD with momentum and weight decay.
    """
    
    def __init__(self, 
                 params: List[Tensor], 
                 lr: float = 0.01, 
                 momentum: float = 0.0, 
                 weight_decay: float = 0.0):
        """
        Initialize SGD optimizer.
        
        Args:
            params: List of parameters to optimize
            lr: Learning rate (default: 0.01)
            momentum: Momentum factor (default: 0.0)
            weight_decay: Weight decay (L2 penalty) (default: 0.0)
        """
        defaults = {'lr': lr, 'momentum': momentum, 'weight_decay': weight_decay}
        super().__init__(params, defaults)
        
    def step(self):
        """Perform a single optimization step."""
        for group in self.param_groups:
            weight_decay = group['weight_decay']
            momentum = group['momentum']
            lr = group['lr']
            
            for param in group['params']:
                if param.grad is None:
                    continue
                    
                grad = param.grad
                
                # Apply weight decay
                if weight_decay != 0:
                    grad = grad + weight_decay * param.data
                    
                # Apply momentum
                if momentum != 0:
                    param_state = self.state.get(id(param), {})
                    
                    if 'momentum_buffer' not in param_state:
                        # Initialize momentum buffer
                        param_state['momentum_buffer'] = grad.copy()
                    else:
                        # Update momentum buffer
                        buf = param_state['momentum_buffer']
                        buf = momentum * buf + grad
                        param_state['momentum_buffer'] = buf
                        grad = buf
                    
                    self.state[id(param)] = param_state
                    
                # Update parameter
                param.data -= lr * grad


class Adam(Optimizer):
    """
    Adam optimizer.
    
    Implements Adam algorithm.
    """
    
    def __init__(self, 
                 params: List[Tensor], 
                 lr: float = 0.001, 
                 betas: tuple = (0.9, 0.999), 
                 eps: float = 1e-8, 
                 weight_decay: float = 0.0):
        """
        Initialize Adam optimizer.
        
        Args:
            params: List of parameters to optimize
            lr: Learning rate (default: 0.001)
            betas: Coefficients for computing running averages of gradient and its square (default: (0.9, 0.999))
            eps: Term added to denominator for numerical stability (default: 1e-8)
            weight_decay: Weight decay (L2 penalty) (default: 0.0)
        """
        defaults = {'lr': lr, 'betas': betas, 'eps': eps, 'weight_decay': weight_decay}
        super().__init__(params, defaults)
        
    def step(self):
        """Perform a single optimization step."""
        for group in self.param_groups:
            lr = group['lr']
            betas = group['betas']
            eps = group['eps']
            weight_decay = group['weight_decay']
            
            for param in group['params']:
                if param.grad is None:
                    continue
                    
                grad = param.grad
                
                # Apply weight decay
                if weight_decay != 0:
                    grad = grad + weight_decay * param.data
                    
                # Initialize state if needed
                param_state = self.state.get(id(param), {})
                if len(param_state) == 0:
                    param_state['step'] = 0
                    param_state['exp_avg'] = 0.0 * grad  # Initialize as zeros
                    param_state['exp_avg_sq'] = 0.0 * grad  # Initialize as zeros
                
                # Get state variables
                exp_avg = param_state['exp_avg']
                exp_avg_sq = param_state['exp_avg_sq']
                step = param_state['step'] = param_state['step'] + 1
                
                # Update biased first and second moment estimates
                beta1, beta2 = betas
                exp_avg = beta1 * exp_avg + (1 - beta1) * grad
                exp_avg_sq = beta2 * exp_avg_sq + (1 - beta2) * (grad * grad)
                
                # Store updated state
                param_state['exp_avg'] = exp_avg
                param_state['exp_avg_sq'] = exp_avg_sq
                
                # Bias correction
                bias_correction1 = 1 - beta1 ** step
                bias_correction2 = 1 - beta2 ** step
                
                # Compute step size
                step_size = lr * (bias_correction2 ** 0.5) / bias_correction1
                
                # Update parameter
                param.data -= step_size * exp_avg / (exp_avg_sq ** 0.5 + eps)
                
                # Store updated state
                self.state[id(param)] = param_state
