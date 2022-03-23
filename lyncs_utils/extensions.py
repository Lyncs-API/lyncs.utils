"""
Extensions of Python standard functions
"""
# pylint: disable=invalid-name

__all__ = [
    "count",
    "redirect_stdout",
    "keydefaultdict",
    "FreezableDict",
    "cache",
    "lazy_import",
    "setitems",
    "commonsuffix",
    "raiseif",
    "RaiseOnUse",
]

import io
import os
import sys
import ctypes
import tempfile
import importlib
from collections import defaultdict
from functools import wraps
from itertools import count as _count
from contextlib import redirect_stdout as _redirect_stdout
from os.path import commonprefix
from .contextlib import setting

try:
    from functools import cache
except ImportError:
    from functools import lru_cache

    cache = lru_cache(maxsize=None)


class count(_count):
    "Extension of itertools.count. Adds __call__ method"

    def __call__(self, num):
        for _ in range(num):
            yield next(self)


def lazy_import(name):
    "Lazy import for modules"
    # Based on: https://stackoverflow.com/questions/42703908/how-do-i-use-importlib-lazyloader
    try:
        return sys.modules[name]
    except KeyError:
        spec = importlib.util.find_spec(name)
        if spec is None:
            raise ImportError(f"Module not found: {name}")
        sys.modules[name] = importlib.util.module_from_spec(spec)
        loader = importlib.util.LazyLoader(spec.loader)
        # Make module with proper locking and get it inserted into sys.modules.
        loader.exec_module(sys.modules[name])
        return sys.modules[name]


def setitems(arr, vals):
    "Sets items of an iterable object"
    size = len(arr)
    if hasattr(vals, "__len__"):
        if len(vals) > size:
            raise ValueError(
                f"Values size ({len(vals)}) larger than array size ({size})"
            )
    else:
        vals = (vals,) * size
    for i, val in enumerate(vals):
        if hasattr(arr[i], "__len__"):
            setitems(arr[i], val)
        else:
            arr[i] = val


def commonsuffix(words):
    "Finds common suffix between list of words"
    reverse = lambda word: word[::-1]
    words = list(map(reverse, words))
    return commonprefix(words)[::-1]


def raiseif(fail, error):
    "Decorator that raises error if condition is satisfied"

    def decorator(fnc):
        if not fail:
            return fnc

        @wraps(fnc)
        def raiser(*args, **kwargs):
            raise error

        return raiser

    return decorator


class RaiseOnUse:
    "Class that raises error if instances are used"
    __slots__ = ("__error__",)

    def __init__(self, error):
        super().__setattr__("__error__", error)

    def _(self, *__, **___):
        raise self.__error__

    __call__ = _
    __getattr__ = _
    __setattr__ = _
    __getitem__ = _
    __setitem__ = _


class redirect_stdout(_redirect_stdout):
    """
    Context manager for temporarily redirecting stdout to another file.
    Additionally to contextlib.redirect_stdout, it redirects stdout also from C.

    >>> with redirect_stdout(sys.stderr):
    ...    print('this is from python')
    ...    os.system('echo this is from echo')
    """

    def __init__(self, new_target):
        super().__init__(new_target)
        self._tmp = None

    @staticmethod
    def cfflush():
        "Flushes the C stdout"
        libc = ctypes.CDLL(None)
        c_stdout = ctypes.c_void_p.in_dll(libc, "stdout")
        libc.fflush(c_stdout)

    def __enter__(self):
        new_target = super().__enter__()
        try:
            fno = new_target.fileno()
        except io.UnsupportedOperation:
            self._tmp = tempfile.TemporaryFile(mode="w+")
            fno = self._tmp.fileno()
            sys.stdout = self._tmp

        self.cfflush()
        self._old_targets.append(os.dup(1))
        os.dup2(fno, 1)

        return sys.stdout

    def __exit__(self, exctype, excinst, exctb):
        self.cfflush()

        if self._tmp:
            self._tmp.flush()
            self._tmp.seek(0, io.SEEK_SET)
            self._new_target.write(self._tmp.read())
            self._tmp.close()

        fno = self._old_targets.pop()
        os.dup2(fno, 1)
        os.close(fno)
        super().__exit__(exctype, excinst, exctb)


class keydefaultdict(defaultdict):
    "A defaultdict that passes the key to the factory as argument"

    def __missing__(self, key):
        with setting(self, "default_factory", lambda: fnc(key)) as fnc:
            return super().__missing__(key)


class FreezableDict(dict):
    """
    Freezable dictionary, a dictionary that can be frozen at any moment with
    the option of either or both not allowing changes or not allowing new keys.
    """

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self._allows_new = True
        self._allows_changes = True
        return self

    @property
    def frozen(self):
        """
        Returns if the current instance is frozen, i.e. cannot be changed anymore.
        To unfreeze it use .copy().
        """
        return not self._allows_new or not self._allows_changes

    @frozen.setter
    def frozen(self, value):
        if value != self.frozen:
            if not value is True:
                raise ValueError(
                    "Frozen can only be changed to True. To unfreeze do a copy."
                )
            self.allows_new = False
            self.allows_changes = False

    @property
    def allows_new(self):
        "Returns if the current instance allows new keys"
        return self._allows_new

    @allows_new.setter
    def allows_new(self, value):
        if value != self.allows_new:
            if not value is False:
                raise ValueError(
                    "Allows_new can only be changed to False. To unfreeze do a copy."
                )
            self._allows_new = value

    @property
    def allows_changes(self):
        "Returns if the current instance allows changes to the values"
        return self._allows_changes

    @allows_changes.setter
    def allows_changes(self, value):
        if value != self.allows_changes:
            if not value is False:
                raise ValueError(
                    "Allows_changes can only be changed to False. To unfreeze do a copy."
                )
            for key, val in self.items():
                if isinstance(val, FreezableDict):
                    self[key] = val.freeze()
            self._allows_changes = value

    def freeze(self, allows_new=False, allows_changes=False):
        "Returns a frozen copy of the dictionary"
        if self.allows_new == allows_new and self.allows_changes == allows_changes:
            return self
        copy = self.copy()
        copy.allows_new = allows_new
        copy.allows_changes = allows_changes
        return copy

    def __delitem__(self, key):
        if self.frozen:
            raise RuntimeError(
                "The dict has been frozen and %s cannot be deleted." % key
            )
        super().__delitem__(key)

    def __setitem__(self, key, val):
        if key in self:
            if not self.allows_changes:
                raise RuntimeError(
                    "The dict has been frozen and %s cannot be changed." % key
                )
        elif not self.allows_new:
            raise RuntimeError("The dict has been frozen and %s cannot be added." % key)
        if not self.allows_changes and isinstance(val, FreezableDict):
            val = val.freeze()
        super().__setitem__(key, val)

    @wraps(dict.copy)
    def copy(self):
        return type(self)(self)

    @wraps(dict.update)
    def update(self, val=None):
        if not val:
            return
        for _k, _v in dict(val).items():
            self[_k] = _v

    @wraps(dict.setdefault)
    def setdefault(self, key, val):
        if key not in self:
            self[key] = val

    @wraps(dict.pop)
    def pop(self, key, val=None):
        if val is not None and key not in self:
            return val
        val = self[key]
        del self[key]
        return val
