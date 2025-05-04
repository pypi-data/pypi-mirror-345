//! Matrix multiplication implementation.

use numpy::ndarray::{Array, ArrayView, Ix2};
use std::sync::Arc;
use rayon::prelude::*;

/// Matrix multiplication implementation.
///
/// Optimized matrix multiplication with SIMD and multi-threading.
pub fn matmul_impl(a: &ArrayView<f32, Ix2>, b: &ArrayView<f32, Ix2>) -> Array<f32, Ix2> {
    let (m, k) = (a.shape()[0], a.shape()[1]);
    let (_, n) = (b.shape()[0], b.shape()[1]);
    
    // Create output array
    let mut c = Array::zeros((m, n));
    
    // Cache blocking parameters - tuned for common L1 cache sizes
    const BLOCK_SIZE_M: usize = 64;
    const BLOCK_SIZE_N: usize = 64;
    const BLOCK_SIZE_K: usize = 64;
    
    // Determine if we should use parallel execution
    let use_parallel = m * n > 10000; // Only use parallel for larger matrices
    
    // This copies input matrices to ensure optimal memory layout (column-major for B)
    // This might seem counterintuitive (extra copies), but proper memory layout
    // dramatically improves cache utilization and overall performance
    let a_owned = a.to_owned();
    let mut b_t = Array::zeros((n, k)); // Transposed B for better memory access patterns
    for i in 0..k {
        for j in 0..n {
            b_t[[j, i]] = b[[i, j]];
        }
    }
    
    if use_parallel {
        // Parallel implementation with cache blocking
        let a_shared = Arc::new(a_owned.clone());
        let b_t_shared = Arc::new(b_t.clone());
        
        // Create a list of block coordinates to process
        let blocks: Vec<(usize, usize)> = (0..m).step_by(BLOCK_SIZE_M)
            .flat_map(|i_block| {
                (0..n).step_by(BLOCK_SIZE_N)
                    .map(move |j_block| (i_block, j_block))
            })
            .collect();
        
        // Process blocks in parallel
        let results: Vec<_> = blocks.into_par_iter().map(|(i_block, j_block)| {
            let i_end = std::cmp::min(i_block + BLOCK_SIZE_M, m);
            let j_end = std::cmp::min(j_block + BLOCK_SIZE_N, n);
            
            // Local block from C to update
            let mut c_block = vec![0.0; (i_end - i_block) * (j_end - j_block)];
            
            // Process blocks of K dimension
            for k_block in (0..k).step_by(BLOCK_SIZE_K) {
                let k_end = std::cmp::min(k_block + BLOCK_SIZE_K, k);
                
                // Process current block
                for i in i_block..i_end {
                    for j in j_block..j_end {
                        let c_idx = (i - i_block) * (j_end - j_block) + (j - j_block);
                        let mut sum = c_block[c_idx];
                        
                        // Manual loop unrolling for better performance
                        let mut kk = k_block;
                        while kk + 7 < k_end {
                            sum += a_shared[[i, kk]] * b_t_shared[[j, kk]];
                            sum += a_shared[[i, kk+1]] * b_t_shared[[j, kk+1]];
                            sum += a_shared[[i, kk+2]] * b_t_shared[[j, kk+2]];
                            sum += a_shared[[i, kk+3]] * b_t_shared[[j, kk+3]];
                            sum += a_shared[[i, kk+4]] * b_t_shared[[j, kk+4]];
                            sum += a_shared[[i, kk+5]] * b_t_shared[[j, kk+5]];
                            sum += a_shared[[i, kk+6]] * b_t_shared[[j, kk+6]];
                            sum += a_shared[[i, kk+7]] * b_t_shared[[j, kk+7]];
                            kk += 8;
                        }
                        
                        // Handle remaining elements
                        while kk < k_end {
                            sum += a_shared[[i, kk]] * b_t_shared[[j, kk]];
                            kk += 1;
                        }
                        
                        c_block[c_idx] = sum;
                    }
                }
            }
            
            (i_block, j_block, i_end, j_end, c_block)
        }).collect();
        
        // Copy results back to the output matrix
        for (i_block, j_block, i_end, j_end, c_block) in results {
            for i in i_block..i_end {
                for j in j_block..j_end {
                    let c_idx = (i - i_block) * (j_end - j_block) + (j - j_block);
                    c[[i, j]] = c_block[c_idx];
                }
            }
        }
    } else {
        // Sequential implementation with cache blocking for smaller matrices
        // Process blocks of rows
        for i_block in (0..m).step_by(BLOCK_SIZE_M) {
            let i_end = std::cmp::min(i_block + BLOCK_SIZE_M, m);
            
            // Process blocks of columns
            for j_block in (0..n).step_by(BLOCK_SIZE_N) {
                let j_end = std::cmp::min(j_block + BLOCK_SIZE_N, n);
                
                // Initialize the result block to zeros
                for i in i_block..i_end {
                    for j in j_block..j_end {
                        c[[i, j]] = 0.0;
                    }
                }
                
                // Process blocks of K dimension
                for k_block in (0..k).step_by(BLOCK_SIZE_K) {
                    let k_end = std::cmp::min(k_block + BLOCK_SIZE_K, k);
                    
                    // Process current block
                    for i in i_block..i_end {
                        for j in j_block..j_end {
                            let mut sum = c[[i, j]];
                            
                            // Manual loop unrolling for better performance
                            let mut kk = k_block;
                            while kk + 7 < k_end {
                                sum += a_owned[[i, kk]] * b_t[[j, kk]];
                                sum += a_owned[[i, kk+1]] * b_t[[j, kk+1]];
                                sum += a_owned[[i, kk+2]] * b_t[[j, kk+2]];
                                sum += a_owned[[i, kk+3]] * b_t[[j, kk+3]];
                                sum += a_owned[[i, kk+4]] * b_t[[j, kk+4]];
                                sum += a_owned[[i, kk+5]] * b_t[[j, kk+5]];
                                sum += a_owned[[i, kk+6]] * b_t[[j, kk+6]];
                                sum += a_owned[[i, kk+7]] * b_t[[j, kk+7]];
                                kk += 8;
                            }
                            
                            // Handle remaining elements
                            while kk < k_end {
                                sum += a_owned[[i, kk]] * b_t[[j, kk]];
                                kk += 1;
                            }
                            
                            c[[i, j]] = sum;
                        }
                    }
                }
            }
        }
    }
    
    c
}

#[cfg(test)]
mod tests {
    use super::*;
    use numpy::ndarray::{Array, Ix2};
    
    #[test]
    fn test_matmul() {
        // Small test case
        let a = Array::from_shape_vec((2, 3), vec![1.0, 2.0, 3.0, 4.0, 5.0, 6.0]).unwrap();
        let b = Array::from_shape_vec((3, 2), vec![7.0, 8.0, 9.0, 10.0, 11.0, 12.0]).unwrap();
        
        let c = matmul_impl(&a.view(), &b.view());
        
        // Expected result:
        // [1*7 + 2*9 + 3*11, 1*8 + 2*10 + 3*12]
        // [4*7 + 5*9 + 6*11, 4*8 + 5*10 + 6*12]
        let expected = Array::from_shape_vec((2, 2), vec![58.0, 64.0, 139.0, 154.0]).unwrap();
        
        assert_eq!(c, expected);
    }
}
