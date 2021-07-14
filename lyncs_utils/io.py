"""
Tools for I/O
"""

__all__ = [
    "open_file",
    "read",
    "write",
    "read_struct",
    "file_size",
    "to_path",
]

import os
import struct
from functools import wraps, partial
from io import IOBase
from pathlib import Path
from tempfile import _TemporaryFileWrapper

FileLike = (
    IOBase,
    _TemporaryFileWrapper,
)


def open_file(fnc=None, arg=0, flag="rb"):
    "Decorator that returns a wrapper that opens the file (at position arg) if needed"

    if not fnc:
        return partial(open_file, arg=arg, flag=flag)

    @wraps(fnc)
    def wrapped(*args, **kwargs):
        if len(args) <= arg:
            raise ValueError(f"filename not found at position {arg}")
        if isinstance(args[arg], FileLike):
            return fnc(*args, **kwargs)
        args = list(args)
        with open(args[arg], flag) as fptr:
            args[arg] = fptr
            return fnc(*args, **kwargs)

    return wrapped


@open_file
def read(_fp, size=None):
    "Reads data from file"
    if size is None:
        return _fp.read()
    return _fp.read(size)


@open_file(flag="wb")
def write(_fp, data):
    "Writes data to file"
    _fp.write(data)


def read_struct(_fp, format):
    "Reads struct from file of given format (see struct)"
    data = read(_fp, struct.calcsize(format))
    data = struct.unpack_from(format, data)
    return data


@open_file
def file_size(_fp):
    "Returns the file size"
    offset = _fp.tell()
    _fp.seek(0, os.SEEK_END)
    fsize = _fp.tell()
    _fp.seek(offset)
    return fsize


def to_path(filename):
    "Returns a Path from the filename"
    if isinstance(filename, FileLike):
        filename = filename.name
    if isinstance(filename, bytes):
        filename = filename.decode()
    return Path(filename)
