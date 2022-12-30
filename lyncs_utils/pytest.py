"""
Include this module only within pytest
"""

__all__ = ("DynParam", "GetMark")

from copy import copy
from dataclasses import dataclass
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
