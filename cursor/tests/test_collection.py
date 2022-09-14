from cursor.path import Path
from cursor.collection import Collection
from cursor.bb import BoundingBox
from cursor.misc import Timer

import pytest
import random
import math


def test_pathcollection_minmax():
    pcol = Collection()

    p1 = Path()

    p1.add(5, 5111)
    p1.add(10, 11)
    p1.add(11, 11)
    p1.add(20, 20)
    p1.add(30, 31)
    p1.add(40, 41)

    p2 = Path()

    p2.add(545, 54)
    p2.add(160, 11)
    p2.add(11, 171)
    p2.add(20, 20)
    p2.add(30, 31)
    p2.add(940, 941)

    pcol.add(p1)
    pcol.add(p2)

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


def test_path_aspect_ratio():
    p = Path()
    p.add(0, 0)
    p.add(100, 50)

    aspect_ratio = p.aspect_ratio()

    assert aspect_ratio == 0.5


def test_path_aspect_ratio_nan():
    p = Path()
    p.add(0, 0)

    aspect_ratio = p.aspect_ratio()

    assert aspect_ratio is math.nan

    p.add(1, 0)

    aspect_ratio = p.aspect_ratio()

    assert aspect_ratio is math.nan


def test_pathcollection_add():
    pcol = Collection()

    assert pcol.empty() is True

    p1 = Path()

    pcol.add(p1)

    assert pcol.empty() is True


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

    with pytest.raises(Exception):
        _ = pcol1 + p1


def test_pathcollection_get():
    pcol = Collection()

    p1 = Path()

    p1.add(5, 5111)
    p1.add(40, 41)

    pcol.add(p1)

    p2 = pcol[0]

    assert p1 == p2

    with pytest.raises(IndexError):
        pcol[1]


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

    pcol.fit((50, 50), padding_units=10)

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

    pcol.fit((50, 50), padding_units=10)

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

    pcol.fit((50, 50), padding_units=10)

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

    pcol.fit((50, 50), padding_units=10)

    pcol.translate(random.randint(-1000, 1000), random.randint(-1000, 1000))

    pcol.fit((50, 50), padding_units=10)
    pcol.fit((50, 50), padding_units=10)
    pcol.fit((50, 50), padding_units=10)

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

    pcol.fit((100, 100), xy_factor=(1, 1), padding_mm=0, cutoff_mm=10)

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
    p0 = Path(layer="custom")
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


def test_pathcollection_line_types():
    p1 = Path(line_type=1)
    p1.add(0, 0)

    p2 = Path(line_type=2)
    p2.add(0, 0)

    p3 = Path(line_type=3)
    p3.add(0, 0)

    p4 = Path(line_type=4)
    p4.add(0, 0)

    p5 = Path(line_type=4)
    p5.add(0, 0)

    pc = Collection()
    pc.add(p1)
    pc.add(p2)
    pc.add(p3)
    pc.add(p4)
    pc.add(p5)

    line_types = pc.get_all_line_types()
    assert line_types == [1, 2, 3, 4]
