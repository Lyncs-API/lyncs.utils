import logging
from io import StringIO
from pytest import raises, skip
from functools import partial
from lyncs_utils.functools import *


def test_is_keyword():
    assert is_keyword("foo")
    assert is_keyword("_foo")
    assert is_keyword("_foo123")
    assert not is_keyword("foo/bar")
    assert not is_keyword("1foo")
    assert not is_keyword("#foo")
    assert not is_keyword(1)


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

        def __call__(self, *args, **kwargs):
            pass

    class f7:
        pass

    class f8:
        def __new__(cls, *args, **kwargs):
            pass

        def __init__(self):
            pass

    f9 = partial(f8, a=1)
    f10 = partial(f1, a=1)
    f11 = f6()

    assert not has_args(f1)
    assert has_args(f2)
    assert not has_args(f3)
    assert has_args(f4)
    assert has_args(f5)
    assert has_args(f6)
    assert not has_args(f7)
    assert has_args(f8)
    assert has_args(f9)
    assert not has_args(f10)
    assert has_args(f11)

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

        def __call__(self, *args, **kwargs):
            pass

    class f7:
        pass

    class f8:
        def __new__(cls, *args, **kwargs):
            pass

        def __init__(self):
            pass

    f9 = partial(f8, a=1)
    f10 = partial(f1, a=1)
    f11 = f6()

    assert not has_kwargs(f1)
    assert not has_kwargs(f2)
    assert has_kwargs(f3)
    assert has_kwargs(f4)
    assert has_kwargs(f5)
    assert has_kwargs(f6)
    assert not has_kwargs(f7)
    assert has_kwargs(f8)
    assert has_kwargs(f9)
    assert not has_kwargs(f10)
    assert has_kwargs(f11)

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


def test_clickit():
    try:

        @clickit
        def foo(a, b, bar: int = 0):
            pass

    except ImportError:
        skip("No click")

    assert hasattr(foo, "__click_params__")
    params = {param.name: param for param in foo.__click_params__}
    assert "a" in params
    assert "b" in params
    assert "bar" in params

    assert params["a"].required
    assert params["b"].required
    assert not params["bar"].required


def test_spy():
    @spy
    def foo(bar=None):
        return "1234"

    logger = logging.getLogger()
    level = logger.getEffectiveLevel()

    logger.setLevel(logging.DEBUG)
    stream = StringIO()
    handle = logging.StreamHandler(stream)
    logger.addHandler(handle)
    foo("hello")
    logger.removeHandler(handle)
    out = stream.getvalue()
    assert "foo" in out
    assert "hello" in out
    assert "1234" in out

    logger.setLevel(logging.WARNING)
    stream = StringIO()
    handle = logging.StreamHandler(stream)
    logger.addHandler(handle)
    foo("hello")
    logger.removeHandler(handle)
    out = stream.getvalue()
    assert out == ""

    logger.setLevel(level)
