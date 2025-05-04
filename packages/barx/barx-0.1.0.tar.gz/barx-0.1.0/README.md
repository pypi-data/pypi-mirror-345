# BARX: Fast, CPU-only AI Framework for Python

[![PyPI version](https://img.shields.io/pypi/v/barx.svg)](https://pypi.org/project/barx/)
[![Python versions](https://img.shields.io/pypi/pyversions/barx.svg)](https://pypi.org/project/barx/)
[![License](https://img.shields.io/github/license/barx-team/barx.svg)](https://github.com/barx-team/barx/blob/main/LICENSE)

BARX is a high-performance, CPU-only AI framework that enables Python developers to build, train, and run AI models without GPU requirements.

## Key Features

- **CPU-only execution**: Run models on laptops, edge devices, and servers without GPU dependencies
- **High performance**: Rust/SIMD kernels for critical operations deliver optimized performance on CPU
- **Tensors & Neural Networks**: Create and manipulate tensors, build neural networks with standard layers
- **Memory efficiency**: INT8 quantization for large models keeps memory usage ≤3GB
- **Simple API**: Clean, intuitive API inspired by popular deep learning frameworks
- **Pure Python frontend**: Easy to understand and extend with a clean Python interface

## Installation

```bash
pip install barx
```

## Quick Start

```python
# Create and manipulate tensors
from barx.tensor import T
x = T.randn(32, 128)
y = x.dot(x.T)
print(y.mean())

# Define a neural network
from barx.nn import Linear, ReLU, Softmax, Sequential
model = Sequential(
    Linear(128, 64), ReLU(),
    Linear(64, 10), Softmax()
)

# Train with automatic differentiation
from barx.optim import SGD
optimizer = SGD(model.parameters(), lr=0.01)
for epoch in range(5):
    for x, y in data_loader:
        pred = model(x)
        loss = ((pred - y)**2).mean()
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
```

## Architecture

BARX is designed for simplicity and efficiency:

- **Pure-Python frontend** with clear abstractions for tensors and neural networks
- **Rust backends** for compute-intensive operations via PyO3 bindings
- **NumPy fallback** ensures all operations work even without Rust kernels
- **Automatic differentiation** for training neural networks from scratch
- **Efficient memory usage** with INT8 quantization support
- **Multi-threading** for operations on large tensors

## Examples

The `examples/` directory contains sample code demonstrating various features:

- Basic tensor operations
- Neural network training and inference
- INT8 quantization for large models

## Comparison with Other Frameworks

| Feature | BARX | NumPy | PyTorch | TensorFlow |
|---------|------|-------|---------|------------|
| **GPU Support** | ❌ | ❌ | ✅ | ✅ |
| **CPU Performance** | ✅ | ⚠️ | ✅ | ✅ |
| **Easy Installation** | ✅ | ✅ | ⚠️ | ⚠️ |
| **Small Footprint** | ✅ | ✅ | ❌ | ❌ |
| **Autograd** | ✅ | ❌ | ✅ | ✅ |
| **Edge Deployment** | ✅ | ⚠️ | ⚠️ | ⚠️ |

## Contributing

Contributions are welcome! Feel free to:

1. Report bugs or request features via issues
2. Submit pull requests with improvements
3. Help with documentation or examples
4. Share your experience using BARX

## License

MIT License
