from lyncs_utils import (
    compute_property,
    static_property,
    class_property,
    default_repr_pretty,
    add_kwargs_of,
    add_to,
    call_method,
    default,
)
from random import random
import pytest

try:
    from IPython.lib.pretty import pretty

    no_ipython = False
except ImportError:
    no_ipython = True
mark_ipython = pytest.mark.skipif(no_ipython, reason="Ipython not available")


class Foo:
    def __init__(self, length, bar=None, not_attr=None, method=None):
        self.length = length
        self.bar = bar

    _repr_pretty_ = default_repr_pretty
    option = default(False, type=bool)

    @static_property
    def pi():
        return 3.14

    @class_property
    def type(cls):
        return cls

    @compute_property
    def random(self):
        return random()

    @compute_property
    def random_list(self):
        return [random() for _ in range(10)]

    random_list.key = "_random_list"

    def method(self):
        pass

    def get_length(self):
        return self.length

    @add_kwargs_of(__init__)
    def decorated(self, **kwargs):
        pass

    def __dir__(self):
        return object.__dir__(self) + [
            "not_attr",
        ]


def test_add_to():
    @add_to(Foo)
    def added(self):
        return 1234

    @add_to(Foo)
    class Added:
        def __new__(cls, foo):
            return 5678

    assert hasattr(Foo, "added")
    assert Foo(0).added() == added(None)
    assert hasattr(Foo, "Added")
    assert Foo(0).Added() == Added(None)


@mark_ipython
def test_repr_pretty():
    assert pretty(Foo(10)) == "Foo(10)"
    assert pretty(Foo(10, bar="bar")) == "Foo(10, bar='bar')"
    long_foo = Foo(123456, bar=list(range(20)))
    assert pretty(long_foo) == f"Foo(123456,\n    bar={list(range(20))})"
    assert pretty(Foo(10, bar=long_foo)) == "Foo(10, bar=Foo(123456, ...))"


def test_compute_property():
    assert isinstance(Foo.random, property)

    foo = Foo(10)
    assert foo.random == foo.random
    assert foo.random == foo._random

    assert foo.random_list == foo.random_list
    assert foo.random_list == foo._random_list
    assert len(foo.random_list) == 10

    foo.random_list.append("foo")
    assert len(foo.random_list) == 10
    assert "foo" not in foo.random_list


def test_static_property():
    foo = Foo(10)
    assert foo.pi == 3.14
    assert Foo.pi == 3.14


def test_class_property():
    foo = Foo(10)
    assert foo.type == Foo
    assert Foo.type == Foo


def test_default():
    foo = Foo(10)
    assert foo.option == False
    assert Foo.option._key == "_option"
    foo.option = True
    assert foo.option == True
    with pytest.raises(TypeError):
        foo.option = "foo"
    foo = Foo(10)
    assert foo.option == False


def test_call_method():
    foo = Foo(10)
    assert call_method(foo, "get_length") == 10
    assert call_method(foo, foo.get_length) == 10
    assert call_method(foo, Foo.get_length) == 10
