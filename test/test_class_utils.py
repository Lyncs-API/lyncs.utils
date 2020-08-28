from IPython.lib.pretty import pretty
from lyncs_utils import compute_property, default_repr_pretty, add_kwargs_of
from random import random


class Foo:
    def __init__(self, length, bar=None, not_attr=None, method=None):
        self.length = length
        self.bar = bar

    _repr_pretty_ = default_repr_pretty

    @compute_property
    def random(self):
        return random()

    @compute_property
    def random_list(self):
        return [random() for _ in range(10)]

    random_list.key = "_random_list"

    def method(self):
        pass

    @add_kwargs_of(__init__)
    def decorated(self, **kwargs):
        pass

    def __dir__(self):
        return object.__dir__(self) + [
            "not_attr",
        ]


def test_repr_pretty():
    assert pretty(Foo(10)) == "Foo(10)"
    assert pretty(Foo(10, bar="bar")) == "Foo(10, bar='bar')"
    long_foo = Foo(123456, bar=list(range(20)))
    assert pretty(long_foo) == f"Foo(123456,\n    bar={list(range(20))})"
    assert pretty(Foo(10, bar=long_foo)) == "Foo(10, bar=Foo(123456, ...))"


def test_compute_property():
    foo = Foo(10)
    assert foo.random == foo.random
    assert foo.random == foo._random

    assert foo.random_list == foo.random_list
    assert foo.random_list == foo._random_list
    assert len(foo.random_list) == 10

    foo.random_list.append("foo")
    assert len(foo.random_list) == 10
    assert "foo" not in foo.random_list
