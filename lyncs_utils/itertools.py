"""
Utils for iterables
"""

__all__ = [
    "first",
    "last",
    "indexes",
    "keys",
    "values",
    "items",
    "dictmap",
    "dictzip",
    "flat_dict",
    "nest_dict",
    "allclose",
    "compact_indexes",
]

from collections.abc import Mapping
from .logical import isiterable
from .math import isclose


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


def keys(dct):
    "Calls keys, if available, or dict.keys"
    try:
        return dct.keys()
    except AttributeError:
        return dict.keys(dct)


def values(dct):
    "Calls values, if available, or dict.values"
    try:
        return dct.values()
    except AttributeError:
        return dict.values(dct)


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
        all_keys = set.union(*map(set, map(keys, dicts)))
    else:
        all_keys = set.intersection(*map(set, map(keys, dicts)))

    for key in all_keys:
        values = tuple(map(lambda _: _.get(key, default), dicts))
        if values_only:
            yield values
        else:
            yield key, values


def flat_dict(dct, sep=None, base=()):
    "Flats a nested dictionary into a single dictionary with key that is either a tuple or joint with `sep` (if given)"
    for key, val in items(dct):
        key = base + (key,)
        if isinstance(val, Mapping):
            yield from flat_dict(val, sep=sep, base=key)
        else:
            if sep is not None:
                key = sep.join(key)
            yield key, val


def nest_dict(dct, sep=None):
    "Turns a dictionary into a nested dictionary splitting the key that is either a tuple or using `sep` (if given)"
    out = {}
    for key, val in items(dct):
        if sep is not None:
            key = key.split(sep)
        tmp = out
        for part in key[:-1]:
            tmp.setdefault(part, {})
            tmp = tmp[part]
        tmp[key[-1]] = val
    return out


def allclose(left, right, **kwargs):
    "Applies isclose to elements of iterable objects recursively"
    if not isiterable(left, exclude_str=True) and not isiterable(
        right, exclude_str=True
    ):
        return isclose(left, right, **kwargs)
    if not isiterable(left):
        left = [left] * len(right)
    if not isiterable(right):
        right = [right] * len(left)
    if len(left) != len(right):
        return False
    if isinstance(left, Mapping) or isinstance(right, Mapping):
        if not isinstance(left, Mapping):
            pairs = zip(left, values(right))
        elif not isinstance(right, Mapping):
            pairs = zip(values(left), right)
        else:
            if set(keys(left)) != set(keys(right)):
                return False
            pairs = dictzip(left, right, values_only=True)
    else:
        pairs = zip(left, right)
    return all((allclose(*pair, **kwargs) for pair in pairs))


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
