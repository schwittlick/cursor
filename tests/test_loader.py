from ..cursor import loader

import os
import pytest

def test_loader_simple():
    path = './data/test_recordings/'
    l = loader.Loader(directory=os.path.abspath(path))
    rec = l.single(0)
    assert len(rec) == 8

    l2 = loader.Loader(directory=os.path.abspath(path))

    rec2 = l2.all()
    assert len(rec2) == 2

def test_loader_keys():
    path = './data/test_recordings/'
    l = loader.Loader(directory=os.path.abspath(path))
    rec = l.keys()
    assert len(rec) == 6

def test_loader_index_too_high_exception():
    path = './data/test_recordings/'
    l = loader.Loader(directory=os.path.abspath(path))
    with pytest.raises(IndexError):
        l.single(100)

def test_loader_isfileandjson():
    l = loader.Loader(directory=os.path.abspath('.'))
    l.is_file_and_json('hey')


