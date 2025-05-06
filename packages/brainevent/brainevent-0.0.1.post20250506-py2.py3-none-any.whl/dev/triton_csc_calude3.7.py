# Copyright 2025 BDP Ecosystem Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

# -*- coding: utf-8 -*-
import torch
import triton
import triton.language as tl


@triton.jit
def csc_spmm_kernel(
    # Pointers to matrices
    a_indptr_ptr, a_indices_ptr, a_data_ptr,  # CSC format: indptr, indices, data
    b_ptr,  # Dense matrix B (row-major)
    c_ptr,  # Output matrix C (row-major)

    # Matrix dimensions
    M, N, K,  # C (M x N) = A (M x K) @ B (K x N)

    # Meta-parameters
    BLOCK_SIZE_M: tl.constexpr,
    BLOCK_SIZE_N: tl.constexpr,
):
    """
    Kernel for computing C = A @ B where A is in CSC format and B is a dense matrix.

    CSC format for A:
    - a_indptr_ptr: column pointers (size K+1)
    - a_indices_ptr: row indices (size nnz)
    - a_data_ptr: non-zero values (size nnz)
    """
    # Program ID
    pid_m = tl.program_id(axis=0)
    pid_n = tl.program_id(axis=1)

    # Compute the block's starting position in the output matrix C
    block_start_m = pid_m * BLOCK_SIZE_M
    block_start_n = pid_n * BLOCK_SIZE_N

    # Generate offset ranges for the m and n dimensions
    offs_m = block_start_m + tl.arange(0, BLOCK_SIZE_M)
    offs_n = block_start_n + tl.arange(0, BLOCK_SIZE_N)

    # Initialize the output block with zeros
    c_block = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)

    # Create a mask for the valid outputs (in case M or N is not a multiple of BLOCK_SIZE)
    mask_m = offs_m < M
    mask_n = offs_n < N

    # Loop over columns of A / rows of B
    for k in range(K):
        # Load A's column pointers for current and next column
        col_start = tl.load(a_indptr_ptr + k)
        col_end = tl.load(a_indptr_ptr + k + 1)

        # Process the nonzeros in this column of A
        for idx in range(col_start, col_end):
            # Load row index and value of A
            row_idx = tl.load(a_indices_ptr + idx)
            val_a = tl.load(a_data_ptr + idx)

            # Check if this row is within our block's row range
            is_in_block = (row_idx >= block_start_m) & (row_idx < block_start_m + BLOCK_SIZE_M)

            if is_in_block:
                # Compute local row index within our block
                local_row = row_idx - block_start_m

                # Load the row of B corresponding to this column of A
                # B is assumed to be in row-major order
                b_row_ptr = b_ptr + k * N + offs_n
                b_row = tl.load(b_row_ptr, mask=mask_n, other=0.0)

                # Update the corresponding row of C
                c_block = tl.where(
                    (tl.arange(0, BLOCK_SIZE_M)[:, None] == local_row) & mask_m[:, None],
                    c_block + val_a * b_row[None, :],
                    c_block
                )

    # Write results back to C
    c_ptrs = c_ptr + offs_m[:, None] * N + offs_n[None, :]
    mask = mask_m[:, None] & mask_n[None, :]
    tl.store(c_ptrs, c_block, mask=mask)


def csc_spmm(A_csc, B, M, K, N, block_size_m=32, block_size_n=32):
    """
    Computes C = A @ B where A is a sparse matrix in CSC format and B is a dense matrix.

    Args:
        A_csc: Tuple of (indptr, indices, data) representing matrix A in CSC format
        B: Dense tensor of shape (K, N)
        M: Number of rows in A
        K: Number of columns in A / Number of rows in B
        N: Number of columns in B
        block_size_m: Block size for M dimension
        block_size_n: Block size for N dimension

    Returns:
        C: Dense tensor of shape (M, N) resulting from A @ B
    """
    indptr, indices, data = A_csc

    # Create output matrix
    C = torch.zeros((M, N), device=B.device, dtype=B.dtype)

    # Set up grid for kernel
    grid = (triton.cdiv(M, block_size_m), triton.cdiv(N, block_size_n))

    # Launch kernel
    csc_spmm_kernel[grid](
        indptr, indices, data,
        B, C,
        M, N, K,
        BLOCK_SIZE_M=block_size_m,
        BLOCK_SIZE_N=block_size_n,
    )

    return C


# Helper function to convert scipy CSC matrix to PyTorch tensors
def scipy_csc_to_torch(csc_matrix, device='cuda'):
    indptr = torch.from_numpy(csc_matrix.indptr.astype('int32')).to(device)
    indices = torch.from_numpy(csc_matrix.indices.astype('int32')).to(device)
    data = torch.from_numpy(csc_matrix.data.astype('float32')).to(device)
    return indptr, indices, data


# Example usage
if __name__ == "__main__":
    import numpy as np
    import scipy.sparse as sp
    import time

    # Create a sparse matrix A in CSC format
    M, K = 1024, 1024
    density = 0.01  # 1% of elements are non-zero

    # Create a random sparse matrix in CSC format
    A_scipy = sp.random(M, K, density=density, format='csc', dtype=np.float32)

    # Create a random dense matrix B
    N = 1024
    B_np = np.random.rand(K, N).astype(np.float32)

    # Convert to PyTorch tensors
    A_torch = scipy_csc_to_torch(A_scipy)
    B_torch = torch.from_numpy(B_np).cuda()

    # Expected result using SciPy
    start_time = time.time()
    expected = A_scipy @ B_np
    scipy_time = time.time() - start_time
    print(f"SciPy time: {scipy_time:.6f} seconds")

    # Result using our Triton kernel
    start_time = time.time()
    result = csc_spmm(A_torch, B_torch, M, K, N)
    triton_time = time.time() - start_time
    print(f"Triton time: {triton_time:.6f} seconds")

    # Verify results
    expected_torch = torch.from_numpy(expected).cuda()
    max_diff = torch.max(torch.abs(result - expected_torch))
    print(f"Maximum difference: {max_diff}")
    print(f"Speedup: {scipy_time / triton_time:.2f}x")

    # Benchmark with different block sizes
    block_sizes = [(16, 16), (32, 32), (64, 64), (128, 128)]
    for bm, bn in block_sizes:
        start_time = time.time()
        result = csc_spmm(A_torch, B_torch, M, K, N, block_size_m=bm, block_size_n=bn)
        triton_time = time.time() - start_time
        print(f"Block size ({bm}, {bn}): {triton_time:.6f} seconds")


# More optimized version of the kernel using tile loading for B
@triton.jit
def csc_spmm_optimized_kernel(
    # Pointers to matrices
    a_indptr_ptr, a_indices_ptr, a_data_ptr,  # CSC format
    b_ptr,  # Dense matrix B (row-major)
    c_ptr,  # Output matrix C (row-major)

    # Matrix dimensions
    M, N, K,  # C (M x N) = A (M x K) @ B (K x N)

    # Meta-parameters
    BLOCK_SIZE_M: tl.constexpr,
    BLOCK_SIZE_N: tl.constexpr,
    GROUP_SIZE_K: tl.constexpr,
):
    """
    More optimized kernel for computing C = A @ B where A is in CSC format and B is dense.
    This version processes groups of columns for better memory access patterns.
    """
    # Program ID
    pid_m = tl.program_id(axis=0)
    pid_n = tl.program_id(axis=1)

    # Compute the block's starting position in the output matrix C
    block_start_m = pid_m * BLOCK_SIZE_M
    block_start_n = pid_n * BLOCK_SIZE_N

    # Generate offset ranges for the m and n dimensions
    offs_m = block_start_m + tl.arange(0, BLOCK_SIZE_M)
    offs_n = block_start_n + tl.arange(0, BLOCK_SIZE_N)

    # Initialize the output block with zeros
    c_block = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)

    # Create a mask for the valid outputs
    mask_m = offs_m < M
    mask_n = offs_n < N

    # Process K columns in groups for better locality
    for k_group in range(0, K, GROUP_SIZE_K):
        k_end = tl.minimum(k_group + GROUP_SIZE_K, K)

        # Process each column in the group
        for k in range(k_group, k_end):
            # Load A's column pointers
            col_start = tl.load(a_indptr_ptr + k)
            col_end = tl.load(a_indptr_ptr + k + 1)

            # Process nonzeros in this column
            for idx in range(col_start, col_end):
                row_idx = tl.load(a_indices_ptr + idx)
                val_a = tl.load(a_data_ptr + idx)

                # Check if row is within our block
                row_in_block = (row_idx >= block_start_m) & (row_idx < block_start_m + BLOCK_SIZE_M)

                if row_in_block:
                    # Compute local row index
                    local_row = row_idx - block_start_m

                    # Load corresponding row of B
                    b_row_ptr = b_ptr + k * N + offs_n
                    b_row = tl.load(b_row_ptr, mask=mask_n, other=0.0)

                    # Update the output block
                    c_block = tl.where(
                        (tl.arange(0, BLOCK_SIZE_M)[:, None] == local_row) & mask_m[:, None],
                        c_block + val_a * b_row[None, :],
                        c_block
                    )

    # Write results back to C
    c_ptrs = c_ptr + offs_m[:, None] * N + offs_n[None, :]
    mask = mask_m[:, None] & mask_n[None, :]
    tl.store(c_ptrs, c_block, mask=mask)


def csc_spmm_optimized(A_csc, B, M, K, N, block_size_m=32, block_size_n=32, group_size_k=4):
    """
    Optimized version of the CSC SpMM operation using grouped processing.
    """
    indptr, indices, data = A_csc

    # Create output matrix
    C = torch.zeros((M, N), device=B.device, dtype=B.dtype)

    # Set up grid for kernel
    grid = (triton.cdiv(M, block_size_m), triton.cdiv(N, block_size_n))

    # Launch kernel
    csc_spmm_optimized_kernel[grid](
        indptr, indices, data,
        B, C,
        M, N, K,
        BLOCK_SIZE_M=block_size_m,
        BLOCK_SIZE_N=block_size_n,
        GROUP_SIZE_K=group_size_k,
    )

    return C


# Auto-tuning version of the kernel
@triton.autotune(
    configs=[
        triton.Config({'BLOCK_SIZE_M': 16, 'BLOCK_SIZE_N': 16, 'GROUP_SIZE_K': 2}),
        triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 32, 'GROUP_SIZE_K': 4}),
        triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 64, 'GROUP_SIZE_K': 8}),
        triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 64, 'GROUP_SIZE_K': 8}),
        triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 128, 'GROUP_SIZE_K': 8}),
    ],
    key=['M', 'N', 'K'],
)
@triton.jit
def csc_spmm_autotuned_kernel(
    # Pointers to matrices
    a_indptr_ptr, a_indices_ptr, a_data_ptr,  # CSC format
    b_ptr,  # Dense matrix B (row-major)
    c_ptr,  # Output matrix C (row-major)

    # Matrix dimensions
    M, N, K,  # C (M x N) = A (M x K) @ B (K x N)

    # Meta-parameters
    BLOCK_SIZE_M: tl.constexpr,
    BLOCK_SIZE_N: tl.constexpr,
    GROUP_SIZE_K: tl.constexpr,
):
    """
    Auto-tuned kernel for computing C = A @ B where A is in CSC format and B is dense.
    This version automatically selects the best block sizes based on matrix dimensions.
    """
    # Same implementation as csc_spmm_optimized_kernel
    pid_m = tl.program_id(axis=0)
    pid_n = tl.program_id(axis=1)

    block_start_m = pid_m * BLOCK_SIZE_M
    block_start_n = pid_n * BLOCK_SIZE_N

    offs_m = block_start_m + tl.arange(0, BLOCK_SIZE_M)
    offs_n = block_start_n + tl.arange(0, BLOCK_SIZE_N)

    c_block = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)

    mask_m = offs_m < M
    mask_n = offs_n < N

    for k_group in range(0, K, GROUP_SIZE_K):
        k_end = tl.minimum(k_group + GROUP_SIZE_K, K)

        for k in range(k_group, k_end):
            col_start = tl.load(a_indptr_ptr + k)
            col_end = tl.load(a_indptr_ptr + k + 1)

            for idx in range(col_start, col_end):
                row_idx = tl.load(a_indices_ptr + idx)
                val_a = tl.load(a_data_ptr + idx)

                row_in_block = (row_idx >= block_start_m) & (row_idx < block_start_m + BLOCK_SIZE_M)

                if row_in_block:
                    local_row = row_idx - block_start_m

                    b_row_ptr = b_ptr + k * N + offs_n
                    b_row = tl.load(b_row_ptr, mask=mask_n, other=0.0)

                    c_block = tl.where(
                        (tl.arange(0, BLOCK_SIZE_M)[:, None] == local_row) & mask_m[:, None],
                        c_block + val_a * b_row[None, :],
                        c_block
                    )

    c_ptrs = c_ptr + offs_m[:, None] * N + offs_n[None, :]
    mask = mask_m[:, None] & mask_n[None, :]
    tl.store(c_ptrs, c_block, mask=mask)


def csc_spmm_autotuned(A_csc, B, M, K, N):
    """
    Auto-tuned version of the CSC SpMM operation.
    """
    indptr, indices, data = A_csc

    # Create output matrix
    C = torch.zeros((M, N), device=B.device, dtype=B.dtype)

    # Set up grid - will be determined by the selected config
    def grid(meta): return (
        triton.cdiv(M, meta['BLOCK_SIZE_M']),
        triton.cdiv(N, meta['BLOCK_SIZE_N'])
    )

    # Launch kernel with auto-tuning
    csc_spmm_autotuned_kernel[grid](
        indptr, indices, data,
        B, C,
        M, N, K,
    )

    return C