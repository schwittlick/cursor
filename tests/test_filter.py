from ..cursor import path
from ..cursor import filter
import pyautogui
import pytest

def test_bb_filter():
    size = pyautogui.Size(100, 100)
    pcol = path.PathCollection(size)

    p1 = path.Path()

    p1.add(5, 51, 10000)
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

    assert len(pcol) == 2

    f1 = filter.Filter()
    with pytest.raises(Exception):
        pcol.filter(f1)

    bb = path.BoundingBox(0, 0, 100, 100)
    f2 = filter.BoundingBoxFilter(bb)
    pcol.filter(f2)

    assert len(pcol) == 1
    assert pcol[0] is p1

def test_point_count_filter():
    size = pyautogui.Size(100, 100)
    pcol = path.PathCollection(size)

    p1 = path.Path()

    p1.add(5, 51, 10000)
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

    pcol.add(p1, size)
    pcol.add(p2, size)

    f2 = filter.MinPointCountFilter(6)
    pcol.filter(f2)

    assert len(pcol) == 1
    assert pcol[0] is p1