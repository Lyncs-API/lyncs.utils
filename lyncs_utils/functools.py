"Tools for functions"

__all__ = [
    "get_varnames",
    "has_args",
    "has_kwargs",
    "apply_annotations",
    "select_kwargs",
]


def get_varnames(func):
    "Returns the list of varnames of the function"

    try:
        return func.__code__.co_varnames[: func.__code__.co_argcount]
    except AttributeError:
        return ()


def has_args(func):
    "Whether the function has *args."

    if isinstance(func, type):
        new = getattr(func, "__new__", None)
        if new != object.__new__:
            return has_args(new)
        return has_args(getattr(func, "__init__", new))

    try:
        return bool(func.__code__.co_flags & 0x04)
    except AttributeError as err:
        if callable(func):
            return False
        raise TypeError(f"Expected a function. Got {type(func)}") from err


def has_kwargs(func):
    "Whether the function has **kwargs."

    if isinstance(func, type):
        new = getattr(func, "__new__", None)
        if new != object.__new__:
            return has_kwargs(new)
        return has_kwargs(getattr(func, "__init__", new))

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