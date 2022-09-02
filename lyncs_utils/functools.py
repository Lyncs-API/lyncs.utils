"Tools for functions"

__all__ = [
    "is_keyword",
    "get_docstring",
    "get_varnames",
    "has_args",
    "has_kwargs",
    "get_defaults",
    "get_annotations",
    "apply_annotations",
    "select_kwargs",
    "spy",
    "clickit",
]

from collections.abc import Sequence
from dataclasses import _MISSING_TYPE
from functools import partial, wraps
from logging import debug
import re
import inspect
from .extensions import raiseif

try:
    import click
except ImportError as _err:
    click = _err

KEYWORD = re.compile("[A-Za-z_][A-Za-z0-9_]*")


def is_keyword(key):
    "Whether the given key is a valid function keyword"
    if isinstance(key, str):
        return KEYWORD.fullmatch(key)
    return False


def get_docstring(func):
    "Returns the docstring of a function or a class"
    doc = getattr(func, "__doc__", "") or ""
    # Getting recursively the doc of all parents classes
    for cls in set(getattr(func, "__mro__", ())):
        if cls in (func, object):
            continue
        tmp = getattr(cls, "__doc__", "")
        if tmp:
            doc += f"\n\n# Documentation of {cls.__name__}\n{tmp}"
    return doc


def get_varnames(func):
    "Returns the list of varnames of the function"
    if hasattr(func, "__code__"):
        return func.__code__.co_varnames[: func.__code__.co_argcount]
    if issubclass(type(func), type):
        if hasattr(func, "__dataclass_fields__"):
            return tuple(
                key for key, val in func.__dataclass_fields__.items() if val.init
            )
        if hasattr(func, "__init__"):
            return get_varnames(func.__init__)
        if hasattr(func, "__new__"):
            return get_varnames(func.__new__)
    if hasattr(func, "__call__"):
        return get_varnames(func.__call__)
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


def get_defaults(func):
    "Returns default values of a function/class"
    if hasattr(func, "__defaults__"):
        keys = get_varnames(func)
        vals = func.__defaults__
        return dict(zip(keys[-len(vals) :], vals))
    if issubclass(type(func), type):
        if hasattr(func, "__dataclass_fields__"):
            return {
                key: val.default
                for key, val in func.__dataclass_fields__.items()
                if val.init and not isinstance(val.default, _MISSING_TYPE)
            }
        if hasattr(func, "__init__"):
            return get_defaults(func.__init__)
        if hasattr(func, "__new__"):
            return get_defaults(func.__new__)
    if hasattr(func, "__call__"):
        return get_defaults(func.__call__)
    return {}


def get_annotations(func):
    "Returns annotations of a function/class"
    if issubclass(type(func), type):
        if hasattr(func, "__dataclass_fields__"):
            return {
                key: val.type
                for key, val in func.__dataclass_fields__.items()
                if val.init and not isinstance(val.type, _MISSING_TYPE)
            }
        if hasattr(func, "__init__"):
            return get_annotations(func.__init__)
        if hasattr(func, "__new__"):
            return get_annotations(func.__new__)
    if hasattr(func, "__call__"):
        if hasattr(func.__call__, "__annotations__"):
            return func.__call__.__annotations__
    if hasattr(func, "__annotations__"):
        return func.__annotations__
    return {}


def apply_annotations(func, *args, _caller=(lambda fnc, val: fnc(val)), **kwargs):
    """Applies the annotations of the func arguments to the respective *args, **kwargs.

    Parameters:
    -----------
    _caller: function
        How to apply the annotation on the argument. By default the annotation is called
        against the argument: `arg = annotation(arg)`. More precisely _caller is used as
        `arg = _caller(annotation, arg)`.
    """

    annotations = get_annotations(func)
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

    annotations = get_annotations(func)
    defaults = get_defaults(func)
    varnames = get_varnames(func)

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

    doc = get_docstring(func).split("\n")
    # comments are all lines starting with "#"
    comments = tuple(line.strip(" #") for line in doc if line.lstrip().startswith("#"))
    doc = "\n".join(tuple(line for line in doc if not line.lstrip().startswith("#")))
    func.__doc__ = doc.strip()

    def get_help(var):
        "Checking in __doc__ for lines that start with {var}:"
        for line in comments:
            if line.startswith(var + ":"):
                return line[len(var) + 1 :].strip()
        return "NODOC"

    for var in varnames:
        value = defaults.get(var, None)
        func = click.option(
            get_key(var),
            required=var not in defaults,
            default=value,
            multiple=is_multiple(var),
            type=get_type(var),
            help=get_help(var),
        )(func)

    return func


def foo(*_, **__):
    "A function that does nothing"
    return
