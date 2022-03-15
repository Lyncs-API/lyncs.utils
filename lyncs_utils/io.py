"""
Tools for I/O
"""

__all__ = [
    "fopen",
    "open_file",
    "read",
    "write",
    "read_struct",
    "write_struct",
    "file_size",
    "to_path",
    "dbdict",
]

import pickle
import os
import struct
from contextlib import contextmanager
from functools import wraps, partial
from io import IOBase
from pathlib import Path
from tempfile import _TemporaryFileWrapper
from collections.abc import MutableMapping
from sqlite3 import dbapi2 as sqlite


FileLike = (
    IOBase,
    _TemporaryFileWrapper,
)


@contextmanager
def fopen(_fp, mode="rb", **kwargs):
    "Flexible open function, that opens the file if needed"
    if isinstance(_fp, FileLike):
        yield _fp
    else:
        with open(_fp, mode=mode, **kwargs) as fptr:
            yield fptr


def open_file(fnc=None, arg=0, mode="rb", flag=None, **kwargs_open):
    "Decorator that returns a wrapper that opens the file (at position arg) if needed"

    if flag is not None:
        # Alias of mode, deprecated
        mode = flag

    if fnc is None:
        return partial(open_file, arg=arg, mode=mode, **kwargs_open)

    @wraps(fnc)
    def wrapped(*args, **kwargs):
        if len(args) <= arg:
            raise ValueError(f"filename not found at position {arg}")
        args = list(args)
        with fopen(args[arg], mode=mode, **kwargs_open) as fptr:
            args[arg] = fptr
            return fnc(*args, **kwargs)

    return wrapped


@open_file
def read(_fp, size=None):
    "Reads data from file"
    if size is None:
        return _fp.read()
    return _fp.read(size)


@open_file(mode="wb")
def write(_fp, data):
    "Writes data to file"
    _fp.write(data)


def read_struct(_fp, fmt):
    "Reads struct from file of given format (see struct)"
    data = read(_fp, struct.calcsize(fmt))
    data = struct.unpack_from(fmt, data)
    return data


def write_struct(_fp, fmt, *data):
    "Writes struct to file of given format (see struct)"
    data = struct.pack(fmt, *data)
    write(_fp, data)


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


class dbdict(MutableMapping):
    """A dictionary-like class for storing dictionaries in a database"""

    def __init__(self, *args, filename="", loads=pickle.loads, dumps=pickle.dumps):
        """
        A dictionary-like class for storing dictionaries in a database

        Parameters
        ----------
        - filename: filename for storing the database,cdefault `.sqlite`
        - loads: serializer for loading, default `pickle.loads`
        - dumps: serializer for dumping, default `pickle.dumps`
        """

        self.filename = filename
        self.dumps = dumps
        self.loads = loads
        if not self.filename.endswith(".sqlite"):
            self.filename += ".sqlite"

        if not os.path.isfile(self.filename):
            self.con = sqlite.connect(self.filename)
            self.con.execute("create table data (key PRIMARY KEY,value)")
        else:
            self.con = sqlite.connect(self.filename)

        if args:
            self.update(*args)

    def __getitem__(self, key):
        row = self.con.execute("select value from data where key=?", (key,)).fetchone()
        if not row:
            raise KeyError
        return self.loads(row[0])

    def __setitem__(self, key, item):
        item = self.dumps(item)
        if self.con.execute("select key from data where key=?", (key,)).fetchone():
            self.con.execute("update data set value=? where key=?", (item, key))
        else:
            self.con.execute("insert into data (key,value) values (?,?)", (key, item))
        self.con.commit()

    def __delitem__(self, key):
        if self.con.execute("select key from data where key=?", (key,)).fetchone():
            self.con.execute("delete from data where key=?", (key,))
            self.con.commit()
        else:
            raise KeyError(f"{key} not in dictonary")

    def __iter__(self):
        # TODO use iterable fetch
        return (row[0] for row in self.con.execute("select key from data").fetchall())

    def __len__(self):
        # TODO find cheaper way
        return len(self.con.execute("select key from data").fetchall())
