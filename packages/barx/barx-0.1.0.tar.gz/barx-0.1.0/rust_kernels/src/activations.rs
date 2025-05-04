//! Activation function implementations.

use numpy::ndarray::{Array, ArrayView, Axis};
use numpy::Ix2;
use std::sync::Arc;
use rayon::prelude::*;

/// ReLU activation function implementation.
///
/// Computes the element-wise rectified linear function: max(0, x)
pub fn relu_impl(x: &ArrayView<f32, Ix2>) -> Array<f32, Ix2> {
    let (m, n) = (x.shape()[0], x.shape()[1]);
    let mut result = Array::zeros((m, n));
    let total_elements = m * n;
    
    // Threshold for parallel execution
    let use_parallel = total_elements > 10000;
    
    // Use chunk size for better cache efficiency
    let chunk_size = 1024; // Tuned for typical L1 cache size
    
    if use_parallel {
        // Parallel implementation using Rayon with chunking
        // Copy to owned for thread safety
        let x_owned = x.to_owned();
        
        // Create a flat view of both input and output for better memory locality
        let x_flat = x_owned.as_slice().unwrap();
        let result_flat = result.as_slice_mut().unwrap();
        
        // Process in parallel chunks
        result_flat.par_chunks_mut(chunk_size)
            .enumerate()
            .for_each(|(chunk_idx, out_chunk)| {
                let start_idx = chunk_idx * chunk_size;
                let end_idx = std::cmp::min(start_idx + chunk_size, total_elements);
                
                // Within each chunk, we can use SIMD-friendly loop patterns
                for i in 0..(end_idx - start_idx) {
                    let val = x_flat[start_idx + i];
                    out_chunk[i] = if val > 0.0 { val } else { 0.0 };
                }
            });
    } else {
        // Sequential implementation with cache-friendly access pattern
        // Get flat views for better memory locality
        let x_flat = x.as_slice().unwrap();
        let result_flat = result.as_slice_mut().unwrap();
        
        // Process in chunks for better cache utilization
        for chunk_start in (0..total_elements).step_by(chunk_size) {
            let chunk_end = std::cmp::min(chunk_start + chunk_size, total_elements);
            
            // Process current chunk
            // This straightforward loop is auto-vectorizable by the Rust compiler
            for i in chunk_start..chunk_end {
                result_flat[i] = f32::max(0.0, x_flat[i]);
            }
        }
    }
    
    result
}

/// Softmax activation function implementation.
///
/// Computes the softmax function along the specified axis.
pub fn softmax_impl(x: &ArrayView<f32, Ix2>, axis: usize) -> Array<f32, Ix2> {
    let (m, n) = (x.shape()[0], x.shape()[1]);
    let mut result = Array::zeros((m, n));
    let use_parallel = m * n > 10000; // Only parallelize for larger tensors
    
    if axis == 0 {
        // Softmax along columns (less common)
        if use_parallel {
            let x_owned = x.to_owned();
            let x_shared = Arc::new(x_owned);
            
            // Precompute max values for numerical stability
            let mut max_vals = vec![f32::MIN; n];
            for j in 0..n {
                for i in 0..m {
                    max_vals[j] = f32::max(max_vals[j], x[[i, j]]);
                }
            }
            let max_vals_shared = Arc::new(max_vals);
            
            // Compute columns in parallel
            let results: Vec<_> = (0..n).into_par_iter().map(|j| {
                let x_local = Arc::clone(&x_shared);
                let max_val = max_vals_shared[j];
                
                // Compute exp(x - max_val) for each element and sum
                let mut exps = vec![0.0; m];
                let mut sum = 0.0;
                
                for i in 0..m {
                    let exp_val = f32::exp(x_local[[i, j]] - max_val);
                    exps[i] = exp_val;
                    sum += exp_val;
                }
                
                // Normalize by sum of exps
                let sum_recip = 1.0 / sum; // Multiplication is faster than division
                for i in 0..m {
                    exps[i] *= sum_recip;
                }
                
                (j, exps)
            }).collect();
            
            // Copy results to output array
            for (j, col_vals) in results {
                for i in 0..m {
                    result[[i, j]] = col_vals[i];
                }
            }
        } else {
            // Sequential implementation
            for j in 0..n {
                // Find max value for numerical stability - vectorizable loop
                let mut max_val = f32::MIN;
                for i in 0..m {
                    max_val = f32::max(max_val, x[[i, j]]);
                }
                
                // Compute exp(x - max_val) and sum - cache friendly approach
                let mut sum = 0.0;
                let mut exps = vec![0.0; m];
                
                for i in 0..m {
                    let exp_val = f32::exp(x[[i, j]] - max_val);
                    exps[i] = exp_val;
                    sum += exp_val;
                }
                
                // Normalize with multiplication instead of division
                let sum_recip = 1.0 / sum;
                for i in 0..m {
                    result[[i, j]] = exps[i] * sum_recip;
                }
            }
        }
    } else {
        // Softmax along rows (more common case)
        if use_parallel {
            let x_owned = x.to_owned();
            let x_shared = Arc::new(x_owned);
            
            // Compute rows in parallel
            let results: Vec<_> = (0..m).into_par_iter().map(|i| {
                let x_local = Arc::clone(&x_shared);
                
                // Cache friendly approach: work with flat arrays
                let mut max_val = f32::MIN;
                for j in 0..n {
                    max_val = f32::max(max_val, x_local[[i, j]]);
                }
                
                // Pre-compute all exponentials
                let mut exps = vec![0.0; n];
                let mut sum = 0.0;
                
                // This loop pattern is SIMD friendly
                for j in 0..n {
                    let exp_val = f32::exp(x_local[[i, j]] - max_val);
                    exps[j] = exp_val;
                    sum += exp_val;
                }
                
                // Use reciprocal for faster computation
                let sum_recip = 1.0 / sum;
                for j in 0..n {
                    exps[j] *= sum_recip;
                }
                
                (i, exps)
            }).collect();
            
            // Copy results to output array
            for (i, row_vals) in results {
                for j in 0..n {
                    result[[i, j]] = row_vals[j];
                }
            }
        } else {
            // Sequential row-wise softmax with cache optimizations
            for i in 0..m {
                // Find max for numerical stability
                let mut max_val = f32::MIN;
                for j in 0..n {
                    max_val = f32::max(max_val, x[[i, j]]);
                }
                
                // Calculate exponentials and sum
                let mut sum = 0.0;
                
                // Use a stack-allocated array for small dimensions to avoid heap allocation
                const STACK_SIZE: usize = 128;
                if n <= STACK_SIZE {
                    let mut exps = [0.0; STACK_SIZE];
                    
                    for j in 0..n {
                        let exp_val = f32::exp(x[[i, j]] - max_val);
                        exps[j] = exp_val;
                        sum += exp_val;
                    }
                    
                    // Use multiplication by reciprocal instead of division
                    let sum_recip = 1.0 / sum;
                    for j in 0..n {
                        result[[i, j]] = exps[j] * sum_recip;
                    }
                } else {
                    // Heap allocation for larger dimensions
                    let mut exps = vec![0.0; n];
                    
                    for j in 0..n {
                        let exp_val = f32::exp(x[[i, j]] - max_val);
                        exps[j] = exp_val;
                        sum += exp_val;
                    }
                    
                    // Normalize with multiplication
                    let sum_recip = 1.0 / sum;
                    for j in 0..n {
                        result[[i, j]] = exps[j] * sum_recip;
                    }
                }
            }
        }
    }
    
    result
}

#[cfg(test)]
mod tests {
    use super::*;
    use numpy::ndarray::Array;
    use approx::assert_relative_eq;
    
    #[test]
    fn test_relu() {
        let x = Array::from_shape_vec((2, 3), vec![
            -1.0, 0.0, 1.0,
            -2.0, 2.0, 3.0
        ]).unwrap();
        
        let result = relu_impl(&x.view());
        
        let expected = Array::from_shape_vec((2, 3), vec![
            0.0, 0.0, 1.0,
            0.0, 2.0, 3.0
        ]).unwrap();
        
        assert_eq!(result, expected);
    }
    
    #[test]
    fn test_softmax_row() {
        let x = Array::from_shape_vec((2, 3), vec![
            1.0, 2.0, 3.0,
            4.0, 5.0, 6.0
        ]).unwrap();
        
        let result = softmax_impl(&x.view(), 1);
        
        // For first row: e^1, e^2, e^3 -> normalize
        // For second row: e^4, e^5, e^6 -> normalize
        let row1_sum = f32::exp(1.0 - 3.0) + f32::exp(2.0 - 3.0) + f32::exp(3.0 - 3.0);
        let row2_sum = f32::exp(4.0 - 6.0) + f32::exp(5.0 - 6.0) + f32::exp(6.0 - 6.0);
        
        let expected = Array::from_shape_vec((2, 3), vec![
            f32::exp(1.0 - 3.0) / row1_sum, f32::exp(2.0 - 3.0) / row1_sum, f32::exp(3.0 - 3.0) / row1_sum,
            f32::exp(4.0 - 6.0) / row2_sum, f32::exp(5.0 - 6.0) / row2_sum, f32::exp(6.0 - 6.0) / row2_sum
        ]).unwrap();
        
        // Check with approximate equality due to floating point
        for i in 0..2 {
            for j in 0..3 {
                assert_relative_eq!(result[[i, j]], expected[[i, j]], epsilon = 1e-5);
            }
        }
    }
}
