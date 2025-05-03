import numpy as np
import warp


def exp1():
    @warp.kernel
    def kernel(
        index: warp.array2d(dtype=int),
        weight: warp.array2d(dtype=float),
        out: warp.array1d(dtype=float),
    ):
        i = warp.tid()

        ind = warp.tile_load(index[i], n_conn)
        w = warp.tile_load(weight[i], n_conn)
        warp.tile_store(out, ind, w)

    n_pre = 1000
    n_post = 1000
    n_conn = 20

    index_ = warp.array(np.random.randint(0, n_post, (n_pre, n_conn)))
    weights_ = warp.array(np.random.randn(n_pre, n_conn), dtype=float)
    out = warp.empty(n_post, dtype=float)

    warp.launch_tiled(kernel, inputs=[index_, weights_], outputs=[out], dim=n_pre, block_dim=32)

    print(out.numpy())


def exp2():
    @warp.kernel
    def kernel(
        index: warp.array2d(dtype=int),
        weight: warp.array2d(dtype=float),
        out: warp.array1d(dtype=float),
    ):
        i, j = warp.tid()

        ind = warp.tile_load(index[i], n_conn)
        w = warp.tile_load(weight[i], n_conn)
        out[ind[j]] += w[j]
        # warp.tile_store(out, ind, w)

    n_pre = 1000
    n_post = 1000
    n_conn = 20

    index_ = warp.array(np.random.randint(0, n_post, (n_pre, n_conn)))
    weights_ = warp.array(np.random.randn(n_pre, n_conn), dtype=float)
    out = warp.empty(n_post, dtype=float)

    warp.launch_tiled(kernel, inputs=[index_, weights_], outputs=[out], dim=n_pre, block_dim=32)

    print(out.numpy())


def exp3():
    @warp.kernel
    def kernel(
        index: warp.array2d(dtype=int),
        weight: warp.array2d(dtype=float),
        out: warp.array1d(dtype=float),
    ):
        i = warp.tid()
        ind = warp.tile_load(index[i], n_conn)
        w = warp.tile_load(weight[i], n_conn)
        ind = warp.untile(ind)
        w = warp.untile(w)
        warp.atomic_add(out, ind, w)

    n_pre = 1000
    n_post = 1000
    n_conn = 40

    index_ = warp.array(np.random.randint(0, n_post, (n_pre, n_conn)))
    weights_ = warp.array(np.random.randn(n_pre, n_conn), dtype=float)
    out = warp.empty(n_post, dtype=float)

    # warp.launch(kernel, inputs=[index_, weights_], outputs=[out], dim=[n_pre, n_conn])
    warp.launch(kernel, inputs=[index_, weights_], outputs=[out], dim=[n_pre], block_dim=32)

    print(out.numpy())


def exp3_2():
    @warp.kernel
    def kernel(
        index: warp.array2d(dtype=int),
        weight: warp.array2d(dtype=float),
        out: warp.array1d(dtype=float),
    ):
        i = warp.tid()
        for j in range(0, n_conn, block_dim):
            ind = warp.tile_load(index[i], block_dim, j)
            w = warp.tile_load(weight[i], block_dim, j)
            ind2 = warp.untile(ind)
            w2 = warp.untile(w)
            warp.atomic_add(out, ind2, w2)

    n_pre = 1000
    n_post = 1000
    n_conn = 40
    block_dim = 32

    index_ = warp.array(np.random.randint(0, n_post, (n_pre, n_conn)), dtype=int)
    weights_ = warp.array(np.random.randn(n_pre, n_conn), dtype=float)
    out = warp.empty(n_post, dtype=float)

    # warp.launch(kernel, inputs=[index_, weights_], outputs=[out], dim=[n_pre, n_conn])
    warp.launch(kernel, inputs=[index_, weights_], outputs=[out], dim=[n_pre], block_dim=block_dim)

    print(out.numpy())


def exp4():
    @warp.kernel
    def kernel(
        index: warp.array2d(dtype=int),
        weight: warp.array2d(dtype=float),
        out: warp.array1d(dtype=float),
    ):
        i, j = warp.tid()
        ind = index[i, j]
        w = weight[i, j]
        warp.atomic_add(out, ind, w)

    n_pre = 1000
    n_post = 1000
    n_conn = 40

    indices_ = warp.array(np.random.randint(0, n_post, (n_pre, n_conn)), dtype=int)
    weights_ = warp.array(np.random.randn(n_pre, n_conn), dtype=float)
    out = warp.empty(n_post, dtype=float)

    # warp.launch(kernel, inputs=[indices_, weights_], outputs=[out], dim=[n_pre, n_conn])
    warp.launch(kernel, inputs=[indices_, weights_], outputs=[out], dim=[n_pre], block_dim=32)

    print(out.numpy())


if __name__ == '__main__':
    # exp3()
    exp3_2()
    # exp4()
