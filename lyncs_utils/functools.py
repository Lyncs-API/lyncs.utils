"Tools for functions"

__all__ = [
    "is_keyword",
    "get_varnames",
    "has_args",
    "has_kwargs",
    "apply_annotations",
    "select_kwargs",
    "spy",
]

from functools import partial, wraps
from logging import debug
import re
import inspect

KEYWORD = re.compile("[A-Za-z_][A-Za-z0-9_]*")


def is_keyword(key):
    "Whether the given key is a valid function keyword"
    if isinstance(key, str):
        return KEYWORD.fullmatch(key)
    return False


def get_varnames(func):
    "Returns the list of varnames of the function"

    try:
        return func.__code__.co_varnames[: func.__code__.co_argcount]
    except AttributeError:
        return ()


def get_func(obj):
    "Finds the actual function of a callable object"

    if not callable(obj) or hasattr(obj, "__code__"):
        return obj

    # Class
    if isinstance(obj, type):
        new = getattr(obj, "__new__", None)
        if new != object.__new__:
            return new
        return getattr(obj, "__init__", new)

    # partial
    if isinstance(obj, partial):
        return get_func(obj.func)

    # instance or nothing
    return getattr(obj, "__call__", obj)


def has_args(func):
    "Whether the function has *args."

    func = get_func(func)
    try:
        return bool(func.__code__.co_flags & 0x04)
    except AttributeError as err:
        if callable(func):
            return False
        raise TypeError(f"Expected a function. Got {type(func)}") from err


def has_kwargs(func):
    "Whether the function has **kwargs."

    func = get_func(func)
    try:
        return bool(func.__code__.co_flags & 0x08)
    except AttributeError as err:
        if callable(func):
            return False
        raise TypeError(f"Expected a function. Got {type(func)}") from err


def apply_annotations(func, *args, _caller=(lambda fnc, val: fnc(val)), **kwargs):
    """Applies the annotations of the func arguments to the respective *args, **kwargs.

    Parameters:
    -----------
    _caller: function
        How to apply the annotation on the argument. By default the annotation is called
        against the argument: `arg = annotation(arg)`. More precisely _caller is used as
        `arg = _caller(annotation, arg)`.
    """

    annotations = getattr(func, "__annotations__", {})
    annotations = tuple((key, val) for key, val in annotations.items() if callable(val))

    if not annotations:
        return args, kwargs

    args = list(args)
    varnames = get_varnames(func)
    for key, val in annotations:
        if key in kwargs:
            kwargs[key] = _caller(val, kwargs[key])
        elif key in varnames:
            idx = varnames.index(key)
            if idx < len(args):
                args[idx] = _caller(val, args[idx])

    return tuple(args), kwargs


def select_kwargs(func, *args, **kwargs):
    "The function is called by passing the args and ONLY the compatible kwargs"

    if has_kwargs(func):
        varnames = get_varnames(func)[: len(args)]
        kwargs = {key: val for key, val in kwargs.items() if key not in varnames}
        return func(*args, **kwargs)

    varnames = get_varnames(func)[len(args) :]
    kwargs = {key: val for key, val in kwargs.items() if key in varnames}
    return func(*args, **kwargs)


def called_as_decorator():
    "Returns if the current function has been called as a decorator"
    lines = inspect.stack(context=2)[1].code_context
    return any(line.strip().startswith("@") for line in lines)


def spy(fnc):
    """
    Decorator that will log debug information when the function is called.
    It requires the default logger to be set to debug level.

    ```
    import logging
    logging.getLogger().setLevel(level=logging.DEBUG)
    ```
    """

    @wraps(fnc)
    def wrapper(*args, **kwargs):
        out = fnc(*args, **kwargs)
        debug(f"{fnc.__name__}({args}, {kwargs}) = {out}")
        return out

    return wrapper
