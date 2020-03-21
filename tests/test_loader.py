from ..cursor import loader
from ..cursor import data

import pytest


def test_loader_simple():
    dir = data.DataHandler().test_recordings()
    l = loader.Loader(directory=dir)

    rec = l.all_collections()
    assert len(rec) == 4


def test_compressed_uncompressed():
    dir = data.DataHandler().test_recordings()
    l = loader.Loader(directory=dir)

    s1 = l.single(0)
    s2 = l.single(2)
    s3 = l.single(3)

    eq1 = s2 == s3
    eq2 = s1 == s3

    assert eq1 is True
    assert eq2 is False


def test_loader_keys():
    dir = data.DataHandler().test_recordings()
    l = loader.Loader(directory=dir)
    rec = l.keys()
    assert len(rec) == 6


def test_loader_index_too_high_exception():
    dir = data.DataHandler().test_recordings()
    l = loader.Loader(directory=dir)
    with pytest.raises(IndexError):
        l.single(100)


def test_loader_isfileandjson():
    is1 = loader.Loader.is_file_and_json('hey')
    assert not is1
    # TODO: test for true


def test_loader_limit_files():
    dir = data.DataHandler().test_recordings()
    l1 = loader.Loader(directory=dir)
    l2 = loader.Loader(directory=dir, limit_files=1)

    assert len(l2) == 1
    assert len(l1) > len(l2)

