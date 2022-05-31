"""
Utils for iterables
"""

__all__ = [
    "first",
    "last",
    "indexes",
    "dictmap",
    "dictzip",
    "compact_indexes",
]

from .logical import isiterable


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


def dictmap(fnc, dct):
    "Map for dictionaries"
    for key, val in dict.items(dct):
        yield key, fnc(val)


def dictzip(*dicts, fill=True, default=None):
    """
    Zip for dictionaries.
    Missing keys are optionally filled with a given default value, otherwise ignored.
    """

    if fill:
        keys = set.union(*map(set, dicts))
    else:
        keys = set.intersection(*map(set, dicts))

    for key in keys:
        yield key, tuple(map(lambda _: _.get(key, default), dicts))


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
                    tmp = [
                        idx,
                    ]
                    step = 0
    if step == 0:
        yield from tmp
    else:
        yield range(tmp[0], tmp[1] + (1 if step > 0 else -1), step)
