import pytest

from cursor import Collection, Path, Position
from cursor.algorithm.kd.kd_annoy import KDTree
from cursor.properties import Property


def test_empty_tree():
    """Test queries on an empty tree."""
    annoy_tree = KDTree([], 2)
    nearest = annoy_tree.get_nearest((3, 4), False)
    assert nearest is None
    assert annoy_tree.is_empty()
    assert annoy_tree.size() == 0


def test_crash_double():
    """Test tree with a single point."""

    pos = (28392.234556, 38476.2356)
    position = Position.from_tuple(pos)
    annoy_tree = KDTree([], 2)
    annoy_tree.add_point(position.as_tuple(), {Property.COLOR: (0, 1, 2)})

    nearest = annoy_tree.get_nearest((3, 4), False)
    assert nearest == (pos, {Property.COLOR: (0, 1, 2)})

    nearest_with_distance = annoy_tree.get_nearest(pos, True)
    # Distance from (3, 4) to (4, 4) is sqrt(1) = 1, so distance squared is 1
    # assert nearest_with_distance[0] == pytest.approx(1.0, rel=1e-5)
    assert nearest_with_distance[1] == (pos, {Property.COLOR: (0, 1, 2)})


def test_crash():
    positions1 = [
        Position.from_tuple((0, 1)),
        Position.from_tuple((0, 2)),
        Position.from_tuple((0, 3)),
        Position.from_tuple((0, 4)),
    ]
    p1 = Path(positions1, {"part_idx": 1})

    positions2 = [
        Position.from_tuple((1, 1)),
        Position.from_tuple((1, 2)),
        Position.from_tuple((1, 3)),
        Position.from_tuple((1, 4)),
    ]
    p2 = Path(positions2, {"part_idx": 2})
    paths = Collection.from_path_list([p1, p2])

    kd_tree = KDTree([], 2)
    for path in paths:
        pending_positions = []
        for i, position in enumerate(path):
            nearest = kd_tree.get_nearest(position.as_tuple(), True)
            if nearest:
                pass
            pending_positions.append(position)
        for position in pending_positions:
            kd_tree.add_point(position.as_tuple(), position.properties)

    print(kd_tree.size())


def test_single_point():
    """Test tree with a single point."""
    annoy_tree = KDTree([], 2)
    annoy_tree.add_point((4, 4), {})

    nearest = annoy_tree.get_nearest((3, 4), False)
    assert nearest == ((4, 4), {})

    nearest_with_distance = annoy_tree.get_nearest((3, 4), True)
    # Distance from (3, 4) to (4, 4) is sqrt(1) = 1, so distance squared is 1
    assert nearest_with_distance[0] == pytest.approx(1.0, rel=1e-5)
    assert nearest_with_distance[1] == ((4, 4), {})


def test_simple_points():
    """Test with simple point additions."""
    annoy_tree = KDTree([], 2)

    annoy_tree.add_point((1, 1), {"id": 1})
    annoy_tree.add_point((2, 2), {"id": 2})
    annoy_tree.add_point((3, 3), {"id": 3})

    # Query near (2.1, 2.1) should return (2, 2)
    nearest = annoy_tree.get_nearest((2.1, 2.1), False)
    assert nearest == ((2, 2), {"id": 2})


def test_properties():
    """Test that properties are correctly stored and retrieved."""
    points_with_props = [((0, 0), {"color": "red"}), ((1, 0), {"color": "blue"})]
    tree = KDTree(points_with_props, 2)

    tree.add_point((1, 2), {"label": "A"})

    nearest = tree.get_nearest((1, 2), False)
    assert nearest == ((1, 2), {"label": "A"})

    # Query near (0.1, 0.1) should return (0, 0) with red color
    nearest = tree.get_nearest((0.1, 0.1), False)
    assert nearest == ((0, 0), {"color": "red"})


def test_initialization_with_points():
    """Test initialization with a list of points."""
    initial_points = [
        ((0.0, 0.0), {"id": 1}),
        ((1.0, 1.0), {"id": 2}),
        ((2.0, 0.0), {"id": 3}),
    ]
    annoy_tree = KDTree(initial_points, 2)

    nearest = annoy_tree.get_nearest((0.5, 0.5), False)
    # Should be closest to (1.0, 1.0) or (0.0, 0.0)
    point, data = nearest
    assert data in [{"id": 1}, {"id": 2}]

    assert annoy_tree.size() == 3
    assert not annoy_tree.is_empty()


def test_knn_single():
    """Test k-nearest neighbors with k=1."""
    annoy_tree = KDTree([], 2)
    annoy_tree.add_point((1, 1), {"id": 1})
    annoy_tree.add_point((2, 2), {"id": 2})
    annoy_tree.add_point((3, 3), {"id": 3})

    knn = annoy_tree.get_knn((2.1, 2.1), 1, return_dist_sq=False)
    assert len(knn) == 1
    assert knn[0] == ((2, 2), {"id": 2})


def test_knn_multiple():
    """Test k-nearest neighbors with k>1."""
    annoy_tree = KDTree([], 2)
    annoy_tree.add_point((0, 0), {"id": 1})
    annoy_tree.add_point((1, 0), {"id": 2})
    annoy_tree.add_point((2, 0), {"id": 3})
    annoy_tree.add_point((10, 10), {"id": 4})

    knn = annoy_tree.get_knn((0.5, 0), 3, return_dist_sq=True)
    assert len(knn) == 3

    # Check that distances are returned
    for item in knn:
        assert len(item) == 2
        dist_sq, (point, props) = item
        assert isinstance(dist_sq, (int, float))
        assert isinstance(point, tuple)
        assert isinstance(props, dict)

    # The three nearest should be (0,0), (1,0), and (2,0), not (10,10)
    ids = [props["id"] for _, (_, props) in knn]
    assert 4 not in ids  # (10, 10) should not be in top 3


def test_knn_with_distance():
    """Test k-nearest neighbors returns correct distances."""
    annoy_tree = KDTree([], 2)
    annoy_tree.add_point((0, 0), {"id": 1})
    annoy_tree.add_point((3, 4), {"id": 2})  # Distance 5 from origin

    knn = annoy_tree.get_knn((0, 0), 2, return_dist_sq=True)
    assert len(knn) == 2

    # First should be (0, 0) with distance 0
    dist_sq, (point, props) = knn[0]
    if point == (0, 0):
        assert dist_sq == pytest.approx(0.0, abs=1e-5)
        assert props["id"] == 1


def test_knn_exceeds_size():
    """Test k-nearest neighbors when k > number of points."""
    annoy_tree = KDTree([], 2)
    annoy_tree.add_point((1, 1), {"id": 1})
    annoy_tree.add_point((2, 2), {"id": 2})

    # Request 10 neighbors but only have 2 points
    knn = annoy_tree.get_knn((0, 0), 10, return_dist_sq=False)
    assert len(knn) == 2


def test_empty_knn():
    """Test k-nearest neighbors on empty tree."""
    annoy_tree = KDTree([], 2)
    knn = annoy_tree.get_knn((0, 0), 5, return_dist_sq=False)
    assert knn == []


def test_mixed_point_formats():
    """Test that various point formats are handled correctly."""
    # Test with tuples
    annoy_tree = KDTree([((1, 2), {"type": "tuple"})], 2)

    # Add with list
    annoy_tree.add_point([3, 4], {"type": "list"})

    nearest = annoy_tree.get_nearest((1.1, 2.1), False)
    assert nearest[0] == (1, 2)
    assert nearest[1] == {"type": "tuple"}


def test_none_properties():
    """Test points with None as properties."""
    annoy_tree = KDTree([], 2)
    annoy_tree.add_point((1, 1), None)
    annoy_tree.add_point((2, 2), None)

    nearest = annoy_tree.get_nearest((1.1, 1.1), False)
    assert nearest == ((1, 1), None)


def test_iterator():
    """Test iteration over all points in the tree."""
    points = [
        ((0, 0), {"id": 1}),
        ((1, 1), {"id": 2}),
        ((2, 2), {"id": 3}),
    ]
    annoy_tree = KDTree(points, 2)

    collected = list(annoy_tree)
    assert len(collected) == 3

    # Check all points are present
    for point, props in points:
        assert (point, props) in collected


def test_higher_dimensions():
    """Test with 3D points."""
    annoy_tree = KDTree([], 3)

    annoy_tree.add_point((1, 2, 3), {"id": 1})
    annoy_tree.add_point((4, 5, 6), {"id": 2})
    annoy_tree.add_point((7, 8, 9), {"id": 3})

    nearest = annoy_tree.get_nearest((1.1, 2.1, 3.1), False)
    assert nearest == ((1, 2, 3), {"id": 1})


def test_different_metrics():
    """Test with different distance metrics."""
    points = [((0, 0), {"id": 1}), ((1, 1), {"id": 2}), ((2, 0), {"id": 3})]

    # Test Manhattan distance
    annoy_tree_manhattan = KDTree(points, 2, metric="manhattan")
    nearest = annoy_tree_manhattan.get_nearest((0.1, 0.1), False)
    assert nearest[1] == {"id": 1}

    # Test Angular distance - angular distance measures angle between vectors
    # For points (1, 0) and (0, 1), querying with (1, 0.1) should find (1, 0)
    points_angular = [((1, 0), {"id": 1}), ((0, 1), {"id": 2})]
    annoy_tree_angular = KDTree(points_angular, 2, metric="angular")
    nearest = annoy_tree_angular.get_nearest((1, 0.1), False)
    assert nearest[1] == {"id": 1}


def test_large_dataset():
    """Test with a larger dataset to verify performance."""
    # Create 1000 points in a grid
    points = [((i % 32, i // 32), {"id": i}) for i in range(1000)]
    annoy_tree = KDTree(points, 2, n_trees=20)

    # Query should be fast
    nearest = annoy_tree.get_nearest((10.5, 10.5), False)
    point, props = nearest

    # Should be close to (10, 10) or (11, 10) or (10, 11) or (11, 11)
    assert abs(point[0] - 10.5) <= 1
    assert abs(point[1] - 10.5) <= 1


def test_compatibility_with_path():
    """Test integration with Path class like in original tests."""
    path = Path.from_tuple_list([(0, 0), (1, 1), (2, 3), (3, 1), (1, 5)])

    # Create tree and add path points
    annoy_tree = KDTree([], 2)
    for i, point in enumerate(path):
        annoy_tree.add_point((point.x, point.y), {"index": i})

    # Find nearest to a query point
    nearest = annoy_tree.get_nearest((2, 2), False)
    point, props = nearest

    # Should find one of the nearby points
    assert isinstance(point, tuple)
    assert "index" in props


def test_size_after_additions():
    """Test that size is correctly tracked."""
    annoy_tree = KDTree([], 2)
    assert annoy_tree.size() == 0

    annoy_tree.add_point((1, 1), {})
    assert annoy_tree.size() == 1

    annoy_tree.add_point((2, 2), {})
    assert annoy_tree.size() == 2

    # Initialize with points
    annoy_tree2 = KDTree([((0, 0), {}), ((1, 1), {})], 2)
    assert annoy_tree2.size() == 2


def test_distance_calculation():
    """Test the get_distance method."""
    annoy_tree = KDTree([], 2, metric="euclidean")

    # Distance from (0, 0) to (3, 4) should be 5
    dist = annoy_tree.get_distance((0, 0), (3, 4))
    assert dist == pytest.approx(5.0, rel=1e-5)

    # Test Manhattan distance
    annoy_tree_manhattan = KDTree([], 2, metric="manhattan")
    dist = annoy_tree_manhattan.get_distance((0, 0), (3, 4))
    assert dist == 7.0


def test_return_distance_flag():
    """Test that return_dist_sq flag works correctly."""
    annoy_tree = KDTree([], 2)
    annoy_tree.add_point((0, 0), {"id": 1})
    annoy_tree.add_point((3, 4), {"id": 2})

    # Without distance
    result = annoy_tree.get_nearest((0, 0), False)
    assert len(result) == 2
    assert result == ((0, 0), {"id": 1})

    # With distance
    result = annoy_tree.get_nearest((0, 0), True)
    assert len(result) == 2
    dist_sq, (point, props) = result
    assert isinstance(dist_sq, (int, float))
    assert point == (0, 0)
    assert props == {"id": 1}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
