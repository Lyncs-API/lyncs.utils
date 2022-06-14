"""
Functions and decorator for classes.
"""

__all__ = [
    "add_to",
    "default_repr_pretty",
    "add_parameters_to_doc",
    "add_kwargs_of",
    "compute_property",
    "static_property",
    "staticproperty",
    "class_property",
    "classproperty",
    "call_method",
    "default",
]

from types import MethodType
from copy import copy
from functools import wraps
from inspect import signature, _empty


def add_to(cls):
    "Decorator for adding a function to a class"

    def decorator(fnc):
        tmp = wraps(fnc)(lambda self, *args, **kwargs: fnc(self, *args, **kwargs))
        setattr(cls, tmp.__name__, tmp)
        return fnc

    return decorator


def default_repr_pretty(self, printer, cycle=False):
    """
    Default _repr_pretty_ for lyncs classes
    """

    name = type(self).__name__ + "("
    printer.begin_group(len(name), name)

    found_first = False
    for key, arg in signature(self.__init__).parameters.items():
        if arg.kind in (
            arg.POSITIONAL_ONLY,
            arg.POSITIONAL_OR_KEYWORD,
            arg.KEYWORD_ONLY,
        ):
            try:
                val = getattr(self, key)
            except AttributeError:
                continue
            if isinstance(val, MethodType):
                continue
            try:
                if arg.default == val:
                    continue
            except:
                pass

            if cycle and found_first:
                printer.text(", ...")
                break

            if found_first:
                printer.text(",")
                printer.breakable(" ")
            else:
                found_first = True

            indent = 0
            if (
                arg.kind in [arg.POSITIONAL_OR_KEYWORD, arg.KEYWORD_ONLY]
                and arg.default != _empty
            ):
                indent = len(key) + 1
                printer.text(key + "=")

            if hasattr(val, "_repr_pretty_"):
                printer.begin_group(indent)
                val._repr_pretty_(printer, cycle=True)
                printer.end_group(indent)
            else:
                printer.text(repr(val))

    printer.end_group(len(name), ")")


def add_parameters_to_doc(doc, doc_params):
    """
    Inserts doc_params in the first empty line after Parameters if possible.
    """
    if not doc:
        return doc

    doc = doc.split("\n")
    found = False
    for i, line in enumerate(doc):
        words = line.split()
        if not found and len(words) == 1 and words[0].startswith("Parameter"):
            found = True
        elif found and not words:
            doc.insert(i, doc_params)
            return "\n".join(doc)

    return "\n".join(doc) + doc_params


def get_parameters_doc(doc):
    """
    Extracts the documentation of the parameters
    """
    if not doc:
        return doc

    found = False
    parameters = []
    for line in doc.split("\n"):
        words = line.split()
        if not found and len(words) == 1 and words[0].startswith("Parameter"):
            found = True
        elif found and words:
            parameters.append(line)
        elif found and not words:
            break

    if found and parameters:
        return "\n".join(parameters[1:])
    return doc


def add_kwargs_of(fnc):
    """
    Decorator for adding kwargs of a function to another
    """

    def decorator(fnc2):
        args = []
        var_kwargs = False
        kwargs = []

        for key, val in signature(fnc2).parameters.items():
            if val.kind == val.POSITIONAL_ONLY or (
                val.kind == val.POSITIONAL_OR_KEYWORD and val.default == _empty
            ):
                args.append(key)
            elif val.kind == val.VAR_POSITIONAL:
                args.append("*" + key)
            elif val.kind == val.VAR_KEYWORD:
                var_kwargs = key
            else:
                kwargs.append((key, val.default))

        assert (
            var_kwargs is not False
        ), "Cannot append kwargs to a function without **kwargs."

        keys = [key for key, val in kwargs]
        kwargs += [
            (key, val.default)
            for key, val in signature(fnc).parameters.items()
            if val.kind in [val.POSITIONAL_OR_KEYWORD, val.KEYWORD_ONLY]
            and val.default != _empty
            and key not in keys
        ]

        args.extend(("%s=%s" % (key, val) for key, val in kwargs))
        args.append("**" + var_kwargs)

        args = ", ".join(args)
        fnc2.__dict__["__wrapped__"] = eval("lambda %s: None" % (args))
        fnc2.__doc__ = add_parameters_to_doc(
            fnc.__doc__, get_parameters_doc(fnc2.__doc__)
        )
        return fnc2

    return decorator


class compute_property(property):
    """
    Computes a property once and store the result in key
    """

    @property
    def key(self):
        "The key of the attribute where to store the result"
        return getattr(self, "_key", "_" + self.fget.__name__)

    @key.setter
    def key(self, value):
        self._key = value

    def __get__(self, obj, owner):
        if obj is None:
            return self
        try:
            return copy(getattr(obj, self.key))
        except AttributeError:
            setattr(obj, self.key, super().__get__(obj, owner))
            return self.__get__(obj, owner)


class static_property:
    "Decorator similar to staticmethod but returns a property"

    def __init__(self, fnc=None):
        self.fget = fnc
        self.__doc__ = getattr(fnc, "__doc__", "")
        self.__name__ = getattr(fnc, "__name__", "")

    def __get__(self, obj, cls=None):
        return self.fget()

    def getter(self, fnc):
        "Sets the getter function"
        self.fget = fnc
        return self


staticproperty = static_property


class class_property:
    "Decorator similar to classmethod but returns a property"

    def __init__(self, fnc=None):
        self.fget = fnc
        self.__doc__ = getattr(fnc, "__doc__", "")
        self.__name__ = getattr(fnc, "__name__", "")

    def __get__(self, obj, cls=None):
        return self.fget(cls)

    def getter(self, fnc):
        "Sets the getter function"
        self.fget = fnc
        return self


classproperty = class_property


class default:
    "Simple attribute with default value and optional type checking"

    def __init__(self, value, type=None, doc=None):
        self.value = value
        self.type = type
        self.__doc__ = doc
        self._key = None

    def var_key(self, cls):
        "Looks for the variable name inside obj"
        if self._key is not None:
            return self._key
        key = "_key_not_found"
        for _k in dir(cls):
            if getattr(cls, _k) is self:
                key = _k
                break
        while hasattr(cls, key):
            key = "_" + key
        self._key = key
        return key

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        return getattr(obj, self.var_key(cls), self.value)

    def __set__(self, obj, value):
        if self.type is not None:
            if not isinstance(value, self.type):
                raise TypeError(f"Expected {self.type} but got {type(value)}")
        setattr(obj, self.var_key(type(obj)), value)


def call_method(self, method, *args, **kwargs):
    "Calls a method of the class. Method can be either a string, function or a method itself"
    if isinstance(method, str):
        return getattr(self, method)(*args, **kwargs)
    if hasattr(method, "__self__") and method.__self__ is self:
        return method(*args, **kwargs)
    if callable(method):
        return method(self, *args, **kwargs)
    raise TypeError(f"Unexpected type {type(method)}")
