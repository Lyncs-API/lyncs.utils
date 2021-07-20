import tempfile
from pathlib import Path
from lyncs_utils.io import *


def test_read():
    data = b"A very random string 123456"
    with tempfile.NamedTemporaryFile() as fp:
        filename = fp.name
        fp.write(data)
        fp.seek(0)
        data0 = fp.read()
        fp.seek(0)
        data1 = read(fp)
        data2 = read(filename, len(data))
        assert data0 == data1
        assert data0 == data2


def test_write():
    data = b"A very random string 123456"
    with tempfile.NamedTemporaryFile() as fp:
        filename = fp.name
        fp.write(data)
        fp.seek(0)
        data0 = fp.read()
        fp.seek(0)
        write(fp, data)
        fp.seek(0)
        data1 = fp.read()
        fp.seek(0)
        write(filename, data)
        fp.seek(0)
        data2 = fp.read()
        assert data0 == data1
        assert data0 == data2


def test_read_struct():
    data = b"A very random string 123456"
    with tempfile.NamedTemporaryFile() as fp:
        filename = fp.name
        fp.write(data)
        fp.seek(0)
        struct = read_struct(fp, "%dc" % len(data))
        assert data == b"".join(struct)
        struct = read_struct(filename, "%dc" % len(data))
        assert data == b"".join(struct)


def test_write_struct():
    data = b"A very random string 123456"
    with tempfile.NamedTemporaryFile() as fp:
        filename = fp.name
        write_struct(fp, "%ds" % len(data), data)
        fp.seek(0)
        struct = read_struct(fp, "%ds" % len(data))
        assert data == struct[0]
        struct = read_struct(filename, "%ds" % len(data))
        assert data == struct[0]


def test_file_size():
    data = b"A very random string 123456"
    with tempfile.NamedTemporaryFile() as fp:
        filename = fp.name
        fp.write(data)
        assert file_size(fp) == len(data)
        assert file_size(filename) == len(data)


def test_to_path():
    with tempfile.NamedTemporaryFile() as fp:
        filename = fp.name
        assert to_path(fp) == Path(filename)
        assert to_path(filename) == Path(filename)
        assert to_path(bytes(filename, "utf-8")) == Path(filename)
