from lyncs_utils import prime_factors, factors, prod, sign


def test_sign():
    assert sign(2) == 1
    assert sign(0) == 1
    assert sign(-2) == -1


def test_factors():
    nums = [1, 20, 30, 123, 211]
    for num in nums:
        assert prod(prime_factors(num)) == num
        assert prod(factors(num)) % num == 0
        assert prod(prime_factors(num ** 2)) == num ** 2
