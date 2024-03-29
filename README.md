# Collection of generic-purpose and stand-alone functions

[![python](https://img.shields.io/pypi/pyversions/lyncs_utils.svg?logo=python&logoColor=white)](https://pypi.org/project/lyncs_utils/)
[![pypi](https://img.shields.io/pypi/v/lyncs_utils.svg?logo=python&logoColor=white)](https://pypi.org/project/lyncs_utils/)
[![license](https://img.shields.io/github/license/Lyncs-API/lyncs.utils?logo=github&logoColor=white)](https://github.com/Lyncs-API/lyncs.utils/blob/master/LICENSE)
[![build & test](https://img.shields.io/github/actions/workflow/status/Lyncs-API/lyncs.utils/ci_cd.yml?logo=github&logoColor=white&branch=master)](https://github.com/Lyncs-API/lyncs.utils/actions)
[![codecov](https://img.shields.io/codecov/c/github/Lyncs-API/lyncs.utils?logo=codecov&logoColor=white)](https://codecov.io/gh/Lyncs-API/lyncs.utils)
[![pylint](https://img.shields.io/badge/pylint%20score-9.4%2F10-green?logo=python&logoColor=white)](http://pylint.pycqa.org/)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg?logo=codefactor&logoColor=white)](https://github.com/ambv/black)

This package provides a collection of generic-purpose and stand-alone functions that are of common use.
A characteristic of the package is to be lightweight and dependencies-free.
Please, consider its installation if any of the following function can be of use in your project.
Any addition to the list is very welcome!


## Installation

The package can be installed via `pip`:

```
pip install [--user] lyncs_utils
```


## Documentation

Here the list of functions implemented with a short description. Use `help(lyncs_utils)` for more details.


### Class Utils

Functions and decorator for classes. See `lyncs_utils.class_utils`.

- `@add_to`: Decorator for adding a function to a class
- `@add_kwargs_of(fnc)`: Decorator for adding kwargs of a function to another
- `@compute_property`: Decorator for computing a property once and cache the result
- `@static_property`: Decorator for a static property (like staticmethod)
- `@class_property`: Decorator for a class property (like classmethod)
- `call_method(obj, fnc, *args, **kwargs)`: Calls a method of the obj.
- `default_repr_pretty`: Default method to use for _repr_pretty_
- `default(value, type=None, doc=None)`: Attribute with default value and optional type checking
- `methodof(self, func)`: Returns the class where method has been defined
- `@before_super`: Decorator that call method from super before executing for self
- `@after_super`: Decorator that call method from super after executing for self

### Extensions

Extensions of Python standard functions. See `lyncs_utils.extensions`.

- `count`: See itertools.count. Adds __call__ method
- `redirect_stdout`: See contextlib.redirect_stdout. Now, it redirects stdout also from C
- `keydefaultdict`: A defaultdict that passes the key to the factory
- `FreezableDict`: Extension of dict. A dictionary that can be frozen at any moment.
- `cache`: Enables functools.cache for all versions of Python
- `lazy_import(module)`: Lazy import for modules
- `setitems(arr, vals)`: Sets items of an iterable object
- `commonsuffix(words)`: Finds common suffix in words
- `@raiseif(fail, error)`: Decorator that raises `error` if `fail` is `True`
- `RaiseOnUse(error)`: Class instance that raises `error` when used
- `ndict`: A dictionally that supports numerical operations

### Math

Math utils. See `lyncs_utils.math`.

- `prod(arr)`:  Enables math.prod for all versions of Python
- `sign(n)`:  Sign of a number
- `iscomplex(n)`: If n is complex
- `isclose(a,b,warn_tol=None,**)`: math.isclose with support for complex and warning tol
- `factors(n)`: Returns the list of factors of n
- `prime_factors(n)`: Returns the list of prime factors of n

### Functools

Tools for functions. See `lyncs_utils.functools`.

- `is_keyword(key)`: Whether key can be used as a function keyword
- `get_docstring(fnc)`: Returns the docstring of a function or class
- `get_varnames(fnc)`: Returns the list of varnames of the function
- `has_args(fnc)`: Whether the function uses *args
- `has_kwargs(fnc)`: Whether the function uses **kwargs
- `get_defaults(fnc)`: Returns the dict of default values of the function
- `get_annotations(fnc)`: Returns the dict of annotations of the function
- `apply_annotations(fnc, *args, **kwargs)`: Applies the annotations of fnc to the respective *args, **kwargs
- `select_kwargs(fnc, *args, **kwargs)`: Calls fnc passing *args and ONLY the applicable **kwargs
- `@spy`: Decorator that will log debug information when the function is called
- `@clickit`: Decorator that adds click.option for any function argument

### Context Managers

Functionalities using `contextmanager` by `contextlib` meant to be called within a with-statement.
See `lyncs_utils.contextlib`.

- `setting(obj, attr, value, default=None)`: Context manager that temporaly sets an attribute of an object.
- `updating(obj, attr, value, default=None)`: Context manager that temporaly sets an item of an object.

### I/O

Tools for I/O. See `lyncs_utils.io`.

- `@open_file`: Decorator that opens the file (if needed) before calling the function
- `read(fname/fp)`: Reads data from file
- `write(fname/fp)`: Writes data into the file
- `read_struct(fname/fp, format)`: Reads a structure from file
- `write_struct(fname/fp, format, *data)`: Writes a structure from file
- `file_size(fname/fp)`: Returns the file size
- `to_path(fname/fp)`: Returns a Path object to the file
- `dbdict`: Dictionary-like class for storing dictionaries in a database

### Logical

Functions returning or manipulating logical values (boolean). See `lyncs_utils.logical`.

- `single_true(iter)`: Whether one and only one element of the list is True
- `isiterable(obj)`: Whether the object is iteragle or not
- `interactive()`: Whether Python has been run in interactive mode
- `version(num, pkg)`: Compares the version number to the one of a package

### Numpy

Functions returning or manipulating Numpy arrays (available with `lyncs[numpy]`)

- `outer(A,B)`: outer product, alias of `numpy.kron`.
- `gamma_matrices(dim, euclidean=True)`: returns n-dimensional gamma matrices
- `su_generators(N)`: returns NxN generators of su(N)

### Itertools

Functions for iterable objects

- `first(it)`: first element of an iterable
- `last(it)`: last element of an iterable
- `indexes(it,val)`: indexes of occurances of a value in an iterable
- `keys(dict)`: calls keys, if available, or dict.keys
- `values(dict)`: calls values, if available, or dict.values
- `items(dict)`: calls items, if available, or dict.items
- `dictmap(fnc, dict)`: map for dictionaries
- `dictzip(*dicts, fill=True, default=None)`: zip for dictionaries
- `flat_dict(dict, sep=None, base=())`: flat nested dictionaries into a single dict
- `nest_dict(dict, sep=None)`: turns a flat dictionaries into a nested dict
- `allclose(left, right, **)`: applies isclose recursively to iterable objects
- `compact_indexes(ids)`: compats list of integers into ranges where possible

### Pytest

Functions tu use within `pytest`, to be impoted from `lyncs_utils.pytest`

- `DynParam(fnc)`: Dynamic params based on the test function
- `GetMark(map, def)`: Dynamic params based on the marks of the test function
- `lazy_fixture(str)`: Use a fixture as one of the values passed in @pytest.mark.parametrize