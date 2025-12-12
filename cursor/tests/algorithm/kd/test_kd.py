from cursor.algorithm.kd.kd import KDTree
from cursor.path import Path


def test_none():
    kd_tree = KDTree([], 2)
    nearest = kd_tree.get_nearest((3, 4), False)
    assert not nearest


def test_simple():
    path = Path.from_tuple_list([(0, 0), (1, 1), (2, 3), (3, 1), (1, 5)])

    kd_tree = KDTree(path.as_tuple_list(), 2)
    kd_tree.add_point((4, 4))

    nearest = kd_tree.get_nearest((3, 4), False)
    assert nearest == ((4, 4), None)

    nearest_with_distance = kd_tree.get_nearest((3, 4), True)
    assert nearest_with_distance == (1, ((4, 4), None))


def test_properties():
    points_with_props = [((0, 0), {"color": "red"}), ((1, 0), {"color": "blue"})]
    tree = KDTree(points_with_props, dim=2)

    tree.add_point((1, 2), {"label": "A"})

    nearest = tree.get_nearest((1, 2))
    assert nearest == (0, ((1, 2), {"label": "A"}))
