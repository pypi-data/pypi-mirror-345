//! Rust kernels for BARX.
//!
//! This crate provides high-performance kernels for BARX using SIMD 
//! instructions where available.

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use numpy::{Ix2, Ix4, IntoPyArray, PyArray, PyReadonlyArrayDyn};
use numpy::ndarray::{Array};

// Import module-specific implementations
mod matmul;
mod conv;
mod activations;
mod quantize;

use matmul::matmul_impl;
use conv::conv2d_impl;
use activations::{relu_impl, softmax_impl};
use quantize::{quantize_int8_impl, dequantize_int8_impl};

/// Matrix multiplication kernel.
///
/// Computes the matrix multiplication of two 2D arrays.
#[pyfunction]
fn matmul_kernel<'py>(
    py: Python<'py>,
    a: PyReadonlyArrayDyn<'py, f32>,
    b: PyReadonlyArrayDyn<'py, f32>
) -> PyResult<&'py PyArray<f32, Ix2>> {
    let a_view = a.as_array();
    let b_view = b.as_array();
    
    if a_view.ndim() != 2 || b_view.ndim() != 2 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Both inputs must be 2D arrays"
        ));
    }
    
    let a_shape = a_view.shape();
    let b_shape = b_view.shape();
    
    if a_shape[1] != b_shape[0] {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Incompatible shapes for matmul: {:?} and {:?}", a_shape, b_shape)
        ));
    }
    
    let result = matmul_impl(&a_view.into_dimensionality::<Ix2>().unwrap(), 
                           &b_view.into_dimensionality::<Ix2>().unwrap());
    
    Ok(result.into_pyarray(py))
}

/// 2D convolution kernel.
///
/// Computes the 2D convolution of an input tensor with a kernel.
#[pyfunction]
fn conv2d<'py>(
    py: Python<'py>,
    input: PyReadonlyArrayDyn<'py, f32>,
    kernel: PyReadonlyArrayDyn<'py, f32>,
    stride: usize
) -> PyResult<&'py PyArray<f32, Ix4>> {
    let input_view = input.as_array();
    let kernel_view = kernel.as_array();
    
    if input_view.ndim() != 4 || kernel_view.ndim() != 4 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Input and kernel must be 4D arrays"
        ));
    }
    
    let result = conv2d_impl(
        &input_view.into_dimensionality::<Ix4>().unwrap(),
        &kernel_view.into_dimensionality::<Ix4>().unwrap(),
        stride
    );
    
    Ok(result.into_pyarray(py))
}

/// ReLU activation function.
///
/// Applies the rectified linear unit function element-wise: max(0, x)
#[pyfunction]
fn relu<'py>(
    py: Python<'py>,
    x: PyReadonlyArrayDyn<'py, f32>
) -> PyResult<&'py PyArray<f32, Ix2>> {
    let x_view = x.as_array();
    
    if x_view.ndim() != 2 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Input must be a 2D array"
        ));
    }
    
    let result = relu_impl(&x_view.into_dimensionality::<Ix2>().unwrap());
    
    Ok(result.into_pyarray(py))
}

/// Softmax activation function.
///
/// Applies the softmax function along the specified axis.
#[pyfunction]
fn softmax<'py>(
    py: Python<'py>,
    x: PyReadonlyArrayDyn<'py, f32>,
    axis: i64
) -> PyResult<&'py PyArray<f32, Ix2>> {
    let x_view = x.as_array();
    
    if x_view.ndim() != 2 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Input must be a 2D array"
        ));
    }
    
    // Convert negative axis to positive
    let axis_pos = if axis < 0 { 
        (x_view.ndim() as i64 + axis) as usize 
    } else { 
        axis as usize 
    };
    
    let result = softmax_impl(&x_view.into_dimensionality::<Ix2>().unwrap(), axis_pos);
    
    Ok(result.into_pyarray(py))
}

/// Quantize a matrix to INT8.
///
/// Quantizes a floating-point matrix to INT8 format.
#[pyfunction]
fn quantize_int8<'py>(
    py: Python<'py>,
    x: PyReadonlyArrayDyn<'py, f32>
) -> PyResult<(Py<PyArray<i8, Ix2>>, f32)> {
    let x_view = x.as_array();
    
    if x_view.ndim() != 2 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Input must be a 2D array"
        ));
    }
    
    let (quantized, scale) = quantize_int8_impl(&x_view.into_dimensionality::<Ix2>().unwrap());
    
    Ok((quantized.into_pyarray(py).to_owned(), scale))
}

/// Dequantize an INT8 matrix.
///
/// Dequantizes an INT8 matrix back to floating point.
#[pyfunction]
fn dequantize_int8<'py>(
    py: Python<'py>,
    x: PyReadonlyArrayDyn<'py, i8>,
    scale: f32
) -> PyResult<&'py PyArray<f32, Ix2>> {
    let x_view = x.as_array();
    
    if x_view.ndim() != 2 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Input must be a 2D array"
        ));
    }
    
    let result = dequantize_int8_impl(&x_view.into_dimensionality::<Ix2>().unwrap(), scale);
    
    Ok(result.into_pyarray(py))
}

/// Register Python module.
#[pymodule]
fn _rust_kernels(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(matmul_kernel, m)?)?;
    m.add_function(wrap_pyfunction!(conv2d, m)?)?;
    m.add_function(wrap_pyfunction!(relu, m)?)?;
    m.add_function(wrap_pyfunction!(softmax, m)?)?;
    m.add_function(wrap_pyfunction!(quantize_int8, m)?)?;
    m.add_function(wrap_pyfunction!(dequantize_int8, m)?)?;
    
    Ok(())
}
