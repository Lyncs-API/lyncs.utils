from pytest import warns
from lyncs_utils import isclose, prime_factors, factors, prod, sign, iscomplex


def test_iscomplex():
    assert iscomplex(1j)
    assert not iscomplex(1)


def test_isclose():
    assert isclose(1, 1.0001, abs_tol=0.0001)
    assert not isclose(1, 1.0002, abs_tol=0.0001)
    with warns(None):
        assert isclose(1, 1.01, warn_tol=0.1)
    assert isclose(1j, 1.0001j, abs_tol=0.0001)
    assert not isclose(1j, 1.0002j, abs_tol=0.0001)
    assert isclose("a", "a")


def test_sign():
    assert sign(2) == 1
    assert sign(0) == 1
    assert sign(-2) == -1


def test_factors():
    nums = [1, 20, 30, 123, 211]
    for num in nums:
        assert prod(prime_factors(num)) == num
        assert prod(factors(num)) % num == 0
        assert prod(prime_factors(num**2)) == num**2
