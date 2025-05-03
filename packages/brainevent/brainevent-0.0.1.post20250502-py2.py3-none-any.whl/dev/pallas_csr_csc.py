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
import jax
import jax.numpy as jnp
from jax import lax
from jax.experimental import pallas as pl
from jax.experimental.pallas import tpu as pltpu
from jax.experimental.pallas import gpu as plgpu
import numpy as np


# Helper function to determine if we're using GPU or TPU
def get_pallas_implementation():
    """Return the appropriate Pallas implementation based on available hardware."""
    if jax.devices()[0].platform == 'gpu':
        return plgpu
    elif jax.devices()[0].platform == 'tpu':
        return pltpu
    else:
        raise RuntimeError("Pallas requires GPU or TPU hardware")


######################################
# CSC Sparse Matrix Multiplication   #
######################################

def csc_spmm_pallas_kernel(indptr, indices, data, B, C, M, N, K,
                           BLOCK_SIZE_M=32, BLOCK_SIZE_N=32):
    """
    JAX Pallas kernel for CSC SpMM (C = A @ B).

    Args:
        indptr: Column pointers for sparse matrix A
        indices: Row indices for sparse matrix A
        data: Values for sparse matrix A
        B: Dense matrix B
        C: Output matrix C (will be written to)
        M, N, K: Matrix dimensions
        BLOCK_SIZE_M, BLOCK_SIZE_N: Block sizes for tiling
    """
    # Get the appropriate Pallas implementation
    pl_impl = get_pallas_implementation()

    # Define the grid dimensions
    grid_m = (M + BLOCK_SIZE_M - 1) // BLOCK_SIZE_M
    grid_n = (N + BLOCK_SIZE_N - 1) // BLOCK_SIZE_N

    @pl_impl.kernel
    def kernel(indptr_ref, indices_ref, data_ref, B_ref, C_ref):
        # Get program ID
        pid_m = pl.program_id(0)
        pid_n = pl.program_id(1)

        # Compute the block's starting position
        block_start_m = pid_m * BLOCK_SIZE_M
        block_start_n = pid_n * BLOCK_SIZE_N

        # Create ranges for m and n dimensions
        range_m = block_start_m + pl.arange(BLOCK_SIZE_M)
        range_n = block_start_n + pl.arange(BLOCK_SIZE_N)

        # Initialize output block
        C_block = pl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=jnp.float32)

        # Loop over columns of A / rows of B
        for k in range(K):
            # Load column pointers
            col_start = indptr_ref[k]
            col_end = indptr_ref[k + 1]

            # Process all non-zeros in this column
            for idx in range(col_start, col_end):
                # Load row index and value
                row_idx = indices_ref[idx]
                val_a = data_ref[idx]

                # Check if this row is within our block
                if (row_idx >= block_start_m) and (row_idx < block_start_m + BLOCK_SIZE_M):
                    # Local row index within our block
                    local_row = row_idx - block_start_m

                    # Load the corresponding row from B
                    b_row = pl.load(B_ref, (k, range_n),
                                    bounds_check=((0, K), (0, N)))

                    # Update the output block
                    for i in range(BLOCK_SIZE_M):
                        for j in range(BLOCK_SIZE_N):
                            if i == local_row and range_m[i] < M and range_n[j] < N:
                                C_block = C_block.at[i, j].add(val_a * b_row[j])

        # Write the result back to C
        for i in range(BLOCK_SIZE_M):
            for j in range(BLOCK_SIZE_N):
                if range_m[i] < M and range_n[j] < N:
                    C_ref = C_ref.at[range_m[i], range_n[j]].add(C_block[i, j])

    # Launch the kernel
    kernel_grid = (grid_m, grid_n)
    pl_impl.launch(kernel, kernel_grid, in_specs=[
        pl_impl.BlockSpec(lambda i, _: indptr.shape, lambda i, _: indptr.dtype),
        pl_impl.BlockSpec(lambda i, _: indices.shape, lambda i, _: indices.dtype),
        pl_impl.BlockSpec(lambda i, _: data.shape, lambda i, _: data.dtype),
        pl_impl.BlockSpec(lambda i, _: B.shape, lambda i, _: B.dtype),
        pl_impl.BlockSpec(lambda i, _: C.shape, lambda i, _: C.dtype),
    ], out_specs=[],
                   # Pass the inputs
                   args=[indptr, indices, data, B, C],
                   # No outputs (we write directly to C)
                   out=[])


def csc_spmm_pallas(A_csc, B, M, K, N, block_size_m=32, block_size_n=32):
    """
    JAX function for CSC SpMM.

    Args:
        A_csc: Tuple of (indptr, indices, data) representing matrix A in CSC format
        B: Dense matrix B of shape (K, N)
        M, N, K: Matrix dimensions
        block_size_m, block_size_n: Block sizes for tiling

    Returns:
        C: Dense result matrix C of shape (M, N)
    """
    indptr, indices, data = A_csc

    # Create output matrix
    C = jnp.zeros((M, N), dtype=B.dtype)

    # Call the kernel
    csc_spmm_pallas_kernel(indptr, indices, data, B, C, M, N, K,
                           BLOCK_SIZE_M=block_size_m, BLOCK_SIZE_N=block_size_n)

    return C


######################################
# CSR Sparse Matrix Multiplication   #
######################################

def csr_spmm_pallas_kernel(indptr, indices, data, B, C, M, N, K,
                           BLOCK_SIZE_M=32, BLOCK_SIZE_N=32):
    """
    JAX Pallas kernel for CSR SpMM (C = A @ B).

    Args:
        indptr: Row pointers for sparse matrix A
        indices: Column indices for sparse matrix A
        data: Values for sparse matrix A
        B: Dense matrix B
        C: Output matrix C (will be written to)
        M, N, K: Matrix dimensions
        BLOCK_SIZE_M, BLOCK_SIZE_N: Block sizes for tiling
    """
    # Get the appropriate Pallas implementation
    pl_impl = get_pallas_implementation()

    # Define the grid dimensions
    grid_m = (M + BLOCK_SIZE_M - 1) // BLOCK_SIZE_M
    grid_n = (N + BLOCK_SIZE_N - 1) // BLOCK_SIZE_N

    @pl_impl.kernel
    def kernel(indptr_ref, indices_ref, data_ref, B_ref, C_ref):
        # Get program ID
        pid_m = pl.program_id(0)
        pid_n = pl.program_id(1)

        # Compute the block's starting position
        block_start_m = pid_m * BLOCK_SIZE_M
        block_start_n = pid_n * BLOCK_SIZE_N

        # Create ranges for m and n dimensions
        range_m = block_start_m + pl.arange(BLOCK_SIZE_M)
        range_n = block_start_n + pl.arange(BLOCK_SIZE_N)

        # Initialize output block
        C_block = pl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=jnp.float32)

        # Process rows in this block
        for m_idx in range(BLOCK_SIZE_M):
            m = block_start_m + m_idx
            if m >= M:
                break

            # Load row pointers
            row_start = indptr_ref[m]
            row_end = indptr_ref[m + 1]

            # Process all non-zeros in this row
            for idx in range(row_start, row_end):
                # Load column index and value
                col_idx = indices_ref[idx]
                val_a = data_ref[idx]

                # Load corresponding row from B
                b_row = pl.load(B_ref, (col_idx, range_n),
                                bounds_check=((0, K), (0, N)))

                # Update the output block
                for j in range(BLOCK_SIZE_N):
                    if range_n[j] < N:
                        C_block = C_block.at[m_idx, j].add(val_a * b_row[j])

        # Write the result back to C
        for i in range(BLOCK_SIZE_M):
            for j in range(BLOCK_SIZE_N):
                if range_m[i] < M and range_n[j] < N:
                    C_ref = C_ref.at[range_m[i], range_n[j]].add(C_block[i, j])

    # Launch the kernel
    kernel_grid = (grid_m, grid_n)
    pl_impl.launch(kernel, kernel_grid, in_specs=[
        pl_impl.BlockSpec(lambda i, _: indptr.shape, lambda i, _: indptr.dtype),
        pl_impl.BlockSpec(lambda i, _: indices.shape, lambda i, _: indices.dtype),
        pl_impl.BlockSpec(lambda i, _: data.shape, lambda i, _: data.dtype),
        pl_impl.BlockSpec(lambda i, _: B.shape, lambda i, _: B.dtype),
        pl_impl.BlockSpec(lambda i, _: C.shape, lambda i, _: C.dtype),
    ], out_specs=[],
                   # Pass the inputs
                   args=[indptr, indices, data, B, C],
                   # No outputs (we write directly to C)
                   out=[])


def csr_spmm_pallas(A_csr, B, M, K, N, block_size_m=32, block_size_n=32):
    """
    JAX function for CSR SpMM.

    Args:
        A_csr: Tuple of (indptr, indices, data) representing matrix A in CSR format
        B: Dense matrix B of shape (K, N)
        M, N, K: Matrix dimensions
        block_size_m, block_size_n: Block sizes for tiling

    Returns:
        C: Dense result matrix C of shape (M, N)
    """
    indptr, indices, data = A_csr

    # Create output matrix
    C = jnp.zeros((M, N), dtype=B.dtype)

    # Call the kernel
    csr_spmm_pallas_kernel(indptr, indices, data, B, C, M, N, K,
                           BLOCK_SIZE_M=block_size_m, BLOCK_SIZE_N=block_size_n)

    return C


######################################
# Optimized JAX Pallas Kernels       #
######################################

def csr_spmm_optimized_pallas_kernel(indptr, indices, data, B, C, M, N, K,
                                     BLOCK_SIZE_M=32, BLOCK_SIZE_N=32, BLOCK_SIZE_K=16):
    """
    Optimized JAX Pallas kernel for CSR SpMM (C = A @ B).

    This version processes non-zeros in blocks for better memory access patterns.
    """
    # Get the appropriate Pallas implementation
    pl_impl = get_pallas_implementation()

    # Define the grid dimensions
    grid_m = (M + BLOCK_SIZE_M - 1) // BLOCK_SIZE_M
    grid_n = (N + BLOCK_SIZE_N - 1) // BLOCK_SIZE_N

    @pl_impl.kernel
    def kernel(indptr_ref, indices_ref, data_ref, B_ref, C_ref):
        # Get program ID
        pid_m = pl.program_id(0)
        pid_n = pl.program_id(1)

        # Compute the block's starting position