from pytest import raises
from lyncs_utils.functools import *


def test_varnames():
    def f(a, b, c=1, d=2):
        pass

    assert get_varnames(f) == ("a", "b", "c", "d")
    assert get_varnames("") == ()


def test_has_args():
    def f1(a, b, c=1, d=2):
        pass

    def f2(a, b, *args, c=1, d=2):
        pass

    def f3(a, b, c=1, d=2, **kwargs):
        pass

    def f4(a, b, *args, c=1, d=2, **kwargs):
        pass

    f5 = lambda *args, **kwargs: None

    class f6:
        def __init__(self, *args, **kwargs):
            pass

    class f7:
        pass

    class f8:
        def __new__(cls, *args, **kwargs):
            pass

        def __init__(self):
            pass

    assert not has_args(f1)
    assert has_args(f2)
    assert not has_args(f3)
    assert has_args(f4)
    assert has_args(f5)
    assert has_args(f6)
    assert not has_args(f7)
    assert has_args(f8)

    with raises(TypeError):
        has_args(1)


def test_has_kwargs():
    def f1(a, b, c=1, d=2):
        pass

    def f2(a, b, *args, c=1, d=2):
        pass

    def f3(a, b, c=1, d=2, **kwargs):
        pass

    def f4(a, b, *args, c=1, d=2, **kwargs):
        pass

    f5 = lambda *args, **kwargs: None

    class f6:
        def __init__(self, *args, **kwargs):
            pass

    class f7:
        pass

    class f8:
        def __new__(cls, *args, **kwargs):
            pass

        def __init__(self):
            pass

    assert not has_kwargs(f1)
    assert not has_kwargs(f2)
    assert has_kwargs(f3)
    assert has_kwargs(f4)
    assert has_kwargs(f5)
    assert has_kwargs(f6)
    assert not has_kwargs(f7)
    assert has_kwargs(f8)

    with raises(TypeError):
        has_kwargs(1)


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


def test_select_kwargs():
    def f(a, b, **kwargs):
        return (a, b), kwargs

    args, kwargs = select_kwargs(f, 1, 2, c=3, d=4)
    assert args == (1, 2)
    assert kwargs == dict(c=3, d=4)

    args, kwargs = select_kwargs(f, 1, 2, b=None, c=3, d=4)
    assert args == (1, 2)
    assert kwargs == dict(c=3, d=4)

    args, kwargs = select_kwargs(f, 1, b=2, c=3, d=4)
    assert args == (1, 2)
    assert kwargs == dict(c=3, d=4)

    def f(a, b, c=1, d=2):
        return (a, b), dict(c=c, d=d)

    args, kwargs = select_kwargs(f, 1, 2, c=3, d=4)
    assert args == (1, 2)
    assert kwargs == dict(c=3, d=4)

    args, kwargs = select_kwargs(f, 1, 2, b=None, c=3, d=4)
    assert args == (1, 2)
    assert kwargs == dict(c=3, d=4)

    args, kwargs = select_kwargs(f, 1, b=2, c=3, d=4, e=5, f=6)
    assert args == (1, 2)
    assert kwargs == dict(c=3, d=4)