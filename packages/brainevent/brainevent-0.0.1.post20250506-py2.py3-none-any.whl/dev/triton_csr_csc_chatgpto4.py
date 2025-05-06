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


import triton
import triton.language as tl

# -------------------- CSC KERNEL (for reference) --------------------
# Kernel: compute C = A_csc @ B, where A is in CSC format
@triton.jit
def sparse_csc_dense_kernel(
    data_ptr, indices_ptr, indptr_ptr, B_ptr, C_ptr,
    nnz, n_cols_A, n_rows_A, N,
    BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr
):
    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)
    row_start = pid_m * BLOCK_SIZE_M
    col_start = pid_n * BLOCK_SIZE_N
    acc = tl.zeros([BLOCK_SIZE_M, BLOCK_SIZE_N], dtype=tl.float32)

    # iterate columns of A
    for k in range(n_cols_A):
        start = tl.load(indptr_ptr + k)
        end = tl.load(indptr_ptr + k + 1)
        for idx in range(start, end):
            i = tl.load(indices_ptr + idx)
            a_val = tl.load(data_ptr + idx)
            # broadcast B row
            b = tl.load(B_ptr + k * N + col_start + tl.arange(0, BLOCK_SIZE_N),
                         mask=col_start + tl.arange(0, BLOCK_SIZE_N) < N, other=0.0)
            if (i >= row_start) & (i < row_start + BLOCK_SIZE_M):
                acc[i - row_start, :] += a_val * b

    # write back
    rows = row_start + tl.arange(0, BLOCK_SIZE_M)
    cols = col_start + tl.arange(0, BLOCK_SIZE_N)
    mask = (rows[:, None] < n_rows_A) & (cols[None, :] < N)
    offs = rows[:, None] * N + cols[None, :]
    tl.store(C_ptr + offs, acc, mask=mask)


def sparse_csc_dense(A_csc, B, BLOCK_SIZE_M=64, BLOCK_SIZE_N=64):
    import torch
    data, indices, indptr = A_csc.data, A_csc.indices, A_csc.indptr
    n_rows, n_cols = A_csc.shape
    _, N = B.shape
    C = torch.zeros((n_rows, N), dtype=B.dtype, device=B.device)
    grid = ((n_rows + BLOCK_SIZE_M - 1) // BLOCK_SIZE_M,
            (N + BLOCK_SIZE_N - 1) // BLOCK_SIZE_N)
    sparse_csc_dense_kernel[grid](
        data, indices, indptr, B, C,
        data.numel(), n_cols, n_rows, N,
        BLOCK_SIZE_M=BLOCK_SIZE_M, BLOCK_SIZE_N=BLOCK_SIZE_N
    )
    return C


# -------------------- CSR KERNEL & WRAPPER --------------------
# Kernel: compute C = A_csr @ B, where A is in CSR format
@triton.jit
def sparse_csr_dense_kernel(
    data_ptr, indices_ptr, indptr_ptr, B_ptr, C_ptr,
    nnz, n_rows_A, n_cols_A, N,
    BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr
):
    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)
    row_start = pid_m * BLOCK_SIZE_M
    col_start = pid_n * BLOCK_SIZE_N
    acc = tl.zeros([BLOCK_SIZE_M, BLOCK_SIZE_N], dtype=tl.float32)

    # iterate rows of A
    for i in range(row_start, row_start + BLOCK_SIZE_M):
        if i >= n_rows_A:
            break
        # row range in data
        row_begin = tl.load(indptr_ptr + i)
        row_end = tl.load(indptr_ptr + i + 1)
        # for each non-zero in row i
        for idx in range(row_begin, row_end):
            j = tl.load(indices_ptr + idx)  # column index
            a_val = tl.load(data_ptr + idx)
            # load B row j
            b = tl.load(B_ptr + j * N + col_start + tl.arange(0, BLOCK_SIZE_N),
                         mask=col_start + tl.arange(0, BLOCK_SIZE_N) < N, other=0.0)
            acc[i - row_start, :] += a_val * b

    # write back
    rows = row_start + tl.arange(0, BLOCK_SIZE_M)
    cols = col_start + tl.arange(0, BLOCK_SIZE_N)
    mask = (rows[:, None] < n_rows_A) & (cols[None, :] < N)
    offs = rows[:, None] * N + cols[None, :]
    tl.store(C_ptr + offs, acc, mask=mask)


def sparse_csr_dense(A_csr, B, BLOCK_SIZE_M=64, BLOCK_SIZE_N=64):
    """
    Compute C = A_csr @ B using Triton.
    A_csr: object with .data, .indices, .indptr (all torch tensors on GPU)
    B: torch.Tensor of shape (n_cols_A, N)
    returns: torch.Tensor C of shape (n_rows_A, N)
    """
    import torch
    data, indices, indptr = A_csr.data, A_csr.indices, A_csr.indptr
    n_rows, n_cols = A_csr.shape
    _, N = B.shape
    C = torch.zeros((n_rows, N), dtype=B.dtype, device=B.device)
    grid = ((n_rows + BLOCK_SIZE_M - 1) // BLOCK_SIZE_M,
            (N + BLOCK_SIZE_N - 1) // BLOCK_SIZE_N)
    sparse_csr_dense_kernel[grid](
        data, indices, indptr, B, C,
        data.numel(), n_rows, n_cols, N,
        BLOCK_SIZE_M=BLOCK_SIZE_M, BLOCK_SIZE_N=BLOCK_SIZE_N
    )
    return C

# Example usage for CSR:
if __name__ == '__main__':
    import torch
    from scipy.sparse import random as sparse_random

    A = sparse_random(1024, 512, density=0.01, format='csr', dtype=float)
    B = torch.randn(512, 256, device='cuda', dtype=torch.float32)
    A = A.tocsr()
    data = torch.tensor(A.data, device='cuda', dtype=torch.float32)
    indices = torch.tensor(A.indices, device='cuda', dtype=torch.int32)
    indptr = torch.tensor(A.indptr, device='cuda', dtype=torch.int32)
    A_csr = type('C', (), {'data': data, 'indices': indices, 'indptr': indptr, 'shape': A.shape})
    C = sparse_csr_dense(A_csr, B)
    print(C.shape)  # (1024, 256)

