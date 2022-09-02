"""
Gamma matrices
"""

__all__ = [
    "numpy",
    "outer",
    "gamma_matrices",
    "su_generators",
    "requires_numpy",
]

from .extensions import lazy_import, raiseif

try:
    numpy = lazy_import("numpy")
except ImportError as err:
    numpy = err

requires_numpy = raiseif(isinstance(numpy, Exception), numpy)


@requires_numpy
def outer(left, right):
    "Outer product between two arrays"
    return numpy.kron(left, right)


@requires_numpy
def gamma_matrices(dim=4, euclidean=True):
    "Based on https://en.wikipedia.org/wiki/Higher-dimensional_gamma_matrices"

    assert dim > 0 and isinstance(dim, int)

    sigmas = (
        numpy.array(((0, 1), (1, 0))),
        numpy.array(((0, -1j), (1j, 0))),
        numpy.array(((1, 0), (0, -1))),
    )

    chiral = sigmas[2]
    gammas = [sigmas[0], (-1 if euclidean else -1j) * sigmas[1]]

    for idx in range((dim + 1) // 2 - 1):
        new = []
        for gamma in gammas:
            new.append(outer(gamma, sigmas[-1]))
        new.append(
            outer(numpy.identity(2 ** (idx + 1)), (1 if euclidean else 1j) * sigmas[0])
        )
        new.append(
            outer(numpy.identity(2 ** (idx + 1)), (1 if euclidean else 1j) * sigmas[1])
        )
        gammas = new
        chiral = outer(chiral, sigmas[2])

    if dim % 2:
        if euclidean:
            gammas[-1] *= 1j
        return tuple(gammas)

    gammas.append(chiral)

    return tuple(gammas)


@requires_numpy
def su_generators(ncol=3):
    "Returns generators of the su(ncol) Lie algebra"

    def norm(mat):
        return 1 / (-2 * mat.dot(mat).trace().real) ** 0.5

    # Off-diagonal: anti-hermitian
    for i in range(ncol - 1):
        for j in range(i + 1, ncol):
            for data in (1, -1), (1j, 1j):
                mat = numpy.zeros((ncol, ncol), dtype=complex)
                mat[i, j], mat[j, i] = data
                yield mat * norm(mat)

    # Diagonal: traceless
    for i in range(1, ncol):
        dia = tuple(range(i + 1))
        data = [1j] * i + [-i * 1j]
        mat = numpy.zeros((ncol, ncol), dtype=complex)
        mat[dia, dia] = data
        yield mat * norm(mat)
