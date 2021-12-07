from lyncs_utils.contextlib import *


def test_setting():
    class Foo:
        pass

    foo = Foo()

    with setting(foo, "bar", 1234) as old:
        assert hasattr(foo, "bar")
        assert foo.bar == 1234
        assert old is None

    assert not hasattr(foo, "bar")

    foo.bar = "old"

    with setting(foo, "bar", "new") as old:
        assert hasattr(foo, "bar")
        assert foo.bar == "new"
        assert old == "old"

    assert hasattr(foo, "bar")
    assert foo.bar == "old"


def test_updating():
    foo = dict()

    with updating(foo, "bar", 1234) as old:
        assert "bar" in foo
        assert foo["bar"] == 1234
        assert old is None

    assert "bar" not in foo

    foo["bar"] = "old"

    with updating(foo, "bar", "new") as old:
        assert "bar" in foo
        assert foo["bar"] == "new"
        assert old == "old"

    assert "bar" in foo
    assert foo["bar"] == "old"
