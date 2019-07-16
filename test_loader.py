import loader


def test_loader_simple():
    path = 'data/test_recordings/'
    l = loader.Loader(path=path)
    rec = l.get()
    assert len(rec) == 2