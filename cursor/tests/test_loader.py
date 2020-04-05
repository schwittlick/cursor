from cursor import loader
from cursor import data

import pytest


def test_loader_simple():
    dir = data.DataPathHandler().test_recordings()
    ll = loader.Loader(directory=dir)

    rec = ll.all_collections()
    assert len(rec) == 4


def test_loader_keys():
    dir = data.DataPathHandler().test_recordings()
    ll = loader.Loader(directory=dir)
    rec = ll.keys()
    assert len(rec) == 6


def test_loader_index_too_high_exception():
    dir = data.DataPathHandler().test_recordings()
    ll = loader.Loader(directory=dir)
    with pytest.raises(IndexError):
        ll.single(100)


def test_loader_single():
    dir = data.DataPathHandler().test_recordings()
    ll = loader.Loader(directory=dir)
    path = ll.single(0)
    assert len(path) > 0


def test_loader_isfileandjson():
    is1 = loader.Loader.is_file_and_json("hey")
    assert not is1
    # TODO: test for true


def test_loader_limit_files():
    dir = data.DataPathHandler().test_recordings()
    l1 = loader.Loader(directory=dir)
    l2 = loader.Loader(directory=dir, limit_files=1)

    assert len(l2) == 1
    assert len(l1) > len(l2)
