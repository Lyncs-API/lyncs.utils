"""
Include this module only within pytest
"""

__all__ = ("DynParam", "GetMark", "lazy_fixture")

from copy import copy
from dataclasses import dataclass
import typing
import pytest


def is_dyn_param(val):
    "Checks if is DynParam"
    return isinstance(val, DynParam)


@dataclass
class DynParam:
    """An object that allows to generate test parameters dynamically."""

    arg: None
    ids: callable = lambda val: str(val)

    def __call__(self, test):
        return self.arg(test)


@dataclass
class GetMark(DynParam):
    """Takes a dictionary as input and returns the value corresponding to the first matching mark."""

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


def normalize_dyn_param(callspec, metafunc, used_keys, idx, key, val):
    """Replaces DynParam with its output"""
    ids = val.ids
    test = metafunc.function
    vals = val(test)
    newcalls = []
    for val in vals:
        newcallspec = copy_callspec(callspec)
        newcallspec.params[key] = val
        newcallspec._idlist[idx] = ids(val)
        calls = normalize_call(newcallspec, metafunc)
        newcalls.extend(calls)
    return newcalls


@dataclass
class LazyFixture:
    """Lazy fixture dataclass."""

    name: str


def lazy_fixture(name: str) -> LazyFixture:
    """Mark a fixture as lazy."""
    return LazyFixture(name)


def is_lazy_fixture(value: object) -> bool:
    """Check whether a value is a lazy fixture."""
    return isinstance(value, LazyFixture)


def normalize_lazy_fixture(callspec, metafunc, used_keys, idx, key, val):
    "Replaces lazy with its output"
    fm = metafunc.config.pluginmanager.get_plugin("funcmanage")
    try:
        if pytest.version_tuple >= (8, 0, 0):
            fixturenames_closure, arg2fixturedefs = fm.getfixtureclosure(
                metafunc.definition.parent, [val.name], {}
            )
        else:
            _, fixturenames_closure, arg2fixturedefs = fm.getfixtureclosure(
                [val.name], metafunc.definition.parent
            )
    except ValueError:
        # 3.6.0 <= pytest < 3.7.0; `FixtureManager.getfixtureclosure` returns 2 values
        fixturenames_closure, arg2fixturedefs = fm.getfixtureclosure(
            [val.name], metafunc.definition.parent
        )
    except AttributeError:
        # pytest < 3.6.0; `Metafunc` has no `definition` attribute
        fixturenames_closure, arg2fixturedefs = fm.getfixtureclosure(
            [val.name], current_node
        )

    extra_fixturenames = [
        fname for fname in fixturenames_closure if fname not in callspec.params
    ]  # and fname not in callspec.funcargs]

    newmetafunc = copy_metafunc(metafunc)
    newmetafunc.fixturenames = extra_fixturenames
    newmetafunc._arg2fixturedefs.update(arg2fixturedefs)
    newmetafunc._calls = [callspec]
    fm.pytest_generate_tests(newmetafunc)
    normalize_metafunc_calls(newmetafunc, used_keys)
    return newmetafunc._calls


@pytest.hookimpl(hookwrapper=True)
def pytest_generate_tests(metafunc):
    "Runs normalize_call for all calls"
    yield
    normalize_metafunc_calls(metafunc)


def normalize_metafunc_calls(metafunc, used_keys=None):
    newcalls = []
    for callspec in metafunc._calls:
        calls = normalize_call(callspec, metafunc, used_keys)
        newcalls.extend(calls)
    metafunc._calls = newcalls


def normalize_call(callspec, metafunc, used_keys=None):
    "Replaces DynParam with its output"
    used_keys = used_keys or set()
    for idx, (key, val) in enumerate(callspec.params.items()):
        if key in used_keys:
            continue
        used_keys.add(key)
        if is_dyn_param(val):
            return normalize_dyn_param(callspec, metafunc, used_keys, idx, key, val)
        if is_lazy_fixture(val):
            return normalize_lazy_fixture(callspec, metafunc, used_keys, idx, key, val)
    return [callspec]


def copy_callspec(callspec):
    "Creating a copy of callspec"
    new = copy(callspec)
    object.__setattr__(new, "params", copy(callspec.params))
    object.__setattr__(new, "_idlist", copy(callspec._idlist))
    return new


def copy_metafunc(metafunc):
    copied = copy(metafunc)
    copied.fixturenames = copy(metafunc.fixturenames)
    copied._calls = []

    try:
        copied._ids = copy(metafunc._ids)
    except AttributeError:
        # pytest>=5.3.0
        pass

    copied._arg2fixturedefs = copy(metafunc._arg2fixturedefs)
    return copied


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
