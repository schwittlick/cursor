from cursor.collection import Collection
from cursor.renderer import PathIterator


def test_pathiterator():
    pc = Collection.from_tuples([[(0, 0), (1, 0)], [(0, 1), (1, 1), (1, -1)]])

    pi = PathIterator(pc)
    sum_p = sum(1 for _ in pi.points())
    assert sum_p == 5

    sum_c = sum(1 for _ in pi.connections())
    assert sum_c == 3


def test_pathiterator2():
    pc = Collection.from_tuples([[(0, 0)], [(0, 1), (1, 1), (1, -1)]])

    pi = PathIterator(pc)
    sum_p = sum(1 for _ in pi.points())
    assert sum_p == 4

    sum_c = sum(1 for _ in pi.connections())
    assert sum_c == 2
