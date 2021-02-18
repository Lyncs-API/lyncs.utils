"""
Gamma matrices
"""

__all__ = [
    "gamma_matrices",
]

import numpy as np


def outer(left, right):
    "Outer product between two arrays"
    return np.kron(left, right)


def gamma_matrices(dim=4, euclidean=True):
    "Based on https://en.wikipedia.org/wiki/Higher-dimensional_gamma_matrices"

    assert dim > 0 and isinstance(dim, int)

    sigmas = (
        np.array(((0, 1), (1, 0))),
        np.array(((0, -1j), (1j, 0))),
        np.array(((1, 0), (0, -1))),
    )

    chiral = sigmas[2]
    gammas = [sigmas[0], (-1 if euclidean else -1j) * sigmas[1]]

    for idx in range((dim + 1) // 2 - 1):
        new = []
        for gamma in gammas:
            new.append(outer(gamma, sigmas[-1]))
        new.append(
            outer(np.identity(2 ** (idx + 1)), (1 if euclidean else 1j) * sigmas[0])
        )
        new.append(
            outer(np.identity(2 ** (idx + 1)), (1 if euclidean else 1j) * sigmas[1])
        )
        gammas = new
        chiral = outer(chiral, sigmas[2])

    if dim % 2:
        if euclidean:
            gammas[-1] *= 1j
        return tuple(gammas)

    gammas.append(chiral)

    return tuple(gammas)
