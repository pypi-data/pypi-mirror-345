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

import os

os.environ['JAX_TRACEBACK_FILTERING'] = 'off'

import jax
import brainstate as bst

from brainevent._csr_test_util import get_csr, vector_csr, csr_vector

import brainevent

transpose = False
transpose = True
replace = True
homo_w = True

n_in = 20
n_out = 30
shape = [n_in, n_out]
x = bst.random.rand(n_in) if transpose else bst.random.rand(n_out)

indptr, indices = get_csr(n_in, n_out, 0.2, replace=replace)
w = 1.5 if homo_w else bst.init.Normal()(indices.shape)
csr = brainevent.CSR((w, indices, indptr), shape=shape)


def f_brainevent(x, w):
    if transpose:
        r = brainevent.EventArray(x) @ csr.with_data(w)
    else:
        r = csr.with_data(w) @ brainevent.EventArray(x)
    return r.sum()


r = jax.grad(f_brainevent, argnums=(0, 1))(x, w)


def f_brainevent2(x, w):
    if transpose:
        r = x @ csr.with_data(w)
    else:
        r = csr.with_data(w) @ x
    return r.sum()


r1 = jax.grad(f_brainevent2, argnums=(0, 1))(x, w)


# -------------------
# TRUE gradients

def f_jax(x, w):
    if transpose:
        r = vector_csr(x, w, indices, indptr, shape=shape)
    else:
        r = csr_vector(x, w, indices, indptr, shape=shape)
    return r.sum()


r2 = jax.grad(f_jax, argnums=(0, 1))(x, w)
# self.assertTrue(jnp.allclose(r[0], r2[0], rtol=1e-3, atol=1e-3))
# self.assertTrue(jnp.allclose(r[1], r2[1], rtol=1e-3, atol=1e-3))
print(r)
print(r1)
print(r2)
