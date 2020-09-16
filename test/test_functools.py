from lyncs_utils.functools import *


def test_varnames():
    def f(a, b, c=1, d=2):
        pass

    assert get_varnames(f) == ("a", "b", "c", "d")
    assert get_varnames("") == ()


def test_annotations():
    def f(a, b: float, c=1, d: str = 2):
        pass

    assert get_varnames(f) == ("a", "b", "c", "d")
    assert apply_annotations(f, 1, 2) == ((1, 2.0), {})
    assert apply_annotations(f, 1, b=2) == ((1,), {"b": 2.0})
    assert apply_annotations(f, 1, b=2, d=3) == ((1,), {"b": 2.0, "d": "3"})
    assert apply_annotations(f, 1, 2, 3, 4) == ((1, 2.0, 3, "4"), {})

    def f(a, b, c=1, d=2):
        pass

    assert apply_annotations(f, 1, 2, 3, 4) == ((1, 2, 3, 4), {})
