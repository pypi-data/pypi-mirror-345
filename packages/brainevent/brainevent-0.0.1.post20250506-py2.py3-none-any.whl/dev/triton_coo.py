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


import time

import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

num_nodes, num_edges = 10_0000, 200_0000
features = 64
edge_index = torch.randint(num_nodes, (2, num_edges), device=device)
# Transpose the tensor to bring the second row to the column dimension
edge_index_transposed = edge_index.t()

# Sort the tensor along the column dimension (formerly the second row)
sorted_edge_index_transposed, _ = edge_index_transposed.sort(dim=0)

# Transpose the tensor back to its original shape
sorted_edge_index = sorted_edge_index_transposed.t()

B = torch.rand(num_nodes, features, device=device).to(torch.float32)
C_atomic = torch.zeros(num_nodes, features, device=device).to(torch.float32)
C_sorted = torch.zeros(num_nodes, features, device=device).to(torch.float32)

group_size = 50

import triton
import triton.language as tl


@triton.jit
def spmm_atomic(edge_index, B, C, num_edges, feature_size: tl.constexpr, XBLOCK: tl.constexpr):
    group_id = tl.program_id(0)
    xoffset = group_id * XBLOCK
    xindex = xoffset + tl.arange(0, XBLOCK)
    x1 = xindex // feature_size
    x2 = xindex % feature_size
    mask = x1 < num_edges
    in_node = tl.load(edge_index + x1, mask)
    out_node = tl.load(edge_index + x1 + num_edges, mask)
    in_val = tl.load(B + in_node * feature_size + x2, mask)
    tl.atomic_add(C + out_node * feature_size + x2, in_val, mask)


@triton.jit
def spmm_sorted_coo_naive(edge_index, B, C, num_edges, feature_size: tl.constexpr, group_size: tl.constexpr):
    group_id = tl.program_id(0)
    node_offset = group_id * group_size
    f_index = tl.arange(0, feature_size)

    xn = node_offset
    mask = xn < num_edges
    in_node = tl.load(edge_index + xn, mask=mask)  # Load the input node
    out_node = tl.load(edge_index + xn + num_edges, mask=mask)  # Load the output node
    curr_node = out_node
    val = tl.load(B + in_node * feature_size + f_index, mask=mask)
    for ii in range(1, group_size):  # Iterate over the group
        xn = ii + node_offset  # Get the node index
        mask = xn < num_edges  # Check if the node index is valid
        in_node = tl.load(edge_index + xn, mask=mask)  # Load the input node
        out_node = tl.load(edge_index + xn + num_edges, mask=mask)  # Load the output node
        new_val = tl.load(B + in_node * feature_size + f_index, mask=mask)
        if out_node != curr_node:
            # Perform atomic addition
            tl.atomic_add(C + curr_node * feature_size + f_index, val, mask=mask)
            # Reset val for the new row
            val = new_val
            curr_node = out_node
        else:
            # Accumulate val
            val += new_val

    tl.atomic_add(C + out_node * feature_size + f_index, val, mask=mask)


grid_atomic = (triton.cdiv(num_edges * features, 128),)
spmm_atomic[grid_atomic](sorted_edge_index, B, C_atomic, num_edges, features, 128)

grid_sorted = (triton.cdiv(num_edges, group_size),)
spmm_sorted_coo_naive[grid_sorted](sorted_edge_index, B, C_sorted, num_edges, features, group_size)

# compare the result
print(torch.allclose(C_atomic, C_sorted))

# test performance
torch.cuda.synchronize()
start = time.time()
for i in range(100):
    spmm_atomic[grid_atomic](sorted_edge_index, B, C_atomic, num_edges, features, 128)
torch.cuda.synchronize()
end = time.time()
print("atomic time: ", end - start)

torch.cuda.synchronize()
start = time.time()
for i in range(100):
    spmm_sorted_coo_naive[grid_sorted](sorted_edge_index, B, C_sorted, num_edges, features, group_size)
torch.cuda.synchronize()
end = time.time()
print("sorted time: ", end - start)

# 创建随机稀疏矩阵
row = torch.randint(num_nodes, (num_edges,), device=device)
col = torch.randint(num_nodes, (num_edges,), device=device)
data = torch.rand(num_edges, device=device)
B = torch.rand(num_nodes, features, device=device).to(torch.float32)

# 创建 PyTorch COO 矩阵
coo = torch.sparse_coo_tensor(indices=torch.stack([row, col]), values=data, size=(num_nodes, num_nodes))

# 评估 PyTorch COO 矩阵乘法性能
C_pytorch = torch.zeros(num_nodes, features, device=device).to(torch.float32)

torch.cuda.synchronize()
start = time.time()
for i in range(100):
    C_pytorch = torch.sparse.mm(coo, B)
torch.cuda.synchronize()
end = time.time()
print("PyTorch COO time: ", end - start)
