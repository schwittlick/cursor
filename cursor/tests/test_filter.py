from cursor.data import DataDirHandler
from cursor.loader import Loader
from cursor.path import Path
from cursor.path import PathCollection
from cursor.path import BoundingBox
from cursor.filter import Filter
from cursor.filter import BoundingBoxFilter
from cursor.filter import MinPointCountFilter
from cursor.filter import MaxPointCountFilter
from cursor.filter import Sorter
from cursor.filter import DistanceFilter

import pytest
import random


def test_bb_filter():
    pcol = PathCollection()

    p1 = Path()

    p1.add(5, 51, 10000)
    p1.add(10, 11, 10001)
    p1.add(11, 11, 10002)
    p1.add(20, 20, 10003)
    p1.add(30, 31, 10004)
    p1.add(40, 41, 10005)

    p2 = Path()

    p2.add(545, 54, 10000)
    p2.add(160, 11, 10001)
    p2.add(11, 171, 10002)
    p2.add(20, 20, 10003)
    p2.add(30, 31, 10004)
    p2.add(940, 941, 10005)

    pcol.add(p1)
    pcol.add(p2)

    assert len(pcol) == 2

    f1 = Filter()
    with pytest.raises(Exception):
        pcol.filter(f1)

    bb = BoundingBox(0, 0, 100, 100)
    f2 = BoundingBoxFilter(bb)
    pcol.filter(f2)

    assert len(pcol) == 1
    assert pcol[0] is p1


def test_point_count_filter():
    pcol = PathCollection()

    p1 = Path()

    p1.add(5, 51, 10000)
    p1.add(10, 11, 10001)
    p1.add(11, 11, 10002)
    p1.add(20, 20, 10003)
    p1.add(30, 31, 10004)
    p1.add(40, 41, 10005)

    p2 = Path()

    p2.add(545, 54, 10000)
    p2.add(160, 11, 10001)
    p2.add(11, 171, 10002)
    p2.add(20, 20, 10003)
    p2.add(30, 31, 10004)

    pcol.add(p1)
    pcol.add(p2)

    min_filter = MinPointCountFilter(6)
    pcol.filter(min_filter)

    assert len(pcol) == 1
    assert pcol[0] is p1

    max_filter = MaxPointCountFilter(4)
    pcol.filter(max_filter)

    assert len(pcol) == 0


def test_entropy_sort():
    pcol = PathCollection()

    for i in range(100):
        p = Path()
        for _ in range(100):
            p.add(random.randint(-100, 100), random.randint(-100, 100))
        pcol.add(p)

    sorter = Sorter(param=Sorter.SHANNON_X)
    pcol.sort(sorter)

    for i in range(len(pcol) - 1):
        p0 = pcol[i]
        p1 = pcol[i + 1]

        assert p0.shannon_x <= p1.shannon_x

    sorter.param = Sorter.SHANNON_Y
    pcol.sort(sorter)

    for i in range(len(pcol) - 1):
        p0 = pcol[i]
        p1 = pcol[i + 1]

        assert p0.shannon_y <= p1.shannon_y

    sorter.param = Sorter.SHANNON_DIRECTION_CHANGES
    pcol.sort(sorter)

    for i in range(len(pcol) - 1):
        p0 = pcol[i]
        p1 = pcol[i + 1]

        assert p0.shannon_direction_changes <= p1.shannon_direction_changes


def test_entropy_sort2():
    pcol = PathCollection()
    dir = DataDirHandler().test_recordings()
    ll = Loader(directory=dir, limit_files=2)
    pcol = ll.all_paths()
    sorter = Sorter(param=Sorter.SHANNON_X, reverse=True)
    pcol.sort(sorter)
    for i in range(10):
        print(pcol[i].hash)

    sorter = Sorter(param=Sorter.SHANNON_Y, reverse=True)
    pcol.sort(sorter)
    for i in range(10):
        print(pcol[i].hash)

    sorter = Sorter(param=Sorter.SHANNON_DIRECTION_CHANGES, reverse=True)
    pcol.sort(sorter)
    for i in range(10):
        print(pcol[i].hash)

    print(1)


def test_distance_filter():
    pcol = PathCollection()

    p1 = Path()

    p1.add(0, 0)
    p1.add(10, 0, 0)

    p2 = Path()

    p2.add(0, 0)
    p2.add(20, 0, 0)

    pcol.add(p1)
    pcol.add(p2)

    assert len(pcol) == 2

    filter = DistanceFilter(15)
    pcol.filter(filter)

    assert len(pcol) == 1
