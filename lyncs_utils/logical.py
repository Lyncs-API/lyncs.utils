"""
Functions returning or manipulating logical values (boolean)
"""

__all__ = [
    "single_true",
    "isiterable",
    "interactive",
]

from collections.abc import Iterable
import __main__


def isiterable(obj, types=None):
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
    if types is None:
        return isinstance(obj, Iterable)
    return isinstance(obj, Iterable) and all((isinstance(val, types) for val in obj))


def single_true(iterable):
    """ Returns if one and only one element of the argument is True """
    i = iter(iterable)
    return any(i) and not any(i)


def interactive():
    "Returns if Python has been run in interactive mode"
    # https://stackoverflow.com/questions/2356399/tell-if-python-is-in-interactive-mode
    return not hasattr(__main__, "__file__")
