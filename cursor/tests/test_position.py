from cursor.position import Position

import pytest


def test_timedposition_copy():
    t1 = Position(0, 0, 0)

    t2 = t1.copy()

    assert t1 is not t2
    assert t1 == t2

    t2.x = 1

    assert t1 != t2


def test_timedposition_translate():
    t1 = Position(0, 0)
    t1.translate(1, 2)

    assert t1.x == 1
    assert t1.y == 2


def test_timedposition_scale():
    t1 = Position(2, 2)
    t1.scale(2, 2)

    assert t1.x == 4
    assert t1.y == 4


def test_timedpos_comparison():
    t1 = Position(0, 0, 0)
    t2 = Position(0, 0, 1)
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
    t = Position(1, 2, 100)
    assert t.time() == 100
    assert t.x == 1
    assert t.y == 2


def test_timedpos_scale():
    t = Position(1, 2, 100)
    t.scale(5, 10)
    assert t.x == 5.0
    assert t.y == 20.0
