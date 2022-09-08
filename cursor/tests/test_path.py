from cursor.path import Path
from cursor.path import Position
from cursor.bb import BoundingBox
from cursor.path import PathCollection
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
    assert bb.x2 == 141
    assert bb.y2 == 4511


def test_path_bb2():
    p = Path()
    p.add(100, 100, 0)
    p.add(200, 100, 0)
    p.add(100, 200, 0)
    p.add(200, 200, 0)

    bb = p.bb()
    assert bb.x == 100
    assert bb.y == 100
    assert bb.x2 == 200
    assert bb.y2 == 200


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

    sx1 = p1.shannon_x
    sx2 = p2.shannon_x
    assert sx1 > sx2

    sy1 = p1.shannon_y
    sy2 = p2.shannon_y
    assert sy1 > sy2


def test_bb_center():
    bb = BoundingBox(100, 200, 300, 400)
    c = bb.center()
    assert c.x == 200
    assert c.y == 300


def test_bb_center2():
    bb = BoundingBox(-100, -100, 100, 100)
    c = bb.center()
    assert c.x == 0
    assert c.y == 0


def test_bb_center3():
    bb = BoundingBox(0, 0, 300, 300)
    c = bb.center()
    assert c.x == 150
    assert c.y == 150


def test_bb_scale():
    bb = BoundingBox(0, 0, 100, 100)
    bb.scale(0.5)

    assert bb.x == 25
    assert bb.y == 25
    assert bb.x2 == 75
    assert bb.y2 == 75
    assert bb.w == 50
    assert bb.h == 50


def test_bb_subdiv():
    bb = BoundingBox(0, 0, 300, 300)
    subdived = bb.subdiv(10, 10)

    assert len(subdived) == 100

    for _bb in subdived:
        assert _bb.w == 30
        assert _bb.h == 30


def test_bb_mostly_inside():
    bb = BoundingBox(0, 0, 300, 300)
    pa = Path()
    pa.add(0, 0)
    pa.add(0, 1)
    pa.add(0, 3)
    pa.add(-1, 3)
    pa.add(-1, 5)

    assert bb.mostly_inside(pa)

    pa.add(-1, 10)

    assert not bb.mostly_inside(pa)


def test_inside_pos():
    bb = BoundingBox(0, 0, 300, 300)

    assert bb.inside(Position(10, 10))
    assert not bb.inside(Position(10, 301))

    pa = Path()
    pa.add(0, 300)
    pa.add(300, 280)

    assert bb.inside(pa)

    pa.add(-10, 10)
    assert not bb.inside(pa)

    pc = PathCollection()
    pc.add(pa)
    assert not bb.inside(pc)

    pc2 = PathCollection()
    p1 = Path()
    p1.add(100, 100)
    p1.add(100, 200)

    p2 = Path()
    p2.add(0, 0)
    p2.add(300, 300)
    pc2.add(p1)
    pc2.add(p2)

    assert bb.inside(p2)


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


def test_path_limit():
    p = Path()

    p.add(0.9, 0.9, 0)
    p.add(0.9, 1.0, 0)
    p.add(0.9, 1.1, 0)
    p.add(0.1, 0.8, 0)
    p.add(-0.1, 0.8, 0)
    p.add(0.0, 0.0, 0)
    p.add(1.0, 1.0, 0)

    p.limit()

    assert len(p) == 5


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

    d = p.distance

    assert d == 20


def test_path_layer():
    p = Path()
    assert p.layer == "layer1"

    p.layer = "custom"
    assert p.layer == "custom"


def test_path_intersection1():
    p = Path()
    p.add(0, 0)
    p.add(10, 10)

    p2 = Path()
    p2.add(10, 0)
    p2.add(0, 10)

    # classic cross intersection

    inter = p.intersect(p2)
    assert inter[0] is True
    assert inter[1] == 5.0
    assert inter[2] == 5.0


def test_path_intersection2():
    p = Path()
    p.add(0, 0)
    p.add(0, 10)

    p2 = Path()
    p2.add(1, 0)
    p2.add(1, 10)

    # two parallel lines

    inter = p.intersect(p2)
    assert inter[0] is False


def test_path_intersection3():
    p = Path()
    p.add(0, 0)
    p.add(0, 10)

    p2 = Path()
    p2.add(1, 0)
    p2.add(5, 10)

    # infinite lines will intersct
    # line segments not

    inter = p.intersect(p2)
    assert inter[0] is False


def test_angles():
    p = Path()
    p.add(0.0, 0.0)
    p.add(0.0, 1.0)
    p.add(1.0, 1.0)
    p.add(1.0, 0.0)
    p.add(0.5, 0.0)

    changes = p.direction_changes()
    assert changes[0] == 0.0
    assert round(changes[1], 2) == 45.0  # wat
    assert round(changes[2], 2) == 45.0
    assert changes[3] == 0.0


def disabled_test_similarity():
    p1 = Path()
    p1.add(0, 0)
    p1.add(0, 1)
    p1.add(0, 2)
    p1.add(0, 3)
    p1.add(0, 4)

    p2 = Path()
    p2.add(0, 0)
    p2.add(0, 1)
    p2.add(0, 2)
    p2.add(0, 3)
    p2.add(0, 4)

    sim = p1.similarity(p2)
    assert sim == 1.0

    p3 = Path()
    p3.add(0, 0)
    p3.add(0, 1)
    p3.add(0, 2)
    p3.add(0, 3.1)
    p3.add(0, 4.1)

    sim2 = p1.similarity(p3)
    assert sim2 >= 0.9


def test_offset():
    p1 = Path()
    p1.add(0, 0)
    p1.add(1, 0)
    p1.add(0.5, 1)
    p1.add(3.5, 1)
    p1.add(3, 0)
    p1.add(4, 0)

    offset = p1.offset(0.2)

    assert offset[0].y == -0.2


def test_downsample():
    p1 = Path()
    p1.add(0, 0)
    p1.add(1, 0)
    p1.add(2, 0)
    p1.add(3, 0)
    p1.add(4, 0)
    p1.add(6, 0)
    p1.add(7, 0)
    p1.add(7.2, 0)

    p1.downsample(1.1)

    assert len(p1) == 4


def test_intersect():
    p1 = [1, 1]
    p2 = [10, 1]

    p3 = [4, 0]
    p4 = [4, 10]

    i = Path.intersect_segment(p1, p2, p3, p4)
    assert i[0] == 4
    assert i[1] == 1


def test_clip():
    p1 = Path()
    p1.add(5, 5)
    p1.add(5, 15)
    p1.add(6, 15)
    p1.add(6, 5)
    p1.add(5, 5)
    p1.add(11, 5)
    p1.add(12, 5)
    p1.add(5, 5)
    p1.add(7, 5)

    bb = BoundingBox(1, 1, 10, 10)

    clipped = p1.clip(bb)

    assert len(clipped) == 3
    assert clipped[0][0] == Position(5, 5)
    assert clipped[0][1] == Position(5, 10)

    assert clipped[1][0] == Position(6, 10)
    assert clipped[1][1] == Position(6, 5)
    assert clipped[1][2] == Position(5, 5)
    assert clipped[1][3] == Position(10, 5)

    assert clipped[2][0] == Position(10, 5)
    assert clipped[2][1] == Position(5, 5)
    assert clipped[2][2] == Position(7, 5)

    assert p1[0] == Position(5, 5)
    assert p1[1] == Position(5, 15)
    assert p1[2] == Position(6, 15)
    assert p1[3] == Position(6, 5)
