import pytest
from lyncs_utils.numpy import *

skip = pytest.mark.skipif(isinstance(numpy, Exception), reason="Numpy not available")


@skip
def test_gammas_minkowsky():

    for dim in range(1, 10):
        g = numpy.array(gamma_matrices(dim, euclidean=False))

        assert len(g) == dim + 1
        prod = numpy.identity(2 ** ((dim + 1) // 2))
        for d in range(dim):
            prod = prod.dot(g[d])
            assert g[d].trace() == 0
            assert (
                g[d].dot(g[d])
                == (1 if d == 0 else -1) * numpy.identity(2 ** ((dim + 1) // 2))
            ).all()
            assert (g[d].transpose().conj() == (1 if d == 0 else -1) * g[d]).all()
            assert (g[-1].dot(g[d]) == -g[d].dot(g[-1])).all()

        if dim % 2 == 0:
            assert ((1j) ** (dim // 2 - 1) * prod == g[-1]).all()


@skip
def test_gammas_euclidean():

    for dim in range(1, 10):
        g = numpy.array(gamma_matrices(dim, euclidean=True))

        assert len(g) == dim + 1
        prod = numpy.identity(g[0].shape[0])
        for d in range(dim):
            prod = prod.dot(g[d])
            assert g[d].trace() == 0
            assert (g[d].dot(g[d]) == numpy.identity(2 ** ((dim + 1) // 2))).all()
            assert (g[d].transpose().conj() == g[d]).all()
            assert (g[-1].dot(g[d]) == -g[d].dot(g[-1])).all()

            for d2 in range(d):
                assert (g[d].dot(g[d2]) == -g[d2].dot(g[d])).all()

        if dim % 2 == 0:
            assert ((1j) ** ((3 * dim) // 2 - 2) * prod == g[-1]).all()
