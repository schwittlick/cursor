from cursor import misc
from cursor.bb import BoundingBox
from cursor.path import Path

import numpy as np


def test_line_intersect_parallel():
    ray_origin = np.array((0, 0))
    ray_dir = np.array((0, 1))

    seg_start = np.array((1, 1))
    seg_end = np.array((1, 2))

    intersected = misc.line_intersection(ray_origin, ray_dir, seg_start, seg_end)
    assert intersected is None


def test_line_intersect():
    dimension = 500

    f = Path.from_tuple_list([(0, 0), (1, 1), (2, -2), (3, 2), (4, -3), (5, 1), (6, -1), (7, 0)])
    nf = Path.from_tuple_list([(0, 0), (1, 1), (2, -2), (3, 2), (2.5, 2), (5, 1), (6, -1), (7, 0)])

    bb = f.bb()

    f.transform(bb, BoundingBox(0, 0, dimension, dimension))
    nf.transform(bb, BoundingBox(0, 0, dimension, dimension))

    is_func1, intersections_functional = f.is_functional(0.01)
    is_func2, intersections_non_functional = nf.is_functional(0.01)

    is_functional1 = all(len(ele) == 1 for ele in intersections_functional)
    is_functional2 = all(len(ele) == 1 for ele in intersections_non_functional)

    assert is_functional1
    assert is_functional1 is is_func1
    assert not is_functional2
    assert is_functional2 is is_func2
