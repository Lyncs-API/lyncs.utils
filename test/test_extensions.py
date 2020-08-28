from pytest import raises
from itertools import count as _count
from lyncs_utils import count, FreezableDict


def test_count():
    assert not callable(_count())
    counter = count()
    assert list(counter(5)) == list(range(5))
    assert list(counter(5)) == list(range(5, 10))


def test_freezable_dict():
    assert isinstance(FreezableDict(), dict)

    foo = FreezableDict(one=1, two=2)
    foo12 = foo.freeze()

    assert not foo.frozen
    assert foo.allows_new
    assert foo.allows_changes

    assert foo12.frozen
    assert not foo12.allows_new
    assert not foo12.allows_changes

    assert foo.freeze() is not foo
    assert foo12.freeze() is foo12

    foo12 = foo.copy()

    foo12.frozen = True
    foo12.allows_new = False
    foo12.allows_changes = False

    assert foo12.frozen
    assert not foo12.allows_new
    assert not foo12.allows_changes

    with raises(ValueError):
        foo12.frozen = False

    with raises(ValueError):
        foo12.allows_new = True

    with raises(ValueError):
        foo12.allows_changes = True

    foo.update(foo)
    foo12.update()
    with raises(RuntimeError):
        foo12.update(foo)

    foo["two"] = foo.pop("two")
    with raises(RuntimeError):
        foo12.pop("two")

    assert foo12.pop("three", 3) == 3

    foo12.setdefault("two", 2)
    with raises(RuntimeError):
        foo12.setdefault("three", 3)

    assert foo == foo12

    dict_in_dict = FreezableDict(foo=foo)
    did = dict_in_dict.freeze(allows_new=True)

    assert did.frozen
    assert did.allows_new
    assert not did.allows_changes
    assert did["foo"].frozen

    did["foo_copy"] = foo.copy()
    assert did["foo_copy"].frozen
    did["foo12"] = foo12
    assert did["foo12"] is foo12
