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


import os

os.environ['JAX_TRACEBACK_FILTERING'] = 'off'

import numpy as np
import brainevent
import jax.numpy as jnp

# brainevent.config.gpu_kernel_backend = 'warp'
brainevent.config.gpu_kernel_backend = 'pallas'


def gen_sparse_matrix(shape, prob=0.2):
    """
    Generate a sparse matrix with the given shape and sparsity probability.
    """
    matrix = np.random.rand(*shape)
    matrix = np.where(matrix < prob, matrix, 0.)
    return jnp.asarray(matrix, dtype=float)


k = 1000
shape = (100, 50)
shape = (2000, 3000)
# shape = (300, 200)
matrix = gen_sparse_matrix(shape)
csr = brainevent.CSR.fromdense(matrix)
csc = csr.T

matrix = jnp.asarray(np.random.rand(k, shape[0]))

out1 = matrix @ csr
out2 = (csc @ matrix.T).T
assert jnp.allclose(out1, out2, atol=1e-4, rtol=1e-4)
print('Test passed!')
