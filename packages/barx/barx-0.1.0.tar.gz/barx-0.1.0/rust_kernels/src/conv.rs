//! 2D Convolution implementation.

use numpy::ndarray::{Array, ArrayView};
use numpy::{Ix2, Ix4};
use rayon::prelude::*;
use std::sync::Arc;

/// 2D convolution implementation.
///
/// Performs 2D convolution with SIMD and multi-threading optimizations.
use crate::matmul::matmul_impl;

/// Convert input to matrix using im2col approach.
///
/// im2col unfolds input tensor into a matrix where each column corresponds to
/// a convolution window, allowing to compute convolution as matrix multiplication.
fn im2col(
    input: &ArrayView<f32, Ix4>, 
    batch_idx: usize,
    kernel_height: usize, 
    kernel_width: usize, 
    stride: usize,
    out_height: usize,
    out_width: usize
) -> Array<f32, Ix2> {
    let (_, in_channels, _, _) = (
        input.shape()[0],
        input.shape()[1], 
        input.shape()[2], 
        input.shape()[3]
    );
    
    // Each column will contain the values from a convolution window
    // Number of rows = kernel_height * kernel_width * in_channels
    // Number of columns = out_height * out_width
    let col_size = kernel_height * kernel_width * in_channels;
    let col_count = out_height * out_width;
    let mut result = Array::zeros((col_size, col_count));
    
    // Fill the matrix by unfolding input tensor
    for c in 0..in_channels {
        for kh in 0..kernel_height {
            for kw in 0..kernel_width {
                let row_idx = c * kernel_height * kernel_width + kh * kernel_width + kw;
                
                for oh in 0..out_height {
                    for ow in 0..out_width {
                        let col_idx = oh * out_width + ow;
                        let ih = oh * stride + kh;
                        let iw = ow * stride + kw;
                        
                        result[[row_idx, col_idx]] = input[[batch_idx, c, ih, iw]];
                    }
                }
            }
        }
    }
    
    result
}

/// Reshape kernel for matrix multiplication.
///
/// Converts kernel tensor into a matrix suitable for matmul with im2col output.
fn reshape_kernel(kernel: &ArrayView<f32, Ix4>) -> Array<f32, Ix2> {
    let (out_channels, in_channels, kernel_height, kernel_width) = (
        kernel.shape()[0], 
        kernel.shape()[1], 
        kernel.shape()[2], 
        kernel.shape()[3]
    );
    
    // Each row contains weights for one output channel
    // Number of rows = out_channels
    // Number of columns = kernel_height * kernel_width * in_channels
    let mut result = Array::zeros((out_channels, kernel_height * kernel_width * in_channels));
    
    for out_c in 0..out_channels {
        for in_c in 0..in_channels {
            for kh in 0..kernel_height {
                for kw in 0..kernel_width {
                    let col_idx = in_c * kernel_height * kernel_width + kh * kernel_width + kw;
                    result[[out_c, col_idx]] = kernel[[out_c, in_c, kh, kw]];
                }
            }
        }
    }
    
    result
}

pub fn conv2d_impl(
    input: &ArrayView<f32, Ix4>,
    kernel: &ArrayView<f32, Ix4>,
    stride: usize
) -> Array<f32, Ix4> {
    let (batch_size, in_channels, in_height, in_width) = (
        input.shape()[0],
        input.shape()[1],
        input.shape()[2],
        input.shape()[3]
    );
    
    let (out_channels, _, kernel_height, kernel_width) = (
        kernel.shape()[0],
        kernel.shape()[1],
        kernel.shape()[2],
        kernel.shape()[3]
    );
    
    // Calculate output dimensions
    let out_height = (in_height - kernel_height) / stride + 1;
    let out_width = (in_width - kernel_width) / stride + 1;
    
    // Create output array
    let mut output = Array::zeros((batch_size, out_channels, out_height, out_width));
    
    // Reshape kernel to a matrix (out_channels x (kernel_h * kernel_w * in_channels))
    let kernel_matrix = reshape_kernel(kernel);
    
    // Determine if we should use parallel execution
    let use_parallel = batch_size > 1;
    
    // Process each batch in parallel
    if use_parallel {
        let input_shared = Arc::new(input.to_owned());
        let kernel_matrix_shared = Arc::new(kernel_matrix);
        
        // Create a vector to hold per-batch outputs
        let mut batch_outputs: Vec<_> = (0..batch_size)
            .into_par_iter()
            .map(|batch_idx| {
                let input_local = Arc::clone(&input_shared);
                let kernel_matrix_local = Arc::clone(&kernel_matrix_shared);
                
                // Convert input to columns matrix for this batch
                let col_matrix = im2col(
                    &input_local.view(),
                    batch_idx,
                    kernel_height,
                    kernel_width,
                    stride,
                    out_height,
                    out_width
                );
                
                // Perform matrix multiplication: kernel_matrix * col_matrix
                // Result: (out_channels) x (out_height * out_width)
                let output_matrix = matmul_impl(&kernel_matrix_local.view(), &col_matrix.view());
                
                // Create a batch output tensor
                let mut batch_output = Array::zeros((out_channels, out_height, out_width));
                
                // Reshape the output matrix to batch output tensor
                for oc in 0..out_channels {
                    for oh in 0..out_height {
                        for ow in 0..out_width {
                            let flat_idx = oh * out_width + ow;
                            batch_output[[oc, oh, ow]] = output_matrix[[oc, flat_idx]];
                        }
                    }
                }
                
                (batch_idx, batch_output)
            })
            .collect();
        
        // Copy batch outputs to the final output tensor
        for (batch_idx, batch_output) in batch_outputs {
            for oc in 0..out_channels {
                for oh in 0..out_height {
                    for ow in 0..out_width {
                        output[[batch_idx, oc, oh, ow]] = batch_output[[oc, oh, ow]];
                    }
                }
            }
        }
    } else {
        // Sequential processing for single batch
        for batch_idx in 0..batch_size {
            // Convert input to columns matrix for this batch
            let col_matrix = im2col(
                input,
                batch_idx,
                kernel_height,
                kernel_width,
                stride,
                out_height,
                out_width
            );
            
            // Perform matrix multiplication: kernel_matrix * col_matrix
            let output_matrix = matmul_impl(&kernel_matrix.view(), &col_matrix.view());
            
            // Reshape the output matrix back to output tensor
            for oc in 0..out_channels {
                for oh in 0..out_height {
                    for ow in 0..out_width {
                        let flat_idx = oh * out_width + ow;
                        output[[batch_idx, oc, oh, ow]] = output_matrix[[oc, flat_idx]];
                    }
                }
            }
        }
    }
    
    output
}

#[cfg(test)]
mod tests {
    use super::*;
    use numpy::ndarray::Array;
    
    #[test]
    fn test_conv2d() {
        // Simple 1x1x3x3 input, 1x1x2x2 kernel, stride=1
        let input = Array::from_shape_vec((1, 1, 3, 3), vec![
            1.0, 2.0, 3.0,
            4.0, 5.0, 6.0,
            7.0, 8.0, 9.0
        ]).unwrap();
        
        let kernel = Array::from_shape_vec((1, 1, 2, 2), vec![
            1.0, 2.0,
            3.0, 4.0
        ]).unwrap();
        
        let output = conv2d_impl(&input.view(), &kernel.view(), 1);
        
        // Expected output:
        // [1*1 + 2*2 + 4*3 + 5*4, 2*1 + 3*2 + 5*3 + 6*4]
        // [4*1 + 5*2 + 7*3 + 8*4, 5*1 + 6*2 + 8*3 + 9*4]
        // = [37, 47, 67, 87]
        let expected = Array::from_shape_vec((1, 1, 2, 2), vec![
            37.0, 47.0,
            67.0, 87.0
        ]).unwrap();
        
        assert_eq!(output, expected);
    }
}
