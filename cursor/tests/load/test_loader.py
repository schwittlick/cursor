from cursor.load.loader import Loader
from cursor.properties import Property

import pytest

from cursor.tests.fixture import get_test_recordings_path


def test_loader_simple():
    ll = Loader(directory=get_test_recordings_path())

    rec = ll.all_collections()
    assert len(rec) == 3


def test_loader_keys():
    ll = Loader(directory=get_test_recordings_path(), load_keys=True)
    rec = ll.keys()
    assert len(rec) == 3


def test_loader_index_too_high_exception():
    ll = Loader(directory=get_test_recordings_path())
    with pytest.raises(IndexError):
        ll.single(100)


def test_loader_single():
    ll = Loader(directory=get_test_recordings_path())
    path = ll.single(0)
    assert len(path) > 0


def test_loader_single_file():
    single_file = get_test_recordings_path() / "1565088885.39372_suffix.json"
    ll = Loader()
    ll.load_file(single_file)
    # that specific file has 18 paths
    assert len(ll.all_paths()) == 18


def test_loader_color_recording():
    single_file = get_test_recordings_path() / "1664178785.14013_with_colors.json"
    ll = Loader()
    ll.load_file(single_file)
    assert len(ll.all_paths()) == 7
    for pa in ll.all_paths():
        for p in pa:
            assert p.properties[Property.COLOR] is not None


def test_loader_limit_files():
    l1 = Loader(directory=get_test_recordings_path())
    l2 = Loader(directory=get_test_recordings_path(), limit_files=1)

    assert len(l2) == 1
    assert len(l1) > len(l2)
