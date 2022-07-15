"""
Functions returning or manipulating logical values (boolean)
"""

__all__ = [
    "single_true",
    "isiterable",
    "interactive",
    "version",
]

import sys
from collections.abc import Iterable
import operator
from packaging.version import parse as parse_version
import __main__


def isiterable(obj, types=None, exclude_str=False):
    """Returns if the argument is an iterable object or not.

    Examples
    --------
    >>> isiterable([1,2,3])
    True
    >>> isiterable([1,2,3], int)
    True
    >>> isiterable([1,2,3], (str, float))
    False
    """
    if not isinstance(obj, Iterable):
        return False
    if isinstance(obj, str):
        return False
    if types is not None:
        return all((isinstance(val, types) for val in obj))
    return True


def single_true(iterable):
    """Returns if one and only one element of the argument is True"""
    i = iter(iterable)
    return any(i) and not any(i)


def interactive():
    "Returns if Python has been run in interactive mode"
    # https://stackoverflow.com/questions/2356399/tell-if-python-is-in-interactive-mode
    return not hasattr(__main__, "__file__")


def version(num, pkg=None, opr=None):
    """
    Compares the version number (by default of the python interpreter with >=).
    For comparing the version number of a package pass the latter via `pkg`.
    For changing the version comparison operator pass to `opr` one between:
    - `ge`, `gt`, `eq`, `ne`, `lt`, `le`
    """

    if not pkg:
        pyv = sys.version_info
        pkg = f"{pyv.major}.{pyv.minor}.{pyv.micro}"
    if hasattr(pkg, "__version__"):
        pkg = pkg.__version__

    if not opr:
        opr = "ge"
    if isinstance(opr, str):
        opr = getattr(operator, opr)
    if not callable(opr):
        raise TypeError(f"Unsupported type for opr: {type(opr)}")

    num = parse_version(num)
    pkg = parse_version(pkg)
    return opr(pkg, num)
