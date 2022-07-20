"Tools for functions"

__all__ = [
    "is_keyword",
    "get_varnames",
    "has_args",
    "has_kwargs",
    "apply_annotations",
    "select_kwargs",
    "spy",
    "clickit",
]

from collections.abc import Sequence
from functools import partial, wraps
from logging import debug
import re
import inspect
from .extensions import raiseif

try:
    import click
except ImportError as err:
    click = err

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


@raiseif(isinstance(click, Exception), click)
def clickit(func):
    "Decorator that turns any function argument to click.option"
    if has_args(func):
        raise NotImplementedError("TODO: investigate how to treat `*args`")

    annotations = getattr(func, "__annotations__", {})
    defaults = getattr(func, "__defaults__", {})
    varnames = get_varnames(func)
    nargs = len(varnames) - len(defaults)

    def get_key(var):
        "Returns a key for the variable"
        out = var.replace("_", "-")
        if get_type(var) == bool:
            if out.startswith("with-"):
                return f"--{out}/--without-{out[5:]}"
            return f"--{out}/--no-{out}"
        return f"--{out}"

    def is_multiple(var):
        "Multiple variables must be typed Sequence"
        return getattr(annotations.get(var, None), "__origin__", None) is Sequence

    def get_type(var):
        "Returns the type of var"
        if var not in annotations:
            return None
        tpe = annotations[var]
        if is_multiple(var):
            args = getattr(tpe, "__args__", (None,))
            if len(args) > 1:
                return args
            return args[0]
        return tpe

    if func.__doc__:
        doc = func.__doc__.split("\n")
        # comments are all lines starting with "#"
        comments = tuple(
            line.strip(" #") for line in doc if line.lstrip().startswith("#")
        )
        doc = "\n".join(
            tuple(line for line in doc if not line.lstrip().startswith("#"))
        )
        func.__doc__ = doc
    else:
        comments = ()

    def get_help(var):
        "Checking in __doc__ for lines that start with {var}:"
        for line in comments:
            if line.startswith(var + ":"):
                return line[len(var) + 1 :].strip()
        return ""

    for i, var in enumerate(varnames):
        value = None if i < nargs else defaults[i - nargs]
        func = click.option(
            get_key(var),
            required=i < nargs,
            default=value,
            multiple=is_multiple(var),
            type=get_type(var),
            help=get_help(var),
        )(func)

    return func
