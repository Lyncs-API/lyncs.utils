"""
Functions returning or manipulating logical values (boolean)
"""

__all__ = [
    "single_true",
    "isiterable",
]

from collections.abc import Iterable


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
