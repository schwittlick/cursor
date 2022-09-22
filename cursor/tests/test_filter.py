from cursor.data import DataDirHandler
from cursor.loader import Loader
from cursor.path import Path
from cursor.collection import Collection
from cursor.bb import BoundingBox

from cursor.filter import Filter
from cursor.filter import Sorter
from cursor.filter import SortParameter
from cursor.filter import BoundingBoxFilter
from cursor.filter import MinPointCountFilter
from cursor.filter import MaxPointCountFilter
from cursor.filter import DistanceFilter

import pytest
import random


def test_bb_filter():
    pcol = Collection()

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
    pcol = Collection()

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


def test_sort_simple():
    pcol = Collection()

    for i in range(500):
        p = Path()
        for _ in range(1000):
            p.add(random.randint(-100, 100), random.randint(-100, 100))
        pcol.add(p)

    from cursor.misc import Timer

    timer = Timer()
    timer.start()
    sorter = Sorter(param=SortParameter.ENTROPY_X)
    pcol.sort(sorter)
    timer.print_elapsed("sorting differential extropy x")

    for i in range(len(pcol) - 1):
        p0 = pcol[i]
        p1 = pcol[i + 1]

        assert p0.entropy_x <= p1.entropy_x


def test_entropy_sort():
    pcol = Collection()

    for i in range(100):
        p = Path()
        for _ in range(100):
            p.add(random.randint(-100, 100), random.randint(-100, 100))
        pcol.add(p)

    from cursor.misc import Timer

    timer = Timer()
    timer.start()
    sorter = Sorter(param=SortParameter.ENTROPY_X)
    pcol.sort(sorter)
    timer.print_elapsed("sorting shannon x")

    for i in range(len(pcol) - 1):
        p0 = pcol[i]
        p1 = pcol[i + 1]

        assert p0.entropy_x <= p1.entropy_x

    sorter.param = SortParameter.ENTROPY_Y
    pcol.sort(sorter)

    for i in range(len(pcol) - 1):
        p0 = pcol[i]
        p1 = pcol[i + 1]

        assert p0.entropy_y <= p1.entropy_y

    sorter.param = SortParameter.ENTROPY_DIRECTION_CHANGES
    pcol.sort(sorter)

    for i in range(len(pcol) - 1):
        p0 = pcol[i]
        p1 = pcol[i + 1]

        assert p0.entropy_direction_changes <= p1.entropy_direction_changes


def test_entropy_sort2():
    pcol = Collection()
    dir = DataDirHandler().test_recordings()
    ll = Loader(directory=dir, limit_files=2)
    pcol = ll.all_paths()
    sorter = Sorter(param=SortParameter.ENTROPY_X, reverse=True)
    pcol.sort(sorter)
    for i in range(10):
        print(pcol[i].hash)

    sorter = Sorter(param=SortParameter.ENTROPY_Y, reverse=True)
    pcol.sort(sorter)
    for i in range(10):
        print(pcol[i].hash)

    sorter = Sorter(param=SortParameter.ENTROPY_DIRECTION_CHANGES, reverse=True)
    pcol.sort(sorter)
    for i in range(10):
        print(pcol[i].hash)

    print(1)


def test_distance_filter():
    pcol = Collection()

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


def test_filter_performance():
    pcol = Collection()

    length = 10  # 10000 = ~2s

    reference = Path()

    for i in range(20):
        reference.add(random.random() * 200, random.random() * 200)

    for i in range(length):
        p = Path()
        for j in range(20):
            p.add(random.random() * 200, random.random() * 200)
        pcol.add(p)

    pcol.add(reference)

    f = Sorter(reverse=False, param=SortParameter.FRECHET_DISTANCE)

    new_col = pcol.sorted(f, reference)

    assert len(new_col) == length + 1
    assert new_col[0].vertices == reference.vertices
