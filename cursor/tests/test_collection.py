from cursor.path import Path
from cursor.properties import Property
from cursor.collection import Collection
from cursor.bb import BoundingBox
from cursor.timer import Timer

import pytest
import random
import math
import cProfile as profile

from cursor.position import Position


def test_copy():
    path = Path.from_tuple_list([(0, 0), (13, 37)])
    path.width = 123
    collection = Collection(name="test123")
    collection.add(path)

    path_to_compare = Path.from_tuple_list([(0, 0), (13, 37)])
    path_to_compare.width = 123

    assert collection.paths == [path_to_compare]
    assert collection.properties == {}
    assert collection.name == "test123"

    collection_copy = collection.copy()

    assert collection_copy.paths == [path_to_compare]
    assert collection_copy.properties == {}
    assert collection_copy.name == "test123"


def test_pathcollection_minmax():
    pcol = Collection.from_tuples(
        [
            [(5, 5111), (10, 11), (11, 11), (20, 20), (30, 31), (40, 41)],
            [(545, 54), (160, 11), (11, 171), (20, 20), (30, 31), (940, 941)],
        ]
    )

    assert pcol.empty() is False

    min = pcol.min()
    max = pcol.max()
    bb = pcol.bb()

    assert min[0] == bb.x
    assert min[1] == bb.y
    assert max[0] == bb.x2
    assert max[1] == bb.y2

    assert min[0] == 5
    assert min[1] == 11
    assert max[0] == 940
    assert max[1] == 5111


def test_collection_equal():
    assert Collection.from_tuples([[(5, 5111)]]) == Collection.from_tuples(
        [[(5, 5111)]]
    )

    assert Collection.from_tuples([[(5, 5111)]]) != Collection.from_tuples(
        [[(5, 5111), (2, 2)]]
    )

    assert Collection.from_tuples([[(5, 5111)]]) != Collection.from_tuples(
        [[(5, 5111)], [(5, 5111)]]
    )

    # different timestamps are *not* used for compare
    assert Collection(123) == Collection(123)
    assert Collection(123) == Collection(1234)


def test_bb_inside():
    p1 = Path()
    p1.add(100, 34)
    p1.add(200, 10)

    pc = Collection()
    pc.add(p1)

    bb = BoundingBox(0, 0, 300, 300)

    assert p1.inside(bb) is True
    assert pc.inside(bb) is True

    p1.add(500, 500, 10023)

    assert p1.inside(bb) is False
    assert pc.inside(bb) is False


def test_collection_as_array():
    p1 = Path()
    p1.add(100, 101)
    p1.add(200, 201)
    p1.add(300, 301)

    p2 = Path()
    p2.add(222, 223)
    p2.add(333, 334)

    pc = Collection()
    pc.add(p1)
    pc.add(p2)

    arr = pc.as_array()

    assert arr.shape[0] == 2

    assert arr[0].shape[0] == 3
    assert arr[1].shape[0] == 2

    assert arr[0][0, 0] == 100
    assert arr[0][0, 1] == 101


def test_collection_from_list_of_tuple_lists():
    tuples = [
        [(0.0, 150.0), (0.0, 0.0)],
        [(114.0, 150.0), (114.0, 0.0)],
        [(0.0, 79.6875), (114.0, 79.6875)],
    ]
    collection = Collection.from_tuples(tuples)

    assert len(collection) == len(tuples)
    assert collection[0] == Path.from_tuple_list([(0.0, 150.0), (0.0, 0.0)])
    assert collection[1] == Path.from_tuple_list([(114.0, 150.0), (114.0, 0.0)])
    assert collection[2] == Path.from_tuple_list([(0.0, 79.6875), (114.0, 79.6875)])


def test_collection_as_dataframe():
    p1 = Path.from_tuple_list([(100, 101), (200, 201), (300, 301)])
    p2 = Path.from_tuple_list([(222, 223), (333, 334), (333, 334), (333, 334)])
    p3 = Path.from_tuple_list([(222, 223)])

    pc = Collection()
    pc.add([p1, p2, p3])

    df = pc.as_dataframe()  # concatenated
    assert df.ndim == 2
    assert df.values.shape[0] == 4
    # the maximum numer of points in a path (rest are filled up with nan's)
    assert df.values.shape[1] == 6  # 3 times x, y columns


def disabled_test_collection_as_array_performance():
    c = Collection()
    for pa in range(10000):
        p1 = Path()

        for i in range(1000):
            p1.add(random.randint(-10000, 10000), random.randint(-10000, 10000))
        c.add(p1)

    timer = Timer()
    timer.start()
    arr = c.as_array()
    timer.print_elapsed(f"as_array {len(c)} {len(c[0])}")

    assert arr.shape[0] == 10000


def test_simplify_collection():
    random.seed(0)
    c = Collection()
    for pa in range(10):
        p1 = Path()

        for i in range(100):
            p1.add(random.random(), random.random())
        c.add(p1)

    assert c.point_count() == 1000
    timer = Timer()
    timer.start()
    c.simplify(0.1)
    timer.print_elapsed(f"simplify {len(c)} {len(c[0])}")

    assert c.point_count() == 881


def test_simplify_performance():
    random.seed(0)
    c = Collection()
    for pa in range(100):
        p1 = Path()

        for i in range(1000):
            p1.add(random.random(), random.random())
        c.add(p1)

    assert c.point_count() == 100000

    timer = Timer()
    timer.start()

    c.simplify(0.1)

    timer.print_elapsed(f"simplify {len(c)} {len(c[0])}")


def test_path_aspect_ratio():
    p = Path()
    p.add(0, 0)
    p.add(100, 50)

    aspect_ratio = p.aspect_ratio()

    assert aspect_ratio == 0.5


def test_path_aspect_ratio_inf():
    p = Path()
    p.add(0, 0)

    assert p.aspect_ratio() == 0.0

    p.add(1, 0)

    aspect_ratio = p.aspect_ratio()

    assert aspect_ratio == -math.inf


def test_pathcollection_add():
    pcol = Collection()

    assert pcol.empty() is True

    p1 = Path()

    pcol.add(p1)

    assert not pcol.empty()


def test_pathcollection_add2():
    pcol1 = Collection()
    p1 = Path()
    p1.add(5, 5111)
    p1.add(10, 11)
    pcol1.add(p1)

    pcol2 = Collection()
    p2 = Path()
    p2.add(545, 54)
    p2.add(160, 11)
    pcol2.add(p2)

    pcol3 = pcol1 + pcol2

    assert len(pcol3) == 2

    pcol4 = pcol1 + pcol2.get_all() + pcol2.get_all()

    assert len(pcol4) == 3


def test_collection_add3():
    # adding collection to collection

    c1 = Collection()
    p1 = Path()
    p1.add(5, 5111)
    p1.add(10, 11)
    c1.add(p1)

    c2 = Collection()
    p2 = Path()
    p2.add(545, 54)
    p2.add(160, 11)
    c2.add(p2)

    assert len(c1) == 1
    c1.add(c2)
    assert len(c1) == 2


def test_pathcollection_get():
    pcol = Collection()

    p1 = Path()

    p1.add(5, 5111)
    p1.add(40, 41)

    pcol.add(p1)

    p2 = pcol[0]

    assert p1 == p2

    with pytest.raises(IndexError):
        _ = pcol[1]


def test_pathcollection_compare():
    pcol = Collection()
    p1 = Path()

    p1.add(5, 5111)
    p1.add(40, 41)

    pcol.add(p1)

    pcol2 = Collection()
    r = pcol == pcol2

    assert not r


def test_pathcollection_clean():
    pcol = Collection()
    p0 = Path()

    p0.add(5, 5111)

    p1 = Path()

    p1.add(5, 5111)
    p1.add(40, 41)
    p1.add(30, 41)

    pcol.add(p0)
    pcol.add(p1)

    assert len(pcol) == 2

    pcol.clean()

    assert len(pcol) == 1


def test_pathcollection_translate():
    pcol = Collection()
    p0 = Path()

    p0.add(5, -80)

    p1 = Path()
    p1.add(-10, 500)
    p1.add(40, 41)

    pcol.add(p0)
    pcol.add(p1)

    pcol.translate(15, -21)

    assert pcol[0][0].x == 20
    assert pcol[0][0].y == -101

    assert pcol[1][0].x == 5
    assert pcol[1][0].y == 479
    assert pcol[1][1].x == 55
    assert pcol[1][1].y == 20


def test_pathcollection_scale():
    pcol = Collection()
    p0 = Path()

    p0.add(5, -80)

    p1 = Path()
    p1.add(-10, 500)
    p1.add(40, 41)

    pcol.add(p0)
    pcol.add(p1)

    pcol.scale(-2, 2)

    assert pcol[0][0].x == -10
    assert pcol[0][0].y == -160

    assert pcol[1][0].x == 20
    assert pcol[1][0].y == 1000
    assert pcol[1][1].x == -80
    assert pcol[1][1].y == 82


def test_pathcollection_fit1():
    pcol = Collection()
    p0 = Path()

    p0.add(0, 0)
    p0.add(100, 100)

    pcol.add(p0)

    pcol.fit(BoundingBox(0, 0, 50, 50), padding_units=10)

    assert pcol.bb().x == 10
    assert pcol.bb().y == 10
    assert pcol.bb().w == 30
    assert pcol.bb().h == 30


def test_pathcollection_fit2():
    pcol = Collection()
    p0 = Path()

    p0.add(0, 0)
    p0.add(100, 100)

    pcol.add(p0)

    pcol.translate(random.randint(-1000, 1000), random.randint(-1000, 1000))

    pcol.fit(BoundingBox(0, 0, 50, 50), padding_units=10)

    assert pcol.bb().x == 10
    assert pcol.bb().y == 10
    assert pcol.bb().w == 30
    assert pcol.bb().h == 30


def test_pathcollection_fit3():
    pcol = Collection()
    p0 = Path()

    p0.add(0, 0)
    p0.add(100, 100)

    pcol.add(p0)

    pcol.translate(random.randint(-1000, 1000), random.randint(-1000, 1000))

    pcol.fit(BoundingBox(0, 0, 50, 50), padding_units=10)

    assert pcol.bb().x == 10
    assert pcol.bb().y == 10
    assert pcol.bb().w == 30
    assert pcol.bb().h == 30


def test_pathcollection_fit4():
    pcol = Collection()
    p0 = Path()

    p0.add(0, 0)
    p0.add(100, 100)

    pcol.add(p0)

    pcol.translate(random.randint(-1000, 1000), random.randint(-1000, 1000))

    pcol.fit(BoundingBox(0, 0, 50, 50), padding_units=10)

    pcol.translate(random.randint(-1000, 1000), random.randint(-1000, 1000))

    pcol.fit(BoundingBox(0, 0, 50, 50), padding_units=10)
    pcol.fit(BoundingBox(0, 0, 50, 50), padding_units=10)
    pcol.fit(BoundingBox(0, 0, 50, 50), padding_units=10)

    assert pcol.bb().x == 10
    assert pcol.bb().y == 10
    assert pcol.bb().w == 30
    assert pcol.bb().h == 30


def test_pathcollection_fit5():
    pcol = Collection()

    p0 = Path()
    p0.add(10, 10)
    p0.add(90, 90)
    pcol.add(p0)

    p1 = Path()
    p1.add(0, 0)
    p1.add(100, 100)
    pcol.add(p1)

    pcol.fit(BoundingBox(0, 0, 100, 100), xy_factor=(1, 1), padding_mm=0, cutoff_mm=10)

    assert len(pcol) == 1


def test_pathcollection_reverse():
    pcol = Collection()

    p0 = Path()
    p0.add(10, 10)
    p0.add(90, 90)
    pcol.add(p0)

    p1 = Path()
    p1.add(0, 0)
    p1.add(100, 100)
    pcol.add(p1)

    assert pcol[0] == p0
    assert pcol[1] == p1

    pcol.reverse()

    assert pcol[0] == p1
    assert pcol[1] == p0


def test_pathcollection_layer():
    pcol = Collection()
    p0 = Path(properties={Property.LAYER: "custom"})
    p0.add(5, 5111)
    p1 = Path()
    p1.add(5, 5111)

    p3 = Path()
    p3.add(5, 5111)

    pcol.add(p0)
    pcol.add(p1)
    pcol.add(p3)

    layers = pcol.layer_names()
    assert len(layers) == 2

    v = pcol.get_layers()

    assert len(v["layer1"]) == 2
    assert len(v["custom"]) == 1


def test_collection_limit():
    c = Collection()

    for i in range(10):
        p = Path()

        p.add(0.9, 0.9, 0)
        p.add(0.9, 1.0, 0)
        p.add(0.9, 1.1, 0)
        p.add(0.1, 0.8, 0)
        p.add(-0.1, 0.8, 0)
        p.add(0.0, 0.0, 0)
        p.add(1.0, 1.0, 0)

        c.add(p)

    c.limit()

    for p in c:
        assert len(p) == 5


def test_collection_travel_distance():
    c = Collection()
    c.add(Path([Position(0, 0), Position(10, 0), Position(10, 10)]))
    dist = c.calc_pen_down_distance(40)
    assert dist == 0.5

    dist = Collection().calc_pen_down_distance(40)
    assert dist == 0.0


def test_pathcollection_line_types():
    p1 = Path(properties={Property.LINE_TYPE: 1})
    p1.add(0, 0)

    p2 = Path(properties={Property.LINE_TYPE: 2})
    p2.add(0, 0)

    p3 = Path(properties={Property.LINE_TYPE: 3})
    p3.add(0, 0)

    p4 = Path(properties={Property.LINE_TYPE: 4})
    p4.add(0, 0)

    p5 = Path(properties={Property.LINE_TYPE: 4})
    p5.add(0, 0)

    pc = Collection()
    pc.add(p1)
    pc.add(p2)
    pc.add(p3)
    pc.add(p4)
    pc.add(p5)

    line_types = pc.get_all_line_types()
    assert line_types == [1, 2, 3, 4]


def test_reorder_custom():
    p0 = Path()
    p0.add(0, 0)
    p0.add(1, 0)
    p0.add(2, 0)
    p0.add(3, 0)
    p0.add(4, 0)

    p1 = Path()
    p1.add(2, 2)
    p1.add(2, 3)
    p1.add(2, 4)
    p1.add(2, 5)
    p1.add(2, 6)

    p2 = Path()
    p2.add(20, 20)
    p2.add(25, 20)
    p2.add(27, 20)
    p2.add(30, 20)
    p2.add(40, 20)

    p3 = Path()
    p3.add(50, 50)
    p3.add(50, 60)
    p3.add(50, 70)
    p3.add(50, 80)
    p3.add(50, 90)
    p3.add(100, 100)

    p4 = Path()
    p4.add(1, 0)
    p4.add(3, 3)
    p4.add(4, 4)
    p4.add(5, 5)
    p4.add(1, 0)

    pc = Collection()
    pc.add(p0)
    pc.add(p1)
    pc.add(p2)
    pc.add(p3)
    pc.add(p4)

    pc.reorder_quadrants(3, 3)

    assert pc[0] == p0
    assert pc[1] == p1
    assert pc[2] == p2
    assert pc[3] == p4
    assert pc[4] == p3


def test_reorder_quadrants():
    p0 = Path.from_tuple_list([(1, 1), (1, 1)])
    p1 = Path.from_tuple_list([(1, 10), (1, 10)])
    p2 = Path.from_tuple_list([(10, 1), (10, 1)])
    p3 = Path.from_tuple_list([(5, 5), (5, 5)])
    p4 = Path.from_tuple_list([(1, 1.1), (1, 1.1)])

    pc = Collection.from_path_list([p0, p1, p2, p3, p4])

    pc.reorder_quadrants(10, 10)

    assert pc[0] == p1
    assert pc[1] == p2
    assert pc[2] == p0
    assert pc[3] == p4
    assert pc[4] == p3


def test_reorder_quadrants2():
    pc = Collection()
    import random

    for i in range(100):
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        p = Path()
        p.add(x, y)
        p.add(x, y)
        pc.add(p)

    pc.reorder_quadrants(10, 10)

    assert len(pc) == 100


def DISABLED_test_tsp_performances():
    random.seed(1)
    points = 100

    c = Collection()
    [
        c.add(
            Path.from_tuple_list(
                [
                    (random.uniform(0, 100), random.uniform(0, 100)),
                    (random.uniform(0, 100), random.uniform(0, 100)),
                ]
            )
        )
        for _ in range(points)
    ]

    c1 = c.copy()
    # order1 = c1.sort_tsp(iters=100)
    profile.runctx("c1.sort_tsp(iters=50)", globals(), locals())

    c2 = c.copy()
    # order2 = c2.fast_tsp()
    profile.runctx("c2.fast_tsp()", globals(), locals())


def test_sort_tsp():
    p0 = Path.from_tuple_list([(1, 1), (2, 1), (5, 10)])
    p1 = Path.from_tuple_list([(1, 10), (1, 5), (5, 2)])
    p2 = Path.from_tuple_list([(10, 1), (10, 10), (20, 1)])
    p3 = Path.from_tuple_list([(1, 5), (1, 2)])
    p4 = Path.from_tuple_list([(5, 5), (5, 8), (0, 0)])

    pc = Collection.from_path_list([p0, p1, p2, p3, p4])

    order = pc.sort_tsp(iters=50)

    assert order == [0, 1, 2, 4, 3]
    assert pc[0] == p0
    assert pc[1] == p1
    assert pc[2] == p2
    assert pc[3] == p4
    assert pc[4] == p3


def test_fast_tsp():
    p0 = Path.from_tuple_list([(1, 1), (2, 1), (5, 1)])
    p1 = Path.from_tuple_list([(5, 1), (1, 5), (10, 1)])
    p2 = Path.from_tuple_list([(1, 1), (1, 1), (2, 1)])
    p3 = Path.from_tuple_list([(2, 1), (1, 2)])
    p4 = Path.from_tuple_list([(1, 2), (5, 8), (1, 1)])

    pc = Collection.from_path_list([p0, p1, p2, p3, p4])

    order = pc.fast_tsp(plot_preview=False, duration_seconds=5)
    # its non-deterministic

    assert order == [0, 2, 4, 3, 1]
    assert pc[0] == p0
    assert pc[1] == p2
    assert pc[2] == p4
    assert pc[3] == p3
    assert pc[4] == p1
