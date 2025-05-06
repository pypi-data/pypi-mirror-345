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
def csr_spmm_kernel(
    # Pointers to matrices
    a_indptr_ptr, a_indices_ptr, a_data_ptr,  # CSR format: indptr, indices, data
    b_ptr,  # Dense matrix B (row-major)
    c_ptr,  # Output matrix C (row-major)

    # Matrix dimensions
    M, N, K,  # C (M x N) = A (M x K) @ B (K x N)

    # Meta-parameters
    BLOCK_SIZE_M: tl.constexpr,
    BLOCK_SIZE_N: tl.constexpr,
):
    """
    Kernel for computing C = A @ B where A is in CSR format and B is a dense matrix.

    CSR format for A:
    - a_indptr_ptr: row pointers (size M+1)
    - a_indices_ptr: column indices (size nnz)
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

    # Loop over rows in this block
    for m_idx in range(BLOCK_SIZE_M):
        m = block_start_m + m_idx
        if m >= M:
            break

        # Load row pointers for current and next row
        row_start = tl.load(a_indptr_ptr + m)
        row_end = tl.load(a_indptr_ptr + m + 1)

        # Process all non-zeros in this row
        for idx in range(row_start, row_end):
            # Load column index and value
            col_idx = tl.load(a_indices_ptr + idx)
            val_a = tl.load(a_data_ptr + idx)

            # Load the corresponding row from B
            b_row_ptr = b_ptr + col_idx * N + offs_n
            b_row = tl.load(b_row_ptr, mask=mask_n, other=0.0)

            # Update the corresponding row of our block in C
            c_block = tl.where(
                (tl.arange(0, BLOCK_SIZE_M)[:, None] == m_idx) & mask_m[:, None],
                c_block + val_a * b_row[None, :],
                c_block
            )

    # Write results back to C
    c_ptrs = c_ptr + offs_m[:, None] * N + offs_n[None, :]
    mask = mask_m[:, None] & mask_n[None, :]
    tl.store(c_ptrs, c_block, mask=mask)


def csr_spmm(A_csr, B, M, K, N, block_size_m=32, block_size_n=32):
    """
    Computes C = A @ B where A is a sparse matrix in CSR format and B is a dense matrix.

    Args:
        A_csr: Tuple of (indptr, indices, data) representing matrix A in CSR format
        B: Dense tensor of shape (K, N)
        M: Number of rows in A
        K: Number of columns in A / Number of rows in B
        N: Number of columns in B
        block_size_m: Block size for M dimension
        block_size_n: Block size for N dimension

    Returns:
        C: Dense tensor of shape (M, N) resulting from A @ B
    """
    indptr, indices, data = A_csr

    # Create output matrix
    C = torch.zeros((M, N), device=B.device, dtype=B.dtype)

    # Set up grid for kernel
    grid = (triton.cdiv(M, block_size_m), triton.cdiv(N, block_size_n))

    # Launch kernel
    csr_spmm_kernel[grid](
        indptr, indices, data,
        B, C,
        M, N, K,
        BLOCK_SIZE_M=block_size_m,
        BLOCK_SIZE_N=block_size_n,
    )

    return C


# Helper function to convert scipy CSR matrix to PyTorch tensors
def scipy_csr_to_torch(csr_matrix, device='cuda'):
    indptr = torch.from_numpy(csr_matrix.indptr.astype('int32')).to(device)
    indices = torch.from_numpy(csr_matrix.indices.astype('int32')).to(device)
    data = torch.from_numpy(csr_matrix.data.astype('float32')).to(device)
    return indptr, indices, data


# Optimized CSR kernel with better memory access patterns
@triton.jit
def csr_spmm_optimized_kernel(
    # Pointers to matrices
    a_indptr_ptr, a_indices_ptr, a_data_ptr,  # CSR format
    b_ptr,  # Dense matrix B (row-major)
    c_ptr,  # Output matrix C (row-major)

    # Matrix dimensions
    M, N, K,  # C (M x N) = A (M x K) @ B (K x N)

    # Meta-parameters
    BLOCK_SIZE_M: tl.constexpr,
    BLOCK_SIZE_N: tl.constexpr,
    BLOCK_SIZE_K: tl.constexpr,  # Number of non-zeros to process at once
):
    """
    Optimized kernel for computing C = A @ B where A is in CSR format and B is dense.
    This version uses memory access optimizations and block processing.
    """
    # Program ID
    pid_m = tl.program_id(axis=0)
    pid_n = tl.program_id(axis=1)

    # Compute the block's starting position
    block_start_m = pid_m * BLOCK_SIZE_M
    block_start_n = pid_n * BLOCK_SIZE_N

    # Generate offset ranges
    offs_m = block_start_m + tl.arange(0, BLOCK_SIZE_M)
    offs_n = block_start_n + tl.arange(0, BLOCK_SIZE_N)

    # Initialize output block
    c_block = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)

    # Create masks
    mask_m = offs_m < M
    mask_n = offs_n < N

    # Process each row in this block
    for m_idx in range(BLOCK_SIZE_M):
        m = block_start_m + m_idx
        if m >= M:
            break

        # Load row pointers
        row_start = tl.load(a_indptr_ptr + m)
        row_end = tl.load(a_indptr_ptr + m + 1)

        # Process non-zeros in blocks for better memory efficiency
        for idx_block_start in range(row_start, row_end, BLOCK_SIZE_K):
            idx_block_end = tl.minimum(idx_block_start + BLOCK_SIZE_K, row_end)

            # Process each non-zero in this block
            for idx in range(idx_block_start, idx_block_end):
                col_idx = tl.load(a_indices_ptr + idx)
                val_a = tl.load(a_data_ptr + idx)

                # Load row from B
                b_row_ptr = b_ptr + col_idx * N + offs_n
                b_row = tl.load(b_row_ptr, mask=mask_n, other=0.0)

                # Update output
                c_block = tl.where(
                    (tl.arange(0, BLOCK_SIZE_M)[:, None] == m_idx) & mask_m[:, None],
                    c_block + val_a * b_row[None, :],
                    c_block
                )

    # Write results
    c_ptrs = c_ptr + offs_m[:, None] * N + offs_n[None, :]
    mask = mask_m[:, None] & mask_n[None, :]
    tl.store(c_ptrs, c_block, mask=mask)


def csr_spmm_optimized(A_csr, B, M, K, N, block_size_m=32, block_size_n=32, block_size_k=16):
    """
    Optimized version of CSR SpMM.
    """
    indptr, indices, data = A_csr

    # Create output matrix
    C = torch.zeros((M, N), device=B.device, dtype=B.dtype)

    # Set up grid
    grid = (triton.cdiv(M, block_size_m), triton.cdiv(N, block_size_n))

    # Launch kernel
    csr_spmm_optimized_kernel[grid](
        indptr, indices, data,
        B, C,
        M, N, K,
        BLOCK_SIZE_M=block_size_m,
        BLOCK_SIZE_N=block_size_n,
        BLOCK_SIZE_K=block_size_k,
    )

    return C


# Auto-tuned kernel
@triton.autotune(
    configs=[
        triton.Config({'BLOCK_SIZE_M': 16, 'BLOCK_SIZE_N': 16, 'BLOCK_SIZE_K': 8}),
        triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 16}),
        triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 16}),
        triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32}),
        triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 128, 'BLOCK_SIZE_K': 32}),
    ],
    key=['M', 'N', 'K'],
)
@triton.jit
def csr_spmm_autotuned_kernel(
    # Pointers to matrices
    a_indptr_ptr, a_indices_ptr, a_data_ptr,  # CSR format
    b_ptr,  # Dense matrix B
    c_ptr,  # Output matrix C

    # Matrix dimensions
    M, N, K,  # C (M x N) = A (M x K) @ B (K x N)
    nnz,  # Number of non-zeros in A

    # Meta-parameters
    BLOCK_SIZE_M: tl.constexpr,
    BLOCK_SIZE_N: tl.constexpr,
    BLOCK_SIZE_K: tl.constexpr,
):
    """
    Auto-tuned kernel for CSR SpMM.
    """
    # Same implementation as optimized kernel
    pid_m = tl.program_id(axis=0)
    pid_n = tl.program_id(axis=1)

    block_start_m = pid_m * BLOCK_SIZE_M
    block_start_n = pid_n * BLOCK_SIZE_N

    offs_m = block_start_m + tl.arange(0, BLOCK_SIZE_M)
    offs_n = block_start_n + tl.arange(0, BLOCK_SIZE_N)

    c_block = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)

    mask_m = offs_m < M
    mask_n = offs_n < N

    for m_idx in range(BLOCK_SIZE_M):
        m = block_start_m + m_idx
        if m >= M:
            break

        row_start = tl.load(a_indptr_ptr + m)
        row_end = tl.load(a_indptr_ptr + m + 1)

        for idx_block_start in range(row_start, row_end, BLOCK_SIZE_K):
            idx_block_end = tl.minimum(idx_block_start + BLOCK_SIZE_K, row_end)

            for idx in range(idx_block_start, idx_block_end):
                col_idx = tl.load(a_indices_ptr + idx)
                val_a = tl.load(a_data_ptr + idx)

                b_row_ptr = b_ptr + col_idx * N + offs_n
                b_row = tl.load(b_row_ptr, mask=mask_n, other=0.0)

                c_block = tl.where(
                    (tl.arange(0, BLOCK_SIZE_M)[:, None] == m_idx) & mask_m[:, None],
                    c_block + val_a * b_row[None, :],
                    c_block
                )

    c_ptrs = c_ptr + offs_m[:, None] * N + offs_n[None, :]
    mask = mask_m[:, None] & mask_n[None, :]
    tl.store(c_ptrs, c_block, mask=mask)


def csr_spmm_autotuned(A_csr, B, M, K, N, nnz):
    """
    Auto-tuned version of CSR SpMM.
    """
    indptr, indices, data = A_csr

    # Create output matrix
    C = torch.zeros((M, N), device=B.device, dtype=B.dtype)

    # Set up grid
    def grid(meta): return (
        triton.cdiv(M, meta['BLOCK_SIZE_M']),
        triton.cdiv(N, meta['BLOCK_SIZE_N'])
    )

    # Launch kernel
    csr_spmm_autotuned_kernel[grid](
        indptr, indices, data,
        B, C,
        M, N, K, nnz,
    )

    return C


# Example usage
if __name__ == "__main__":
    import numpy as np
    import scipy.sparse as sp
    import time

    # Create a sparse matrix A in CSR format
    M, K = 1024, 1024
    density = 0.01  # 1% of elements are non-zero

    # Create a random sparse matrix in CSR format
    A_scipy = sp.random(M, K, density=density, format='csr', dtype=np.float32)
    nnz = A_scipy.nnz

    # Create a random dense matrix B
    N = 1024
    B_np = np.random.rand(K, N).astype(np.float32)

    # Convert to PyTorch tensors
    A_torch = scipy_csr_to_torch(A_scipy)
    B_torch = torch.from_numpy(B_np).cuda()

    # Expected result using SciPy
    start_time = time.time()
    expected = A_scipy @ B_np
    scipy_time = time.time() - start_time
    print(f"SciPy time: {scipy_time:.6f} seconds")

    # Result using our Triton kernel
    start_time = time.time()
    result = csr_spmm(A_torch, B_torch, M, K, N)
    triton_time = time.time() - start_time
    print(f"Triton time: {triton_time:.6f} seconds")
    result_cpu = result.cpu().numpy()

    # Verify results
    max_diff = np.max(np.abs(result_cpu - expected))
    print(f"Maximum difference: {max_diff}")
    print(f"Speedup: {scipy_time / triton_time:.2f}x")

    # Benchmark optimized kernel
    start_time = time.time()
    result_opt = csr_spmm_optimized(A_torch, B_torch, M, K, N)
    opt_time = time.time() - start_time
    print(f"Optimized Triton time: {opt_time:.6f} seconds")
    print(f"Speedup vs basic: {triton_time / opt_time:.2f}x")

    # Benchmark with auto-tuning
    start_time = time.time()
    result_auto = csr_spmm_autotuned(A_torch, B_torch, M, K, N, nnz)
    auto_time = time.time() - start_time
    print(f"Auto-tuned Triton time: {auto_time:.6f} seconds")
    print(f"Speedup vs basic: {triton_time / auto_time:.2f}x")
