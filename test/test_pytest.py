import pytest
from lyncs_utils.pytest import GetMark, DynParam, lazy_fixture


@pytest.fixture(params=[GetMark({"mark1": [11], "mark2": [12]}, default="mark1")])
def param1(request):
    return request.param


@pytest.fixture(params=[GetMark({"mark1": [21]}, default="mark1")])
def param2(request):
    return request.param


@pytest.fixture(params=[DynParam(lambda test: [test.__name__])])
def name(request):
    return request.param


def test_default(param1, param2, name):
    assert param1 == 11
    assert param2 == 21
    assert name == "test_default"


@pytest.mark.mark1
def test_mark1(param1, param2, name):
    assert param1 == 11
    assert param2 == 21
    assert name == "test_mark1"


@pytest.mark.mark2
def test_mark2(param1, param2, name):
    assert param1 == 12
    assert param2 == 21
    assert name == "test_mark2"


@pytest.fixture
def one():
    return 1


@pytest.mark.parametrize(
    "arg1,arg2",
    [
        ("val1", lazy_fixture("one")),
    ],
)
def test_func(arg1, arg2):
    assert arg2 == 1
