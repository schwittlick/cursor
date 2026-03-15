from cursor.collection import Collection
from cursor.load import KeyPress
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


def test_loader_len():
    ll = Loader(directory=get_test_recordings_path())
    assert len(ll) == 3


def test_loader_all_paths():
    ll = Loader(directory=get_test_recordings_path())
    all_paths = ll.all_paths()
    assert isinstance(all_paths, Collection)
    expected = sum(len(c) for c in ll.all_collections())
    assert len(all_paths) == expected


def test_loader_limit_files_by_name():
    stem = "1565088885.39372_suffix"
    ll = Loader(directory=get_test_recordings_path(), limit_files=[stem])
    assert len(ll) == 1
    assert len(ll.all_paths()) == 18


def test_loader_load_file_with_keys():
    single_file = get_test_recordings_path() / "1565088885.39372_suffix.json"
    ll = Loader()
    ll.load_file(single_file, load_keys=True)
    assert isinstance(ll.keys(), list)
    assert all(isinstance(k, KeyPress) for k in ll.keys())


def test_loader_is_file_and_json():
    recordings_path = get_test_recordings_path()
    assert Loader.is_file_and_json(recordings_path / "1565088885.39372_suffix.json") is True
    assert Loader.is_file_and_json(recordings_path) is False  # directory, not a file
    assert Loader.is_file_and_json(recordings_path / "nonexistent.json") is False


def test_loader_invalid_file_stem(tmp_path):
    invalid_file = tmp_path / "nounderscorehere.json"
    invalid_file.write_text("{}")
    ll = Loader()
    with pytest.raises(AssertionError):
        ll.load_file(invalid_file)


def test_loader_empty_directory(tmp_path):
    ll = Loader(directory=tmp_path)
    assert len(ll) == 0


def test_loader_legacy_key_format(tmp_path):
    from cursor.load.compress import JsonCompressor

    # 2-element key tuples are the legacy format (no is_down field)
    data = {
        "mouse": {"timestamp": 1234567890.0, "paths": []},
        "keys": [["a", 0.5]],
    }
    compressed = JsonCompressor().json_zip(data)
    file_path = tmp_path / "1234567890.0_test.json"
    file_path.write_text(str(compressed))

    ll = Loader()
    ll.load_file(file_path, load_keys=True)
    assert len(ll.keys()) == 1
    assert ll.keys()[0].key == "a"
    assert ll.keys()[0].timestamp == 0.5
    assert ll.keys()[0].is_down is True  # default when missing
