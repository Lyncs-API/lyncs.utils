"Tools for functions"

__all__ = [
    "get_varnames",
    "apply_annotations",
]


def get_varnames(func):
    "Returns the list of varnames of the function"

    try:
        return func.__code__.co_varnames[: func.__code__.co_argcount]
    except AttributeError:
        return ()


def apply_annotations(func, *args, **kwargs):
    "Applies the annotations (callable) of func to *args, **kwargs"

    annotations = getattr(func, "__annotations__", {})
    annotations = tuple((key, val) for key, val in annotations.items() if callable(val))

    if not annotations:
        return args, kwargs

    args = list(args)
    varnames = get_varnames(func)
    for key, val in annotations:
        if key in kwargs:
            kwargs[key] = val(kwargs[key])
        elif key in varnames:
            idx = varnames.index(key)
            if idx < len(args):
                args[idx] = val(args[idx])

    return tuple(args), kwargs
