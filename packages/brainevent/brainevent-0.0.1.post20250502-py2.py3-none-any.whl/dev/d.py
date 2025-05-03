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

import warp as wp
import numpy as np

# -*- coding: utf-8 -*-
TILE_SIZE = wp.constant(256)
TILE_THREADS = 64

@wp.kernel
def compute(a: wp.array2d(dtype=float), b: wp.array2d(dtype=float)):

    # obtain our block index
    i = wp.tid()

    # load a row from global memory
    t = wp.tile_load(a[i], 0, TILE_SIZE)

    # cooperatively compute the sum of the tile elements; s is a 1x1 tile
    s = wp.tile_sum(t)

    # store s in global memory
    wp.tile_store(b[0], i, s)

N = 10

a_np = np.arange(N).reshape(-1, 1) * np.ones((1, 256), dtype=float)
a = wp.array(a_np, dtype=float)
b = wp.zeros((1,N), dtype=float)

wp.launch_tiled(compute, dim=[a.shape[0]], inputs=[a, b], block_dim=TILE_THREADS)

print(f"b = {b}")

