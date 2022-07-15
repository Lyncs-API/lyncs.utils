"""
Utils for iterables
"""

__all__ = [
    "first",
    "last",
    "indexes",
    "dictmap",
    "dictzip",
    "flat_dict",
    "compact_indexes",
]

from .logical import isiterable
from collections.abc import Mapping


def first(iterable):
    "Returns the first element of iterable"
    return next(iter(iterable))


def last(iterable):
    "Returns the last element of iterable"
    return next(reversed(iterable))


def indexes(iterable, val):
    "Returns all indexes of an occurrance"
    start = 0
    while True:
        try:
            index = iterable.index(val, start)
            yield index
            start = index + 1
        except ValueError:
            return


def items(dct):
    "Calls items, if available, or dict.items"
    try:
        return dct.items()
    except AttributeError:
        return dict.items(dct)


def dictmap(fnc, dct):
    "Map for dictionaries"
    for key, val in items(dct):
        yield key, fnc(val)


def dictzip(*dicts, fill=True, default=None, values_only=False):
    """
    Zip for dictionaries.
    Missing keys are optionally filled with a given default value, otherwise ignored.
    """

    if fill:
        keys = set.union(*map(set, dicts))
    else:
        keys = set.intersection(*map(set, dicts))

    for key in keys:
        values = tuple(map(lambda _: _.get(key, default), dicts))
        if values_only:
            yield values
        else:
            yield key, values


def flat_dict(dct, sep="/", base=None):
    "Flats a nested dictionary into a single dictionary with key separated by given `sep`"
    for key, val in items(dct):
        if base:
            key = f"{base}{sep}{key}"
        if isinstance(val, Mapping):
            yield from flat_dict(val, sep=sep, base=key)
        else:
            yield key, val


def compact_indexes(indexes):
    """
    Returns a list of ranges or integers
    as they occur sequentially in the list

    Examples
    --------
    >>> list(compact_indexes([1, 2, 4, 6, 7, 8, 10, 12, 13]))
    [1, range(2, 7, 2), 7, range(8, 13, 2), 13]
    """

    if not isiterable(indexes, int):
        raise TypeError("compact_indexes requires a list of integers")

    tmp = []
    step = 0
    for idx in indexes:
        if len(tmp) < 2:
            tmp.append(idx)
        else:
            if step == 0:
                step = tmp[1] - tmp[0]
                if step == 0 or idx - tmp[1] != step:
                    yield tmp.pop(0)
                    tmp.append(idx)
                    step = 0
                else:
                    tmp[1] = idx
            else:
                if idx - tmp[1] == step:
                    tmp[1] = idx
                else:
                    yield range(tmp[0], tmp[1] + (1 if step > 0 else -1), step)
                    tmp = [idx]
                    step = 0
    if step == 0:
        yield from tmp
    else:
        yield range(tmp[0], tmp[1] + (1 if step > 0 else -1), step)
