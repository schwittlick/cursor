from ..cursor import path
import pyautogui
import pytest


def test_pathcollection_minmax():
    size = pyautogui.Size(100, 100)
    pcol = path.PathCollection(size)

    p1 = path.Path()

    p1.add(5, 5111, 10000)
    p1.add(10, 11, 10001)
    p1.add(11, 11, 10002)
    p1.add(20, 20, 10003)
    p1.add(30, 31, 10004)
    p1.add(40, 41, 10005)

    p2 = path.Path()

    p2.add(545, 54, 10000)
    p2.add(160, 11, 10001)
    p2.add(11, 171, 10002)
    p2.add(20, 20, 10003)
    p2.add(30, 31, 10004)
    p2.add(940, 941, 10005)

    pcol.add(p1, size)
    pcol.add(p2, size)

    assert pcol.empty() is False

    min = pcol.min()
    max = pcol.max()
    bb = pcol.bb()

    assert min[0] == bb[0]
    assert min[1] == bb[1]
    assert max[0] == bb[2]
    assert max[1] == bb[3]

    assert min[0] == 5
    assert min[1] == 11
    assert max[0] == 940
    assert max[1] == 5111

def test_pathcollection_add():
    size = pyautogui.Size(100, 100)
    pcol = path.PathCollection(size)

    assert pcol.empty() is True

    p1 = path.Path()

    pcol.add(p1, size)

    assert pcol.empty() is True

    size2 = pyautogui.Size(101, 100)
    with pytest.raises(Exception):
        pcol.add(p1, size2)


def test_pathcollection_get():
    size = pyautogui.Size(100, 100)
    pcol = path.PathCollection(size)

    p1 = path.Path()

    p1.add(5, 5111, 10000)
    p1.add(40, 41, 10005)

    pcol.add(p1, size)

    p2 = pcol[0]

    assert p1 == p2

    with pytest.raises(IndexError):
        p3 = pcol[1]

def test_pathcollection_compare():
    size = pyautogui.Size(100, 100)
    pcol = path.PathCollection(size)
    p1 = path.Path()

    p1.add(5, 5111, 10000)
    p1.add(40, 41, 10005)

    pcol.add(p1, size)

    pcol2 = path.PathCollection(size)
    r = pcol == pcol2

    assert r == False

    r2 = pcol == True
    assert r2 == False