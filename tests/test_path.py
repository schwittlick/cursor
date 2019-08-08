from ..cursor import path
import pytest


def test_path_empty_start():
    p = path.Path()

    with pytest.raises(IndexError):
        p.start_pos()


def test_path_empty_end():
    p = path.Path()
    with pytest.raises(IndexError):
        p.end_pos()


def test_path_add():
    p = path.Path()

    assert len(p) == 0

    for i in range(100):
        p.add(0, 0, 100)

    assert len(p) == 100


def test_path_clear():
    p = path.Path()
    assert p.empty() == True

    p.add(0, 0, 100)

    assert len(p) == 1

    p.clear()

    assert len(p) == 0

    assert p.empty() == True


def test_path_copy():
    p = path.Path()

    p2 = p.copy()
    assert p is not p2

    p3 = p
    assert p is p3


def test_path_start_end():
    p = path.Path()
    p.add(0, 0, 10000)
    p.add(10, 11, 10000)

    start = p.start_pos()
    assert start.x == 0
    assert start.y == 0

    end = p.end_pos()
    assert end.x == 10
    assert end.y == 11


def test_path_bb():
    p = path.Path()
    p.add(0, 0, 10000)
    p.add(140, 11, 10000)
    p.add(23, 141, 10000)
    p.add(141, 4511, 10000)

    bb = p.bb()
    assert bb[0] == 0
    assert bb[1] == 0
    assert bb[2] == 141
    assert bb[3] == 4511

def test_path_morph():
    p = path.Path()

    p.add(19, 34, 10000)
    p.add(10, 10, 10000)
    p.add(600, 10, 10001)

    pm = p.morph((0, 0), (10, 100))

    start = pm.start_pos()
    end = pm.end_pos()
    assert round(start.x) == 0
    assert round(start.y) == 0
    assert round(end.x) == 10
    assert round(end.y) == 100

def test_path_morph2():
    p = path.Path()

    p.add(19, 34, 10000)
    p.add(10, 10, 10000)
    p.add(600, 10, 10001)

    pm = p.morph((10, 100), (0, 0))

    start = pm.start_pos()
    end = pm.end_pos()
    assert round(start.x) == 10
    assert round(start.y) == 100
    assert round(end.x) == 0
    assert round(end.y) == 0

def test_timedpos_comparison():
    t1 = path.TimedPosition(0, 0, 0)
    t2 = path.TimedPosition(0, 0, 1)
    r = t1 < t2
    assert r is True

    r2 = t1 > t2
    assert r2 is False

    eq = t1 == t2
    assert eq is False

    b = False
    with pytest.raises(NotImplementedError):
        r = b == t1


def test_timedpos_simple():
    t = path.TimedPosition(0, 0, 100)
    assert t.time() == 100


def test_sort_path():
    p = path.Path()

    p.add(19, 34, 10040)
    p.add(10, 10, 10000)
    p.add(600, 10, 10001)

    print(p)
    s = path.Path(sorted(p))
    print(s)

    assert s[0].timestamp == 10000
    assert s[2].timestamp == 10040
