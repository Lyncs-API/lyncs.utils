from pytest import raises
from lyncs_utils import (
    first,
    last,
    indexes,
    dictzip,
    dictmap,
    flat_dict,
    nest_dict,
    compact_indexes,
    allclose,
)


def test_first():
    assert first({1: 1, 2: 2}) == 1
    assert first([1, 2]) == 1
    assert first((1, 2)) == 1


def test_last():
    # assert last({1: 1, 2: 2}) == 2
    assert last([1, 2]) == 2
    assert last((1, 2)) == 2


def test_indexes():
    assert tuple(indexes((1, 2, 3), 4)) == ()
    assert tuple(indexes((1, 2, 3), 1)) == (0,)
    assert tuple(indexes((1, 2, 1, 1), 1)) == (0, 2, 3)


def test_dictmap():
    dict1 = dict(a=1.0, b=2.0, c=3.0)
    assert dict(dictmap(int, dict1)) == {key: int(val) for key, val in dict1.items()}


def test_dictzip():
    dict1 = dict(a=1, b=2, c=3)
    dict2 = dict(a="a", b="b")
    assert dict(dictzip(dict1)) == dict(dictmap(lambda _: (_,), dict1))
    assert dict(dictzip(dict1, dict2)) == dict(a=(1, "a"), b=(2, "b"), c=(3, None))
    assert dict(dictzip(dict1, dict2, fill=False)) == dict(a=(1, "a"), b=(2, "b"))


def test_flatdict():
    dict1 = dict(a=dict(b=dict(c="d")))
    dict2 = dict(flat_dict(dict1))
    assert tuple(dict2) == (("a", "b", "c"),)
    assert dict2["a", "b", "c"] == "d"
    assert nest_dict(dict2) == dict1

    dict2 = dict(flat_dict(dict1, "/"))
    assert tuple(dict2) == ("a/b/c",)
    assert dict2["a/b/c"] == "d"
    assert dict(flat_dict(dict2, "/")) == dict2
    assert nest_dict(dict2, "/") == dict1

    dict2 = dict(flat_dict(dict1, sep=" ", base=("foo",)))
    assert tuple(dict2) == ("foo a b c",)
    assert dict2["foo a b c"] == "d"
    assert dict(flat_dict(dict2, " ")) == dict2
    assert nest_dict(dict2, " ")["foo"] == dict1


def test_example():
    assert list(compact_indexes([1, 2, 4, 6, 7, 8, 10, 12, 13])) == [
        1,
        range(2, 7, 2),
        7,
        range(8, 13, 2),
        13,
    ]


def test_range():
    assert list(compact_indexes(range(10)))[0] == range(10)
    assert list(compact_indexes(range(10, 0, -1)))[0] == range(10, 0, -1)
    assert list(compact_indexes(range(2, 20, 2)))[0] == range(2, 20, 2)


def test_error():
    with raises(TypeError):
        list(compact_indexes(1))

    with raises(TypeError):
        list(compact_indexes([0.1, "foo"]))


def test_allclose():
    assert allclose([1, 2, 3], (1, 2, 3))
    assert not allclose([1, 2, 3], (3, 2, 1))
    assert allclose(0, (0, 0, 0, (0, 0, 0)))
    assert not allclose(0, (0, 0, 1, (0, 0, 0)))
    assert allclose({"a": 0, "b": {"c": 0}}, 0)
    assert allclose(0, {"a": 0, "b": {"c": 0}})
    assert allclose({"a": 0, "b": {"c": 0}}, {"b": {"c": 0}, "a": 0})
    assert not allclose({"a": 0, "b": {"c": "d"}}, 0)
