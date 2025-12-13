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


def test_size():
    # Test with empty tree
    tree = KDTree([], 2)
    assert tree.size() == 0

    # Test with a few points
    points = [((0, 0), None), ((1, 1), None), ((2, 2), None)]
    tree = KDTree(points, 2)
    assert tree.size() == 3

    # Test adding points
    tree.add_point((3, 3))
    assert tree.size() == 4

    # Test with 1,000,000 points
    import random

    random.seed(42)
    large_points = [((random.uniform(0, 1000), random.uniform(0, 1000)), {"id": i}) for i in range(1000000)]
    large_tree = KDTree(large_points, 2)
    assert large_tree.size() == 1000000

    # Add more points and verify size updates
    large_tree.add_point((500, 500), {"id": 1000000})
    assert large_tree.size() == 1000001
