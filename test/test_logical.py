import sys
from pytest import raises
import lyncs_utils
from lyncs_utils import isiterable, single_true, interactive, version


def test_isiterable():
    assert isiterable([])
    assert isiterable(map(lambda _: _, []))
    assert isiterable([1, 2, 3], int)
    assert not isiterable(1)
    assert not isiterable([1, 2, 3], (str, float))


def test_single_true():
    assert single_true([1])
    assert single_true([1, 0, 0, 0])
    assert single_true([True, False, 0, 0])
    assert not single_true([False, True, False, True])
    assert not single_true(
        [
            False,
        ]
    )


def test_interactive():
    assert not interactive()


def test_version():
    pyv = sys.version_info
    num = f"{pyv.major}.{pyv.minor}.{pyv.micro}"
    assert version(num)
    assert version(num, opr="ge")
    assert version(num, opr="eq")
    assert version(num, opr="le")
    assert not version(num, opr="gt")
    assert not version(num, opr="ne")
    assert not version(num, opr="lt")

    assert version(lyncs_utils.__version__, pkg=lyncs_utils)

    with raises(TypeError):
        version(num, opr=1)
