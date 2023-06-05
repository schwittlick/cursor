from cursor.path import Path
from cursor.position import Position
from cursor.bb import BoundingBox

import random
import pytest
import math


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

    sx1 = p1.entropy_x
    sx2 = p2.entropy_x
    assert sx1 > sx2

    sy1 = p1.entropy_y
    sy2 = p2.entropy_y
    assert sy1 > sy2


def test_entropy_by_position1():
    p1 = Path()
    p1.add(10, 10)
    p1.add(10, 10)
    p1.add(10, 10)
    p1.add(10, 10)

    sx1 = p1.entropy_x
    sy1 = p1.entropy_y

    assert sx1 == 0.0
    assert sy1 == 0.0


def test_entropy_by_position2():
    p1 = Path()
    p1.add(10, 10)
    p1.add(11, 10)
    p1.add(12, 10)
    p1.add(13, 10)

    sx1 = p1.entropy_x
    sy1 = p1.entropy_y

    assert sx1 == 1.3862943611198906
    assert sy1 == 0.0


def test_variation():
    p1 = Path()
    p1.add(10, 10)
    p1.add(11, 10)
    p1.add(12, 10)
    p1.add(13, 10)

    sx = p1.variation_x
    sy = p1.variation_y

    assert math.isclose(sx, 0.11226038684659179)
    assert math.isclose(sy, 0.0)


def test_differential_entropy():
    random.seed(0)

    p1 = Path.from_tuple_list([(random.random(), random.random()) for _ in range(20)])

    sx1 = p1.differential_entropy_x
    sy1 = p1.differential_entropy_y

    assert math.isclose(sx1, -0.63857967954)
    assert math.isclose(sy1, -0.02733247453)


def test_simplify_random():
    random.seed(0)

    p1 = Path.from_tuple_list([(random.random(), random.random()) for _ in range(20)])

    p1.simplify(0.01)

    assert len(p1) == 18


def test_entropy_by_position3():
    # lower entropy value
    # because repeated
    p1 = Path()
    p1.add(10, 10)
    p1.add(11, 10)
    p1.add(10, 10)
    p1.add(11, 10)

    sx1 = p1.entropy_x
    sy1 = p1.entropy_y

    assert sx1 == 0.6931471805599453
    assert sy1 == 0.0


def test_entropy_by_position4():
    p1 = Path()

    for i in range(20000):
        p1.add(random.randint(-10000, 10000), random.randint(-10000, 10000))

    sx1 = p1.entropy_x
    sy1 = p1.entropy_y

    assert sx1 > 9.3
    assert sy1 > 9.3


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


def test_path_offset_shapely():
    p = Path()

    p.add(0.9, 0.9, 0)
    p.add(0.9, 1.0, 0)
    p.add(0.9, 1.1, 0)
    p.add(0.1, 0.8, 0)
    p.add(-0.1, 0.8, 0)
    p.add(0.0, 0.0, 0)
    p.add(1.0, 1.0, 0)
    p.scale(10, 10)

    new = p.parallel_offset(1)

    assert len(new) == 1
    assert len(new[0]) == 6


def test_path_nearest_points():
    p = Path()

    p.add(0.0, 0.0, 0)
    p.add(1.0, 1.1, 0)
    p.add(2.0, 0.0, 0)

    new = p.nearest_points(Position(1.0, 2.0))

    assert new.x == 1.0
    assert new.y == 1.1


def test_path_dilate():
    p = Path()

    p.add(0.0, 0.0, 0)
    p.add(1.0, 1.1, 0)
    p.add(2.0, 0.0, 0)

    new = p.dilate_erode(2.0)

    assert len(new) == 78


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
    p.add(0.0, 1.0)
    p.add(1.0, 1.0)
    p.add(1.0, 0.0)
    p.add(0.5, 0.0)

    changes = p.direction_changes(mapped=True)
    assert changes[0] == 45.0
    assert changes[1] == 45.0
    assert changes[2] == 0.0


def test_angles_posneg():
    p = Path()
    p.add(0.0, 1.0)
    p.add(1.0, 1.0)
    p.add(1.0, 0.0)
    p.add(1.0, 1.0)

    changes = p.direction_changes(mapped=False)
    assert changes[0] == 45.0
    assert changes[1] == 45.0
    assert changes[2] == -45.0


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
    # can't compare the rest


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


def test_rdp():
    p1 = Path()
    p1.add(0, 0)
    p1.add(1, 0)
    p1.add(2, 0)
    p1.add(3, 0)
    p1.add(4, 0)
    p1.add(6, 0)
    p1.add(7, 0)
    p1.add(7.2, 0)

    p1.simplify(0.1)

    assert len(p1) == 2
    assert p1[0] == Position(0, 0)
    assert p1[1] == Position(7.2, 0)


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


def test_arr():
    p = Path()
    p.add(0, 0)
    p.add(1, 2)
    p.add(3, 4)

    arr = p.as_array()
    assert arr.shape[0] == 3
    assert arr.shape[1] == 2


def test_centroid():
    p = Path()
    p.add(-1, -1)
    p.add(1, 1)

    centroidx, centroidy = p.centeroid()

    assert centroidx == 0.0
    assert centroidy == 0.0


def test_bb_mostly_inside():
    bb = BoundingBox(0, 0, 300, 300)
    pa = Path()
    pa.add(0, 0)
    pa.add(0, 1)
    pa.add(0, 3)
    pa.add(-1, 3)
    pa.add(-1, 5)

    assert pa.mostly_inside(bb)

    pa.add(-1, 10)

    assert not pa.mostly_inside(bb)


def test_is_closed():
    pa = Path()
    pa.add(0, 0)
    pa.add(0, 1)
    pa.add(0, 0)

    assert pa.is_closed()

    pa.add(-1, 10)

    assert not pa.is_closed()


def test_as_tuple_list():
    pa = Path()
    pa.add(0, 0)
    pa.add(1, 2)
    pa.add(3, 4)

    assert pa.as_tuple_list() == [(0, 0), (1, 2), (3, 4)]


def test_from_tuple_list():
    tuple_list = [(0, 0), (1, 2), (3, 4)]
    pa = Path.from_tuple_list(tuple_list)
    assert pa[0] == Position(0, 0)
    assert pa[1] == Position(1, 2)
    assert pa[2] == Position(3, 4)


def test_intersection_points():
    p1 = Path()
    p1.add(0, 0)
    p1.add(1, 1)
    p1.add(2, 2)
    p1.add(0, 2)
    p1.add(0, 1)
    p1.add(1, 0)

    intersections = p1.intersection_points()
    assert len(intersections) == 1

    assert intersections[0] == (0.5, 0.5)
