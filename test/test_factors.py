from lyncs_utils import prime_factors, factors, prod


def test_factors():
    nums = [1, 20, 30, 123, 211]
    for num in nums:
        assert prod(prime_factors(num)) == num
        assert prod(factors(num)) % num == 0
        assert prod(prime_factors(num ** 2)) == num ** 2
