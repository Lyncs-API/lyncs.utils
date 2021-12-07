"Functionalities using contextmanager"

from contextlib import contextmanager


@contextmanager
def setting(obj, attr, value, default=None):
    """
    Context manager that temporaly sets an attribute of an object.
    It yields the current value of the attribute if present,
    otherwise returns `default` (`None` by default).
    If the attribute did not exist, it is removed on exit,
    otherwise its original value is restored.
    """

    try:
        old = getattr(obj, attr)
        had = True
    except AttributeError:
        old = default
        had = False

    setattr(obj, attr, value)

    yield old

    if had:
        setattr(obj, attr, old)
    else:
        delattr(obj, attr)


@contextmanager
def updating(obj, key, value, default=None):
    """
    Context manager that temporaly sets an item (key) of an object.
    It yields the current value of the item if present,
    otherwise returns `default` (`None` by default).
    If the item did not exist, it is removed on exit,
    otherwise its original value is restored.
    """

    try:
        old = obj[key]
        had = True
    except KeyError:
        old = default
        had = False

    obj[key] = value

    yield old

    if had:
        obj[key] = old
    else:
        del obj[key]
