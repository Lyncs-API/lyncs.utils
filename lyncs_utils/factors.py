"""
A collection of factorization utils
"""

__all__ = [
    "prod",
    "factors",
    "prime_factors",
]

from functools import reduce

try:
    from math import prod
except ImportError:

    def prod(arr):
        "Returns the product of the elements"
        return reduce((lambda x, y: x * y), arr, 1)


def factors(num):
    "Returns the list of factors of n"
    assert isinstance(num, int), "Num must be int"
    for i in range(2, num // 2):
        if num % i == 0:
            yield i
    yield num


def prime_factors(num):
    "Returns the list of prime factors of n"
    itr = iter(PRIMES)
    cur = next(itr)
    stop = int(num ** 0.5) + 1
    while num > 1 and cur < stop:
        while num % cur == 0:
            yield cur
            num //= cur

        # Looping first over the known prime numbers
        try:
            cur = next(itr)
        # then proceeding only with the odd numbers
        except StopIteration:
            cur += 2

    if num > 1:
        yield num


PRIMES = (
    2,
    3,
    5,
    7,
    11,
    13,
    17,
    19,
    23,
    29,
    31,
    37,
    41,
    43,
    47,
    53,
    59,
    61,
    67,
    71,
    73,
    79,
    83,
    89,
    97,
    101,
    103,
    107,
    109,
    113,
    127,
    131,
    137,
    139,
    149,
    151,
    157,
    163,
    167,
    173,
    179,
    181,
    191,
    193,
    197,
    199,
)
