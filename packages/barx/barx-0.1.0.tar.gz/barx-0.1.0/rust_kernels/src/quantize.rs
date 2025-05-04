//! Quantization implementations.

use numpy::ndarray::{Array, ArrayView, Axis};
use numpy::Ix2;
use std::sync::Arc;
use rayon::prelude::*;

/// Quantize a matrix to INT8 format.
///
/// Scales and quantizes a floating-point matrix to INT8 range [-127, 127].
pub fn quantize_int8_impl(x: &ArrayView<f32, Ix2>) -> (Array<i8, Ix2>, f32) {
    let (m, n) = (x.shape()[0], x.shape()[1]);
    let mut result = Array::zeros((m, n));
    let total_elements = m * n;
    
    // Get flat views for better cache utilization during max abs search
    let x_flat = x.as_slice().unwrap();
    
    // Find max absolute value using chunked approach for better cache performance
    const CHUNK_SIZE: usize = 1024;
    let mut max_abs = 0.0f32;
    
    for chunk_start in (0..total_elements).step_by(CHUNK_SIZE) {
        let chunk_end = std::cmp::min(chunk_start + CHUNK_SIZE, total_elements);
        
        // This sequential pattern is easily auto-vectorizable
        let mut chunk_max = 0.0f32;
        for i in chunk_start..chunk_end {
            chunk_max = f32::max(chunk_max, f32::abs(x_flat[i]));
        }
        
        max_abs = f32::max(max_abs, chunk_max);
    }
    
    // Calculate scale factor: max_abs / 127.0
    let scale = if max_abs > 0.0 { max_abs / 127.0 } else { 1.0 };
    let scale_recip = 1.0 / scale; // Use reciprocal for faster computation
    
    // Determine if we should use parallel execution
    let use_parallel = total_elements > 10000; // Only use parallel for larger matrices
    
    if use_parallel {
        // Get flat mutable view of result for better memory access pattern
        let result_flat = result.as_slice_mut().unwrap();
        
        // Process in parallel chunks
        result_flat.par_chunks_mut(CHUNK_SIZE)
            .enumerate()
            .for_each(|(chunk_idx, out_chunk)| {
                let start_idx = chunk_idx * CHUNK_SIZE;
                let end_idx = std::cmp::min(start_idx + CHUNK_SIZE, total_elements);
                
                // Process current chunk with auto-vectorizable pattern
                for i in 0..(end_idx - start_idx) {
                    let val = x_flat[start_idx + i] * scale_recip;
                    // Clip to [-127, 127] range and round
                    out_chunk[i] = f32::round(f32::max(-127.0, f32::min(127.0, val))) as i8;
                }
            });
    } else {
        // Sequential implementation with cache-friendly access
        let result_flat = result.as_slice_mut().unwrap();
        
        // Process in chunks for better cache utilization
        for chunk_start in (0..total_elements).step_by(CHUNK_SIZE) {
            let chunk_end = std::cmp::min(chunk_start + CHUNK_SIZE, total_elements);
            
            // Process current chunk with vectorization-friendly pattern
            for i in chunk_start..chunk_end {
                let val = x_flat[i] * scale_recip;
                // Clip to [-127, 127] range and round
                result_flat[i] = f32::round(f32::max(-127.0, f32::min(127.0, val))) as i8;
            }
        }
    }
    
    (result, scale)
}

/// Dequantize an INT8 matrix back to floating point.
///
/// Converts a quantized INT8 matrix back to floating point using the scale factor.
pub fn dequantize_int8_impl(x: &ArrayView<i8, Ix2>, scale: f32) -> Array<f32, Ix2> {
    let (m, n) = (x.shape()[0], x.shape()[1]);
    let mut result = Array::zeros((m, n));
    
    // Determine if we should use parallel execution
    let use_parallel = m * n > 10000; // Only use parallel for larger matrices
    
    if use_parallel {
        // Parallel implementation using Rayon
        let x_owned = x.to_owned();
        let x_shared = Arc::new(x_owned);
        
        // Compute rows in parallel
        let results: Vec<_> = (0..m).into_par_iter().map(|i| {
            let x_local = Arc::clone(&x_shared);
            let mut row_result = vec![0.0; n];
            
            for j in 0..n {
                row_result[j] = x_local[[i, j]] as f32 * scale;
            }
            
            (i, row_result)
        }).collect();
        
        // Copy results to output array
        for (i, row_vals) in results {
            for j in 0..n {
                result[[i, j]] = row_vals[j];
            }
        }
    } else {
        // Sequential implementation for smaller matrices
        for i in 0..m {
            for j in 0..n {
                result[[i, j]] = x[[i, j]] as f32 * scale;
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
    fn test_quantize_dequantize() {
        let x = Array::from_shape_vec((2, 3), vec![
            -10.0, 0.0, 10.0,
            -5.0, 5.0, 20.0
        ]).unwrap();
        
        let (quantized, scale) = quantize_int8_impl(&x.view());
        let dequantized = dequantize_int8_impl(&quantized.view(), scale);
        
        // Expected scale: 20.0 / 127.0
        let expected_scale = 20.0 / 127.0;
        assert_relative_eq!(scale, expected_scale, epsilon = 1e-5);
        
        // Check that dequantized values are close to original
        // There will be some precision loss due to quantization
        for i in 0..2 {
            for j in 0..3 {
                assert_relative_eq!(
                    dequantized[[i, j]], 
                    x[[i, j]], 
                    epsilon = scale * 1.0 // Allow error up to one quantization step
                );
            }
        }
    }
    
    #[test]
    fn test_quantize_zero() {
        let x = Array::from_shape_vec((2, 2), vec![
            0.0, 0.0, 
            0.0, 0.0
        ]).unwrap();
        
        let (quantized, scale) = quantize_int8_impl(&x.view());
        
        // Scale should be 1.0 for all zeros
        assert_eq!(scale, 1.0);
        
        // All values should be quantized to zero
        for i in 0..2 {
            for j in 0..2 {
                assert_eq!(quantized[[i, j]], 0);
            }
        }
    }
}
