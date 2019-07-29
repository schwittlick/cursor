from ..cursor import loader

import os

def test_loader_simple():
    path = 'tests/data/test_recordings/'
    l = loader.Loader(directory=os.path.abspath(path))
    rec = l.single(0)
    assert len(rec) == 8

    l2 = loader.Loader(directory=os.path.abspath(path))

    rec2 = l2.all()
    assert len(rec2) == 1