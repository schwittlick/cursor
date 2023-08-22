from cursor.collection import Collection
from cursor.path import Path


def test_pathiterator():
    pc = Collection()
    p1 = Path()
    p1.add(0, 0)
    p1.add(1, 0)
    p2 = Path()
    p2.add(0, 1)
    p2.add(1, 1)
    p2.add(1, -1)

    pc.add(p1)
    pc.add(p2)

    pi = PathIterator(pc)
    sum_p = sum(1 for _ in pi.points())
    assert sum_p == 5

    sum_c = sum(1 for _ in pi.connections())
    assert sum_c == 3


def test_pathiterator2():
    pc = Collection()
    p1 = Path()
    p1.add(0, 0)
    p2 = Path()
    p2.add(0, 1)
    p2.add(1, 1)
    p2.add(1, -1)

    pc.add(p1)
    pc.add(p2)

    pi = PathIterator(pc)
    sum_p = sum(1 for _ in pi.points())
    assert sum_p == 4

    sum_c = sum(1 for _ in pi.connections())
    assert sum_c == 2
