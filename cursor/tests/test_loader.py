from cursor.loader import Loader
from cursor.data import DataDirHandler

import pytest


def test_loader_simple():
    dir = DataDirHandler().test_recordings()
    ll = Loader(directory=dir)

    rec = ll.all_collections()
    assert len(rec) == 2


def test_loader_keys():
    dir = DataDirHandler().test_recordings()
    ll = Loader(directory=dir)
    rec = ll.keys()
    assert len(rec) == 3


def test_loader_index_too_high_exception():
    dir = DataDirHandler().test_recordings()
    ll = Loader(directory=dir)
    with pytest.raises(IndexError):
        ll.single(100)


def test_loader_single():
    dir = DataDirHandler().test_recordings()
    ll = Loader(directory=dir)
    path = ll.single(0)
    assert len(path) > 0


def test_loader_isfileandjson():
    with pytest.raises(AssertionError):
        Loader.is_file_and_json("hey")


def test_loader_limit_files():
    dir = DataDirHandler().test_recordings()
    l1 = Loader(directory=dir)
    l2 = Loader(directory=dir, limit_files=1)

    assert len(l2) == 1
    assert len(l1) > len(l2)
