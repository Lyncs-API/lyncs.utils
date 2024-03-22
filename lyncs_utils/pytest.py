"""
Include this module only within pytest
"""

__all__ = ("DynParam", "GetMark", "lazy_fixture")

from copy import copy
from dataclasses import dataclass
import typing
import pytest


@dataclass
class DynParam:
    """
    An object that allows to generate test parameters dynamically.
    """

    arg: None
    ids: callable = lambda val: str(val)

    def __call__(self, test):
        return self.arg(test)


@dataclass
class GetMark(DynParam):
    """
    Takes a dictionary as input and returns the value corresponding to the first matching mark.
    """

    default: str = None

    def __call__(self, test):
        out = set()
        for mark in getattr(test, "pytestmark", ()):
            if mark.name in self.arg:
                out.update(self.arg[mark.name])
        if not out:
            if self.default is None:
                return ()
            return self.arg[self.default]
        return tuple(out)


@pytest.hookimpl(hookwrapper=True)
def pytest_generate_tests(metafunc):
    "Runs normalize_call for all calls"
    yield
    newcalls = []
    for callspec in metafunc._calls:
        calls = normalize_call(callspec, metafunc.function)
        newcalls.extend(calls)
    metafunc._calls = newcalls


def normalize_call(callspec, test):
    "Replaces DynParam with its output"
    for idx, (key, val) in enumerate(callspec.params.items()):
        if is_dyn_param(val):
            ids = val.ids
            vals = val(test)
            newcalls = []
            for val in vals:
                newcallspec = copy_callspec(callspec)
                newcallspec.params[key] = val
                newcallspec._idlist[idx] = ids(val)
                calls = normalize_call(newcallspec, test)
                newcalls.extend(calls)
            return newcalls
    return [callspec]


def copy_callspec(callspec):
    "Creating a copy of callspec"
    new = copy(callspec)
    object.__setattr__(new, "params", copy(callspec.params))
    object.__setattr__(new, "_idlist", copy(callspec._idlist))
    return new


def is_dyn_param(val):
    "Checks if is DynParam"
    return isinstance(val, DynParam)


@dataclass
class LazyFixture:
    """Lazy fixture dataclass."""

    name: str


def lazy_fixture(name: str) -> LazyFixture:
    """Mark a fixture as lazy.

    Credit:
    - https://github.com/TvoroG/pytest-lazy-fixture/issues/65#issuecomment-1914581161
    """
    return LazyFixture(name)


def is_lazy_fixture(value: object) -> bool:
    """Check whether a value is a lazy fixture.

    Credit:
    - https://github.com/TvoroG/pytest-lazy-fixture/issues/65#issuecomment-1914581161
    """
    return isinstance(value, LazyFixture)


def pytest_make_parametrize_id(
    config: pytest.Config,
    val: object,
    argname: str,
) -> (str, None):
    """Inject lazy fixture parametrized id.

    Reference:
    - https://bit.ly/48Off6r

    Args:
        config (pytest.Config): pytest configuration.
        value (object): fixture value.
        argname (str): automatic parameter name.

    Returns:
        str: new parameter id.

    Credit:
    - https://github.com/TvoroG/pytest-lazy-fixture/issues/65#issuecomment-1914581161
    """
    if is_lazy_fixture(val):
        return typing.cast(LazyFixture, val).name
    return None


@pytest.hookimpl(tryfirst=True)
def pytest_fixture_setup(
    fixturedef: pytest.FixtureDef,
    request: pytest.FixtureRequest,
) -> (object, None):
    """Lazy fixture setup hook.

    This hook will never take over a fixture setup but just simply will
    try to resolve recursively any lazy fixture found in request.param.

    Reference:
    - https://bit.ly/3SyvsXJ

    Args:
        fixturedef (pytest.FixtureDef): fixture definition object.
        request (pytest.FixtureRequest): fixture request object.

    Returns:
        object | None: fixture value or None otherwise.

    Credit:
    - https://github.com/TvoroG/pytest-lazy-fixture/issues/65#issuecomment-1914581161
    """
    if hasattr(request, "param") and request.param:
        request.param = _resolve_lazy_fixture(request.param, request)
    return None


def _resolve_lazy_fixture(__val: object, request: pytest.FixtureRequest) -> object:
    """Lazy fixture resolver.

    Args:
        __val (object): fixture value object.
        request (pytest.FixtureRequest): pytest fixture request object.

    Returns:
        object: resolved fixture value.

    Credit:
    - https://github.com/TvoroG/pytest-lazy-fixture/issues/65#issuecomment-1914581161
    """
    if isinstance(__val, (list, tuple)):
        return tuple(_resolve_lazy_fixture(v, request) for v in __val)
    if isinstance(__val, typing.Mapping):
        return {k: _resolve_lazy_fixture(v, request) for k, v in __val.items()}
    if not is_lazy_fixture(__val):
        return __val
    lazy_obj = typing.cast(LazyFixture, __val)
    return request.getfixturevalue(lazy_obj.name)
