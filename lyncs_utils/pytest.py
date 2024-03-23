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
    "Replaces LazyFixture with its output"
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


@pytest.hookimpl(tryfirst=True)
def pytest_fixture_setup(fixturedef, request):
    """Replaces LazyFixture with its name"""
    val = getattr(request, "param", None)
    if is_lazy_fixture(val):
        request.param = request.getfixturevalue(val.name)


@pytest.hookimpl(hookwrapper=True)
def pytest_generate_tests(metafunc):
    """Runs normalize_call for all calls"""
    yield
    normalize_metafunc_calls(metafunc)


def normalize_metafunc_calls(metafunc, used_keys=None):
    """Runs normalize_call for all calls"""
    newcalls = []
    for callspec in metafunc._calls:
        calls = normalize_call(callspec, metafunc, used_keys)
        newcalls.extend(calls)
    metafunc._calls = newcalls


def normalize_call(callspec, metafunc, used_keys=None):
    "Replaces special fixtures with their output"
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
    """Creates a copy of callspec"""
    new = copy(callspec)
    object.__setattr__(new, "params", copy(callspec.params))
    object.__setattr__(new, "_idlist", copy(callspec._idlist))
    return new


def copy_metafunc(metafunc):
    """Creates a copy of metafunc"""
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
