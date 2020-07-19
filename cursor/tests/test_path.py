from cursor.path import Path
from cursor.path import TimedPosition
from cursor.path import BoundingBox

import pyautogui

import pytest


def test_path_empty_start():
    p = Path()

    with pytest.raises(IndexError):
        p.start_pos()


def test_path_empty_end():
    p = Path()
    with pytest.raises(IndexError):
        p.end_pos()


def test_path_add():
    p = Path()

    assert len(p) == 0

    for i in range(100):
        p.add(0, 0, 100)

    assert len(p) == 100


def test_path_clear():
    p = Path()
    assert p.empty()

    p.add(0, 0, 100)

    assert len(p) == 1

    p.clear()

    assert len(p) == 0

    assert p.empty()


def test_path_copy():
    p = Path()

    p2 = p.copy()
    assert p is not p2

    p3 = p
    assert p is p3


def test_path_start_end():
    p = Path()
    p.add(0, 0, 10000)
    p.add(10, 11, 10000)

    start = p.start_pos()
    assert start.x == 0
    assert start.y == 0

    end = p.end_pos()
    assert end.x == 10
    assert end.y == 11


def test_path_scale():
    p = Path()
    p.add(3, 5)
    p.add(5, 9)
    p.add(-3, -10)

    p.scale(2, 5)

    assert p[0].x == 6
    assert p[0].y == 25
    assert p[1].x == 10
    assert p[1].y == 45
    assert p[2].x == -6
    assert p[2].y == -50


def test_path_translate():
    p = Path()
    p.add(3, 5)
    p.add(5, 9)
    p.translate(2, 5)

    assert p[0].x == 5
    assert p[0].y == 10
    assert p[1].x == 7
    assert p[1].y == 14


def test_path_bb():
    p = Path()
    p.add(0, 0, 10000)
    p.add(140, 11, 10000)
    p.add(23, 141, 10000)
    p.add(141, 4511, 10000)

    bb = p.bb()
    assert bb.x == 0
    assert bb.y == 0
    assert bb.w == 141
    assert bb.h == 4511


def test_path_bb2():
    p = Path()
    p.add(100, 100, 0)
    p.add(200, 100, 0)
    p.add(100, 200, 0)
    p.add(200, 200, 0)

    bb = p.bb()
    assert bb.x == 100
    assert bb.y == 100
    assert bb.w == 200
    assert bb.h == 200


def test_path_morph():
    p = Path()

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
    p = Path()

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


def test_path_interp():
    p = Path()
    p.add(0, 0, 10000)
    p.add(100, 0, 10001)

    p1 = Path()
    p1.add(0, 100, 10000)
    p1.add(100, 100, 10001)

    interped = p.interp(p1, 0.5)

    assert int(interped[0].y) == 50
    assert int(interped[1].y) == 50
    assert int(interped[0].x) == 0
    assert int(interped[1].x) == 100


def test_timedpos_comparison():
    t1 = TimedPosition(0, 0, 0)
    t2 = TimedPosition(0, 0, 1)
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
    t = TimedPosition(0, 0, 100)
    assert t.time() == 100


def test_timedpos_scale():
    t = TimedPosition(1, 2, 100)
    t.scale(5, 10)
    assert t.x == 5.0
    assert t.y == 20.0


def test_sort_path():
    p = Path()

    p.add(19, 34, 10040)
    p.add(10, 10, 10000)
    p.add(600, 10, 10001)

    print(p)
    s = Path(sorted(p))
    print(s)

    assert s[0].timestamp == 10000
    assert s[2].timestamp == 10040


def test_entropy():
    p1 = Path()
    p1.add(100, 34, 10040)
    p1.add(200, 10, 10000)
    p1.add(100, 10, 10001)
    p1.add(200, 10, 10001)
    p1.add(100, 10, 10001)
    p1.add(200, 10, 10001)

    p2 = Path()
    p2.add(200, 10, 10000)
    p2.add(200, 10, 10001)
    p2.add(200, 10, 10001)
    p2.add(200, 10, 10001)
    p2.add(200, 10, 10001)

    sx1 = p1.shannon_x()
    sx2 = p2.shannon_x()
    assert sx1 > sx2

    sy1 = p1.shannon_y()
    sy2 = p2.shannon_y()
    assert sy1 > sy2


def test_bb_center():
    bb = BoundingBox(100, 200, 300, 400)
    cx, cy = bb.center()
    assert cx == 200
    assert cy == 300


def test_bb_center2():
    bb = BoundingBox(-100, -100, 100, 100)
    cx, cy = bb.center()
    assert cx == 0
    assert cy == 0


def test_path_clean():
    p = Path()

    p.add(5, 5111, 10000)
    p.add(5, 5111, 10000)
    p.add(5, 5112, 10000)
    p.add(5, 5112, 10000)
    p.add(5, 5112, 10000)
    p.add(6, 5112, 10000)
    p.add(6, 5112, 10000)
    p.add(6, 5112, 10000)

    assert len(p) == 8

    p.clean()

    assert len(p) == 3


def test_path_reverse():
    p1 = Path()

    p1.add(5, 5111, 10000)
    p1.add(5, 5112, 10000)
    p1.add(6, 5112, 10000)

    assert p1[0].x == 5
    assert p1[0].y == 5111

    assert p1[1].x == 5
    assert p1[1].y == 5112

    assert p1[2].x == 6
    assert p1[2].y == 5112

    p1.reverse()

    assert p1[0].x == 6
    assert p1[0].y == 5112

    assert p1[1].x == 5
    assert p1[1].y == 5112

    assert p1[2].x == 5
    assert p1[2].y == 5111

    p2 = Path()

    p2.add(5, 5111, 10000)
    p2.add(5, 5112, 10000)
    p2.add(6, 5112, 10000)

    p3 = p2.reversed()

    assert p2[0].x == 5
    assert p2[0].y == 5111

    assert p2[1].x == 5
    assert p2[1].y == 5112

    assert p2[2].x == 6
    assert p2[2].y == 5112

    assert p3[0].x == 6
    assert p3[0].y == 5112

    assert p3[1].x == 5
    assert p3[1].y == 5112

    assert p3[2].x == 5
    assert p3[2].y == 5111


def test_path_distance():
    p = Path()
    p.add(0, 0, 10000)
    p.add(0, 10, 10000)
    p.add(10, 10, 10000)

    size = pyautogui.Size(1, 1)
    d = p.distance(size)

    assert d == 20


def test_path_layer():
    p = Path()
    assert p.layer is "default"

    p.layer = "custom"
    assert p.layer is "custom"
