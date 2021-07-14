# Collection of generic-purpose and stand-alone functions

[![python](https://img.shields.io/pypi/pyversions/lyncs_utils.svg?logo=python&logoColor=white)](https://pypi.org/project/lyncs_utils/)
[![pypi](https://img.shields.io/pypi/v/lyncs_utils.svg?logo=python&logoColor=white)](https://pypi.org/project/lyncs_utils/)
[![license](https://img.shields.io/github/license/Lyncs-API/lyncs.utils?logo=github&logoColor=white)](https://github.com/Lyncs-API/lyncs.utils/blob/master/LICENSE)
[![build & test](https://img.shields.io/github/workflow/status/Lyncs-API/lyncs.utils/build%20&%20test?logo=github&logoColor=white)](https://github.com/Lyncs-API/lyncs.utils/actions)
[![codecov](https://img.shields.io/codecov/c/github/Lyncs-API/lyncs.utils?logo=codecov&logoColor=white)](https://codecov.io/gh/Lyncs-API/lyncs.utils)
[![pylint](https://img.shields.io/badge/pylint%20score-9.6%2F10-green?logo=python&logoColor=white)](http://pylint.pycqa.org/)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg?logo=codefactor&logoColor=white)](https://github.com/ambv/black)

This package provides a collection of generic-purpose and stand-alone functions that are used in multiple places of Lyncs.


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

### Extensions

Extensions of Python standard functions. See `lyncs_utils.extensions`.

- `count`: See itertools.count. Adds __call__ method
- `redirect_stdout`: See contextlib.redirect_stdout. Now, it redirects stdout also from C
- `FreezableDict`: Extension of dict. A dictionary that can be frozen at any moment.
- `cache`: Enables functools.cache for all versions of Python

### Factors

Factorization utils. See `lyncs_utils.factors`.

- `prod(arr)`:  Enables math.prod for all versions of Python
- `factors(n)`: Returns the list of factors of n
- `prime_factors(n)`: Returns the list of prime factors of n

### Functools

Tools for functions. See `lyncs_utils.functools`.

- `is_keyword(key)`: Whether key can be used as a function keyword
- `get_varnames(fnc)`: Returns the list of varnames of the function
- `has_args(fnc)`: Whether the function uses *args
- `has_kwargs(fnc)`: Whether the function uses **kwargs
- `apply_annotations(fnc, *args, **kwargs)`: Applies the annotations of fnc to the respective *args, **kwargs
- `select_kwargs(fnc, *args, **kwargs)`: Calls fnc passing *args and ONLY the applicable **kwargs

### I/O

Tools for I/O. See `lyncs_utils.io`.

- `@open_file`: Decorator that opens the file (if needed) before calling the function
- `read(fname/fp)`: Reads data from file
- `write(fname/fp)`: Writes data into the file
- `read_struct(fname/fp, format)`: Reads a structure from file
- `file_size(fname/fp)`: Returns the file size
- `to_path(fname/fp)`: Reaturns a Path object to the file

### Logical

Functions returning or manipulating logical values (boolean). See `lyncs_utils.logical`.

- `single_true(iter)`: Whether one and only one element of the list is True
- `isiterable(obj)`: Whether the object is iteragle or not
- `interactive()`: Whether Python has been run in interactive mode
- `version(num, pkg)`: Compares the version number to the one of a package
