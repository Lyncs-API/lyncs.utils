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

    def __call__(self, test):
        return self.arg(test)


@dataclass
class GetMark(DynParam):
    """
    Takes a dictionary as input and returns the value corresponding to the first matching mark.
    """

    default: list = ()

    def __call__(self, test):
        for mark in getattr(test, "pytestmark", ()):
            if mark.name in self.arg:
                return self.arg[mark.name]
        return self.default


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
    for key, val in callspec.params.items():
        if is_dyn_param(val):
            vals = val(test)
            newcalls = []
            for val in vals:
                newcallspec = copy(callspec)
                newcallspec.params = copy(callspec.params)
                newcallspec.params[key] = val
                calls = normalize_call(newcallspec, test)
                newcalls.extend(calls)
            return newcalls
    return [callspec]


def is_dyn_param(val):
    "Checks if is DynParam"
    return isinstance(val, DynParam)
