from cursor.load.loader import Loader
from cursor.data import DataDirHandler
from cursor.properties import Property

import pytest


def test_loader_simple():
    dir = DataDirHandler().test_recordings()
    ll = Loader(directory=dir)

    rec = ll.all_collections()
    assert len(rec) == 3


def test_loader_keys():
    dir = DataDirHandler().test_recordings()
    ll = Loader(directory=dir, load_keys=True)
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


def test_loader_single_file():
    dir = DataDirHandler().test_recordings()
    single_file = dir / "1565088885.39372_suffix.json"
    ll = Loader()
    ll.load_file(single_file)
    # that specific file has 18 paths
    assert len(ll.all_paths()) == 18


def test_loader_color_recording():
    dir = DataDirHandler().test_recordings()
    single_file = dir / "1664178785.14013_with_colors.json"
    ll = Loader()
    ll.load_file(single_file)
    assert len(ll.all_paths()) == 7
    for pa in ll.all_paths():
        for p in pa:
            assert p.properties[Property.COLOR] is not None


def test_loader_limit_files():
    dir = DataDirHandler().test_recordings()
    l1 = Loader(directory=dir)
    l2 = Loader(directory=dir, limit_files=1)

    assert len(l2) == 1
    assert len(l1) > len(l2)
