import loader


def test_loader_simple():
    path = 'data/test_recordings/'
    l = loader.Loader(path=path)
    rec = l.single(0)
    assert len(rec) == 11

    l2 = loader.Loader(path=path)

    rec2 = l2.all()
    assert len(rec2) == 2