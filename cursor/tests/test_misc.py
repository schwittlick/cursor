from cursor.bb import BoundingBox
from cursor.path import Path


def test_line_intersect():
    dimension = 500

    f = Path.from_tuple_list([(0, 0), (1, 1), (2, -2), (3, 2), (4, -3), (5, 1), (6, -1), (7, 0)])
    nf = Path.from_tuple_list([(0, 0), (1, 1), (2, -2), (3, 2), (2.5, 2), (5, 1), (6, -1), (7, 0)])

    bb = f.bb()

    f.transform(bb, BoundingBox(0, 0, dimension, dimension))
    nf.transform(bb, BoundingBox(0, 0, dimension, dimension))

    intersections_functional = f.is_functional(0.01)
    intersections_non_functional = nf.is_functional(0.01)

    is_functional1 = all(len(ele) == 1 for ele in intersections_functional)
    is_functional2 = all(len(ele) == 1 for ele in intersections_non_functional)

    assert is_functional1
    assert not is_functional2
