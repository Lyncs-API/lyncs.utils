"Reductions using functools.reduce"

__all__ = [
    "prod",
    "sum",
]

from functools import reduce


def prod(arr):
    "Returns the product of the elements"
    return reduce((lambda x, y: x * y), arr, 1)


def sum(arr):
    "Returns the sum of the elements"
    return reduce((lambda x, y: x + y), arr, 0)
