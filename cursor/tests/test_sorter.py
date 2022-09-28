from cursor.sorter import Sorter
from cursor.sorter import SortParameter

from cursor.data import DataDirHandler
from cursor.loader import Loader
from cursor.path import Path
from cursor.collection import Collection

import random


def test_sort_simple():
    c = Collection()

    for i in range(500):
        p = Path()
        for _ in range(1000):
            p.add(random.randint(-100, 100), random.randint(-100, 100))
        c.add(p)

    s = Sorter(param=SortParameter.ENTROPY_X)
    c.sort(s)

    for i in range(len(c) - 1):
        p0 = c[i]
        p1 = c[i + 1]

        assert p0.entropy_x <= p1.entropy_x


def test_entropy_sort():
    c = Collection()

    for i in range(100):
        p = Path()
        for _ in range(100):
            p.add(random.randint(-100, 100), random.randint(-100, 100))
        c.add(p)

    s = Sorter(param=SortParameter.ENTROPY_X)
    c.sort(s)

    for i in range(len(c) - 1):
        p0 = c[i]
        p1 = c[i + 1]

        assert p0.entropy_x <= p1.entropy_x

    s.param = SortParameter.ENTROPY_Y
    c.sort(s)

    for i in range(len(c) - 1):
        p0 = c[i]
        p1 = c[i + 1]

        assert p0.entropy_y <= p1.entropy_y

    s.param = SortParameter.ENTROPY_DIRECTION_CHANGES
    c.sort(s)

    for i in range(len(c) - 1):
        p0 = c[i]
        p1 = c[i + 1]

        assert p0.entropy_direction_changes <= p1.entropy_direction_changes


def test_entropy_sort2():
    loader = Loader(directory=DataDirHandler().test_recordings(), limit_files=2)
    c = loader.all_paths()

    s = Sorter(param=SortParameter.ENTROPY_X, reverse=True)
    c.sort(s)
    for i in range(10):
        print(c[i].hash)

    s = Sorter(param=SortParameter.ENTROPY_Y, reverse=True)
    c.sort(s)
    for i in range(10):
        print(c[i].hash)

    s = Sorter(param=SortParameter.ENTROPY_DIRECTION_CHANGES, reverse=True)
    c.sort(s)
    for i in range(10):
        print(c[i].hash)

    print(1)


def test_sorter_performance():
    c = Collection()

    length = 10  # 10000 = ~2s

    ref = Path()

    for i in range(20):
        ref.add(random.random() * 200, random.random() * 200)

    for i in range(length):
        p = Path()
        for j in range(20):
            p.add(random.random() * 200, random.random() * 200)
        c.add(p)

    c.add(ref)

    s = Sorter(reverse=False, param=SortParameter.FRECHET_DISTANCE)

    new_c = c.sorted(s, ref)

    assert len(new_c) == length + 1
    assert new_c[0].vertices == ref.vertices
