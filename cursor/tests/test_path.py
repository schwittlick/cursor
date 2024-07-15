from cursor.path import Path
from cursor.position import Position
from cursor.bb import BoundingBox

import random
import pytest
import math

from cursor.properties import Property


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
    p = Path.from_tuple_list([(0, 0), (10, 11)])

    start = p.start_pos()
    assert start.x == 0
    assert start.y == 0

    end = p.end_pos()
    assert end.x == 10
    assert end.y == 11


def test_path_scale():
    p = Path.from_tuple_list([(3, 5), (5, 9), (-3, -10)])

    p.scale(2, 5)

    assert p[0].x == 6
    assert p[0].y == 25
    assert p[1].x == 10
    assert p[1].y == 45
    assert p[2].x == -6
    assert p[2].y == -50


def test_path_translate():
    p = Path.from_tuple_list([(3, 5), (5, 9)])
    p.translate(2, 5)

    assert p[0].x == 5
    assert p[0].y == 10
    assert p[1].x == 7
    assert p[1].y == 14


def test_path_bb():
    p = Path.from_tuple_list(
        [(0, 0), (140, 11),
         (23, 141), (141, 4511)])

    bb = p.bb()
    assert bb.x == 0
    assert bb.y == 0
    assert bb.x2 == 141
    assert bb.y2 == 4511


def test_path_bb2():
    p = Path.from_tuple_list(
        [(100, 100), (200, 100),
         (100, 200), (200, 200)])

    bb = p.bb()
    assert bb.x == 100
    assert bb.y == 100
    assert bb.x2 == 200
    assert bb.y2 == 200


def test_path_oriented_bb():
    p = Path.from_tuple_list(
        [(1, 1), (100, 100),
         (100, 101), (3, 3)])
    bb = p.oriented_bb()
    # this test is so lazy..
    assert len(bb) == 5


def test_path_morph():
    p = Path.from_tuple_list(
        [(19, 34), (10, 10), (600, 10)])

    pm = p.morph((0, 0), (10, 100))

    start = pm.start_pos()
    end = pm.end_pos()
    assert round(start.x) == 0
    assert round(start.y) == 0
    assert round(end.x) == 10
    assert round(end.y) == 100


def test_path_morph2():
    p = Path.from_tuple_list([(19, 34), (10, 10), (600, 10)])

    pm = p.morph((10, 100), (0, 0))

    start = pm.start_pos()
    end = pm.end_pos()
    assert round(start.x) == 10
    assert round(start.y) == 100
    assert round(end.x) == 0
    assert round(end.y) == 0


def test_path_interp():
    p = Path.from_tuple_list([(0, 0), (100, 0)])
    p1 = Path.from_tuple_list([(0, 100), (100, 100)])

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
    p1 = Path.from_tuple_list(
        [(100, 34), (200, 10), (100, 10),
         (200, 10), (100, 10), (200, 20)])

    p2 = Path.from_tuple_list(
        [(200, 10), (200, 10), (200, 10),
         (200, 10), (200, 10)])

    sx1 = p1.entropy_x
    sx2 = p2.entropy_x
    assert sx1 > sx2

    sy1 = p1.entropy_y
    sy2 = p2.entropy_y
    assert sy1 > sy2


def test_entropy_by_position1():
    p1 = Path.from_tuple_list(
        [(10, 10), (10, 10), (10, 10), (10, 10)])

    sx1 = p1.entropy_x
    sy1 = p1.entropy_y

    assert sx1 == 0.0
    assert sy1 == 0.0


def test_entropy_by_position2():
    p1 = Path.from_tuple_list(
        [(10, 10), (11, 10), (12, 10), (13, 10)])

    sx1 = p1.entropy_x
    sy1 = p1.entropy_y

    assert math.isclose(sx1, 1.386294361119)
    assert math.isclose(sy1, 0.0)


def test_variation():
    p1 = Path.from_tuple_list(
        [(10, 10), (11, 10), (12, 10), (13, 10)])

    sx = p1.variation_x
    sy = p1.variation_y

    assert math.isclose(sx, 0.11226039, abs_tol=0.00001)
    assert math.isclose(sy, 0.0)


def test_differential_entropy():
    random.seed(0)

    p1 = Path.from_tuple_list([(random.random(), random.random()) for _ in range(20)])

    sx1 = p1.differential_entropy_x
    sy1 = p1.differential_entropy_y

    assert math.isclose(sx1, -0.42138186975, abs_tol=0.00001)
    assert math.isclose(sy1, -0.02186395082, abs_tol=0.00001)


def test_simplify_random():
    random.seed(0)

    p1 = Path.from_tuple_list([(random.random(), random.random()) for _ in range(20)])

    p1.simplify(0.01)

    assert len(p1) == 18


def test_entropy_by_position3():
    # lower entropy value
    # because repeated
    p1 = Path.from_tuple_list([(10, 10), (11, 10), (10, 10), (11, 10)])

    sx1 = p1.entropy_x
    sy1 = p1.entropy_y

    assert math.isclose(sx1, 0.693147180559)
    assert math.isclose(sy1, 0)


def test_entropy_by_position4():
    p1 = Path()

    for i in range(20000):
        p1.add(random.randint(-10000, 10000), random.randint(-10000, 10000))

    sx1 = p1.entropy_x
    sy1 = p1.entropy_y

    assert sx1 > 9.3
    assert sy1 > 9.3


def test_path_clean():
    p = Path.from_tuple_list(
        [(1, 1), (1, 1), (1, 2), (1, 2),
         (1, 2), (2, 2), (2, 2), (2, 2)])

    assert len(p) == 8

    p.clean()

    assert len(p) == 3


def test_path_limit():
    p = Path.from_tuple_list(
        [(0.9, 0.9), (0.9, 1.0), (0.9, 1.1), (0.1, 0.8),
         (-0.1, 0.8), (0.0, 0.0), (1.0, 1.0)])

    p.limit()

    assert len(p) == 5


def test_path_offset_shapely():
    p = Path.from_tuple_list(
        [(0.9, 0.9), (0.9, 1.0), (0.9, 1.1), (0.1, 0.8),
         (-0.1, 0.8), (0.0, 0.0), (1.0, 1.0)])
    p.scale(10, 10)

    new = p.parallel_offset(1)

    assert len(new) == 1
    assert len(new[0]) == 7


def test_path_nearest_points():
    p = Path.from_tuple_list([(0, 0), (1, 1.1), (2, 0)])

    new = p.nearest_points(Position(1.0, 2.0))

    assert new.x == 1.0
    assert math.isclose(new.y, 1.1, abs_tol=0.0001)


def test_path_dilate():
    p = Path.from_tuple_list([(0, 0), (1, 1.1), (2, 0)])

    new = p.dilate_erode(2.0)

    assert len(new) == 78


def test_path_reverse():
    """
    testing in-place reverse() and reversed()
    """
    p1 = Path.from_tuple_list([(1, 1), (2, 2), (3, 3)])
    p_test = Path.from_tuple_list([(1, 1), (2, 2), (3, 3)])

    assert p1 == p_test

    p1.reverse()

    p_reversed = Path.from_tuple_list([(3, 3), (2, 2), (1, 1)])

    assert p1 == p_reversed

    p2 = Path.from_tuple_list([(1, 1), (2, 2), (3, 3)])

    p3 = p2.reversed()

    assert p2 == p_test
    assert p3 == p_reversed


def test_path_distance():
    p = Path.from_tuple_list([(0, 0), (0, 10), (10, 10), (-10, 10)])
    assert p.distance == 40


def test_path_layer():
    p = Path()
    assert p.layer == "layer1"

    p.layer = "custom"
    assert p.layer == "custom"


def test_path_intersection1():
    p = Path.from_tuple_list([(0, 0), (10, 10)])
    p2 = Path.from_tuple_list([(10, 0), (0, 10)])

    # classic cross intersection

    inter = p.intersect(p2)
    assert inter[0] is True
    assert inter[1] == 5.0
    assert inter[2] == 5.0


def test_path_intersection2():
    p = Path.from_tuple_list([(0, 0), (0, 10)])
    p2 = Path.from_tuple_list([(1, 0), (1, 10)])

    # two parallel lines

    inter = p.intersect(p2)
    assert inter[0] is False


def test_path_intersection3():
    p = Path.from_tuple_list([(0, 0), (0, 10)])
    p2 = Path.from_tuple_list([(1, 0), (5, 10)])

    # infinite lines will intersct
    # line segments not

    inter = p.intersect(p2)
    assert inter[0] is False


def test_intersection_all():
    random.seed(1)
    p1 = Path.from_tuple_list([(random.uniform(-10, 10), random.uniform(-10, 10)) for _ in range(2)])
    p2 = Path.from_tuple_list([(random.uniform(-10, 10), random.uniform(-10, 10)) for _ in range(2)])
    intersections = p1.intersect_all(p2)
    assert len(intersections) == 1


def test_angles():
    p = Path.from_tuple_list(
        [(0, 1), (1, 1), (1, 0), (0.5, 0)])

    changes = p.direction_changes(mapped=True)
    assert math.isclose(changes[0], 45.0, abs_tol=0.00001)
    assert math.isclose(changes[1], 45.0, abs_tol=0.00001)
    assert math.isclose(changes[2], 0.0, abs_tol=0.00001)


def test_angles_posneg():
    p = Path.from_tuple_list(
        [(0, 1), (1, 1), (1, 0), (1, 1)])

    changes = p.direction_changes(mapped=False)
    assert math.isclose(changes[0], 45.0, abs_tol=0.00001)
    assert math.isclose(changes[1], 45.0, abs_tol=0.00001)
    assert math.isclose(changes[2], -45.0, abs_tol=0.00001)


def test_slopes():
    p = Path.from_tuple_list(
        [(0, 1), (1, 1), (1, 0), (1, 1)])

    slopes = p.slopes()
    assert slopes == [0.0, float('inf'), float('inf')]


def test_slopes2():
    p = Path.from_tuple_list(
        [(0, 0), (1, 0), (2, 1), (1, 1), (1, 3), (2, 3), (4, 0)])

    slopes = p.slopes()
    assert slopes == [0.0, 1.0, -0.0, float('inf'), 0.0, -1.5]


def disabled_test_similarity():
    p1 = Path.from_tuple_list(
        [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)])

    p2 = Path.from_tuple_list(
        [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)])

    sim = p1.similarity(p2)
    assert sim == 1.0

    p3 = Path.from_tuple_list(
        [(0, 0), (0, 1), (0, 2),
         (0, 3.1), (0, 4.1)])

    sim2 = p1.similarity(p3)
    assert sim2 >= 0.9


def test_offset():
    p1 = Path.from_tuple_list(
        [(0, 0), (1, 0), (0.5, 1),
         (3.5, 1), (3, 0), (4, 0)])

    offset = p1.offset(0.2)

    assert math.isclose(offset[0].y, -0.2, abs_tol=0.00001)
    # can't compare the rest


def test_downsample():
    p1 = Path.from_tuple_list(
        [(0, 0), (1, 0), (2, 0), (3, 0),
         (4, 0), (6, 0), (7, 0), (7.2, 0)])

    p1.downsample(1.1)

    assert len(p1) == 4


def test_resample():
    p1 = Path.from_tuple_list(
        [(0, 0), (1, 0), (0, 1), (1.1, 1.1)])
    # using (1.1, 1.1) for the last points in order to not drop the last
    # point because it would not be included (the last two points distance
    # would be below 0.5)

    p1.resample(0.5)

    assert len(p1) == 8


def test_rdp():
    p = Path.from_tuple_list(
        [(0, 0), (1, 0), (2, 0), (3, 0),
         (4, 0), (6, 0), (7, 0), (7.2, 0)])

    p.simplify(0.1)

    assert len(p) == 2
    assert p[0] == Position(0, 0)
    assert p[1] == Position(7.2, 0)


def test_intersect():
    p1 = [1, 1]
    p2 = [10, 1]

    p3 = [4, 0]
    p4 = [4, 10]

    i = Path.intersect_segment(p1, p2, p3, p4)
    assert i[0] == 4
    assert i[1] == 1


def test_clip():
    p = Path.from_tuple_list(
        [(5, 5), (5, 15), (6, 15), (6, 5),
         (5, 5), (11, 5), (12, 5), (5, 5), (7, 5)])

    bb = BoundingBox(1, 1, 10, 10)

    clipped = p.clip(bb)

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

    assert p[0] == Position(5, 5)
    assert p[1] == Position(5, 15)
    assert p[2] == Position(6, 15)
    assert p[3] == Position(6, 5)


def test_arr():
    p = Path.from_tuple_list([(0, 0), (1, 2), (3, 4)])

    arr = p.as_array()
    assert arr.shape[0] == 3
    assert arr.shape[1] == 2


def test_centroid():
    p = Path.from_tuple_list([(-1, -1), (1, 1)])

    centroidx, centroidy = p.centeroid()

    assert centroidx == 0.0
    assert centroidy == 0.0


def test_bb_mostly_inside():
    bb = BoundingBox(0, 0, 300, 300)
    pa = Path.from_tuple_list([(0, 0), (0, 1), (0, 3), (-1, 3), (-1, 5)])

    assert pa.mostly_inside(bb)

    pa.add(-1, 10)

    assert not pa.mostly_inside(bb)


def test_is_closed():
    pa = Path.from_tuple_list([(0, 0), (0, 1), (0, 0)])

    assert pa.is_closed()

    pa.add(-1, 10)

    assert not pa.is_closed()


def test_as_tuple_list():
    pa = Path.from_tuple_list([(0, 0), (1, 2), (3, 4)])

    assert pa.as_tuple_list() == [(0, 0), (1, 2), (3, 4)]


def test_from_tuple_list():
    pa = Path.from_tuple_list([(0, 0), (1, 2), (3, 4)])
    assert pa[0] == Position(0, 0)
    assert pa[1] == Position(1, 2)
    assert pa[2] == Position(3, 4)


def test_intersection_points():
    p = Path.from_tuple_list([(0, 0), (1, 1), (2, 2), (0, 2), (0, 1), (1, 0)])

    intersections = p.intersection_points()
    assert len(intersections) == 1

    assert intersections[0] == (0.5, 0.5)


def test_move_to_origin():
    p = Path.from_tuple_list([(10, 1), (10, 10), (10, 20)])

    p.move_to_origin()

    assert p.as_tuple_list() == [(0, 0), (0, 9), (0, 19)]


def test_functional():
    path = Path.from_tuple_list([(0, 0), (1, 0), (2, 1), (3, -1), (4, 0), (5, 0)])
    is_functional, intersections = path.vertical_line_test(0.1)
    assert is_functional


def test_functional_fixed():
    path = Path.from_tuple_list([(0, 0), (1, 0), (2, 1), (3, -1), (4, 0), (5, 0)])
    is_functional, intersections = path.vertical_line_test2()
    assert is_functional


def test_split_by_color():
    pos1 = Position(0, 0, 0, {Property.COLOR: (1, 2, 3)})
    pos2 = Position(1, 0, 0, {Property.COLOR: (1, 2, 3)})
    pos3 = Position(2, 1, 0, {Property.COLOR: (100, 200, 300)})
    pos4 = Position(3, -1, 0, {Property.COLOR: (1, 2, 3)})
    pos5 = Position(4, 0, 0, {Property.COLOR: (1, 2, 3)})
    pos6 = Position(5, 0, 0, {Property.COLOR: (100, 200, 300)})

    path = Path.from_list([pos1, pos2, pos3, pos4, pos5, pos6])
    paths = path.split_by_color()

    new_path1 = Path.from_list([Position(0, 0, 0, {Property.COLOR: (1, 2, 3)}),
                                Position(1, 0, 0, {Property.COLOR: (1, 2, 3)}),
                                Position(2, 1, 0, {Property.COLOR: (1, 2, 3)})])

    new_path2 = Path.from_list([Position(2, 1, 0, {Property.COLOR: (100, 200, 300)}),
                                Position(3, -1, 0, {Property.COLOR: (100, 200, 300)})])

    new_path3 = Path.from_list([Position(3, -1, 0, {Property.COLOR: (1, 2, 3)}),
                                Position(4, 0, 0, {Property.COLOR: (1, 2, 3)}),
                                Position(5, 0, 0, {Property.COLOR: (1, 2, 3)})])

    new_path4 = Path.from_list([Position(5, 0, 0, {Property.COLOR: (100, 200, 300)}),
                                Position(5, 0, 0, {Property.COLOR: (100, 200, 300)})])
    compare_paths = [new_path1, new_path2, new_path3, new_path4]

    assert compare_paths == paths
