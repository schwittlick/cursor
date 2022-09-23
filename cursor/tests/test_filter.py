from cursor.path import Path
from cursor.collection import Collection
from cursor.bb import BoundingBox

from cursor.filter import Filter
from cursor.filter import BoundingBoxFilter
from cursor.filter import MinPointCountFilter
from cursor.filter import MaxPointCountFilter
from cursor.filter import DistanceFilter

import pytest


def test_bb_filter():
    c = Collection()

    p1 = Path.from_tuple_list(
        [(5, 51), (10, 11), (11, 11), (20, 20), (30, 31), (40, 41)]
    )

    p2 = Path.from_tuple_list(
        [(545, 54), (160, 11), (11, 171), (20, 20), (30, 31), (940, 941)]
    )
    c.add(p1)
    c.add(p2)

    assert len(c) == 2

    f1 = Filter()
    with pytest.raises(Exception):
        c.filter(f1)

    f2 = BoundingBoxFilter(BoundingBox(0, 0, 100, 100))
    c.filter(f2)

    assert len(c) == 1
    assert c[0] is p1


def test_point_count_filter():
    c = Collection()

    p1 = Path.from_tuple_list(
        [(5, 51), (10, 11), (11, 11), (20, 20), (30, 31), (40, 41)]
    )
    p2 = Path.from_tuple_list([(545, 54), (160, 11), (11, 171), (20, 20), (30, 31)])

    c.add(p1)
    c.add(p2)

    min_filter = MinPointCountFilter(6)
    c.filter(min_filter)

    assert len(c) == 1
    assert c[0] is p1

    max_filter = MaxPointCountFilter(4)
    c.filter(max_filter)

    assert len(c) == 0


def test_distance_filter():
    c = Collection()

    p1 = Path.from_tuple_list([(0, 0), (10, 0)])
    p2 = Path.from_tuple_list([(0, 0), (20, 0)])

    c.add(p1)
    c.add(p2)

    assert len(c) == 2

    f = DistanceFilter(15)
    c.filter(f)

    assert len(c) == 1
