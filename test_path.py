import path
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
    p.add(0, 0, 100)

    assert len(p) == 1

    p.clear()

    assert len(p) == 0


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


def test_path_morph():
    p = path.Path()

    p.add(0, 0, 10000)
    p.add(10, 10, 10000)
    p.add(2, 10, 10001)

    pm = p.morph((0, 0), (10, 100))

    start = pm.start_pos()
    end = pm.end_pos()
    assert round(start.x) == 0
    assert round(start.y) == 0
    assert round(end.x) == 10
    assert round(end.y) == 100