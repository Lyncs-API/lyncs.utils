import pytest
import tempfile
from pathlib import Path
from lyncs_utils.io import *
from lyncs_utils import first


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


def test_dbdict():
    with tempfile.NamedTemporaryFile() as fp:
        filename = fp.name
        tmp = dbdict(filename=filename)

        tmp["foo"] = "bar"
        assert "foo" in tmp
        assert tmp["foo"] == "bar"
        assert "bar" not in tmp
        assert len(tmp) == 1
        assert first(tmp) == "foo"

        tmp["foo"] = "bar2"
        assert tmp["foo"] == "bar2"

        tmp2 = dbdict({"bar": "foo"}, filename=filename)
        assert "foo" in tmp2
        assert "bar" in tmp

        del tmp["foo"]
        assert "foo" not in tmp
        assert "foo" not in tmp2

        with pytest.raises(KeyError):
            del tmp["foo"]
