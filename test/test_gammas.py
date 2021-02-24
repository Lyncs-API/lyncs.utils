from lyncs_utils import gamma_matrices
import numpy as np


def test_gammas_minkowsky():

    for dim in range(1, 10):
        g = np.array(gamma_matrices(dim, euclidean=False))

        assert len(g) == dim + 1
        prod = np.identity(2 ** ((dim + 1) // 2))
        for d in range(dim):
            prod = prod.dot(g[d])
            assert g[d].trace() == 0
            assert (
                g[d].dot(g[d])
                == (1 if d == 0 else -1) * np.identity(2 ** ((dim + 1) // 2))
            ).all()
            assert (g[d].transpose().conj() == (1 if d == 0 else -1) * g[d]).all()
            assert (g[-1].dot(g[d]) == -g[d].dot(g[-1])).all()

        if dim % 2 == 0:
            assert ((1j) ** (dim // 2 - 1) * prod == g[-1]).all()


def test_gammas_euclidean():

    for dim in range(1, 10):
        g = np.array(gamma_matrices(dim, euclidean=True))

        assert len(g) == dim + 1
        prod = np.identity(g[0].shape[0])
        for d in range(dim):
            prod = prod.dot(g[d])
            assert g[d].trace() == 0
            assert (g[d].dot(g[d]) == np.identity(2 ** ((dim + 1) // 2))).all()
            assert (g[d].transpose().conj() == g[d]).all()
            assert (g[-1].dot(g[d]) == -g[d].dot(g[-1])).all()

            for d2 in range(d):
                assert (g[d].dot(g[d2]) == -g[d2].dot(g[d])).all()

        if dim % 2 == 0:
            assert ((1j) ** ((3 * dim) // 2 - 2) * prod == g[-1]).all()
