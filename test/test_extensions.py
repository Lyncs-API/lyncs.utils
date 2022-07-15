import ctypes
import os
import io
import sys
import tempfile
from lyncs_utils import redirect_stdout
from pytest import raises, mark
from itertools import count as _count
from lyncs_utils.extensions import *
from lyncs_utils.numpy import numpy


def test_count():
    assert not callable(_count())
    counter = count()
    assert list(counter(5)) == list(range(5))
    assert list(counter(5)) == list(range(5, 10))


def test_lazy_import():
    utils = lazy_import("lyncs_utils")
    assert isinstance(utils, type(os))

    assert "lyncs_setuptools" not in sys.modules
    setup = lazy_import("lyncs_setuptools")
    assert "lyncs_setuptools" in sys.modules
    assert isinstance(setup, type(os))
    assert setup.__name__ == "lyncs_setuptools"

    with raises(ImportError):
        lazy_import("non.existing.module")


@mark.skipif(isinstance(numpy, Exception), reason="Numpy not available")
def test_setitems():
    arr = numpy.zeros((5, 4, 6))
    setitems(arr, 13)
    assert (arr == 13).all()

    setitems(arr, range(arr.shape[0]))
    for i in range(arr.shape[0]):
        assert (arr[i] == i).all()

    rand = numpy.random.rand(*arr.shape) * 100
    setitems(arr, rand)
    assert (arr == rand).all()


def test_commonsuffix():
    assert commonsuffix(["foo", "bar"]) == ""
    assert commonsuffix(["foo.txt", "bar.txt"]) == ".txt"


def test_raiseif():
    fnc = raiseif(False, RuntimeError())(lambda: "foo")
    assert fnc() == "foo"

    fnc = raiseif(True, RuntimeError())(lambda: "foo")
    with raises(RuntimeError):
        fnc()


def test_raiseonuse():
    foo = RaiseOnUse(RuntimeError())

    with raises(RuntimeError):
        foo()

    with raises(RuntimeError):
        foo.bar

    with raises(RuntimeError):
        foo.bar = None

    with raises(RuntimeError):
        foo["bar"]

    with raises(RuntimeError):
        foo["bar"] = None


def test_redirect_stdout():
    libc = ctypes.CDLL(None)

    fp = io.StringIO()

    with redirect_stdout(fp):
        print("this is from python")
        libc.puts(b"this is from C\n")
        os.system("echo this is from echo")

    output = fp.getvalue().split("\n")

    assert "this is from python" in output
    assert "this is from C" in output
    assert "this is from echo" in output

    fp = tempfile.TemporaryFile(mode="w+")

    with redirect_stdout(fp):
        print("this is from python")
        libc.puts(b"this is from C\n")
        os.system("echo this is from echo")

    fp.flush()
    fp.seek(0, io.SEEK_SET)
    output = fp.read().split("\n")

    assert "this is from python" in output
    assert "this is from C" in output
    assert "this is from echo" in output


def test_keydefaultdict():
    foo = keydefaultdict(lambda key: key * 3)
    assert foo[0] == 0
    assert foo[3] == 9
    assert foo["a"] == "aaa"


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
