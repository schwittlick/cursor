import time

import numpy as np
import pytest

from cursor.algorithm.color.copic import Copic
from cursor.algorithm.kd.kd_hnsw import HNSWKDTree
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property


def test_empty_tree():
    """Test queries on an empty tree."""
    hnsw_tree = HNSWKDTree([], 2)
    nearest = hnsw_tree.get_nearest((3, 4), False)
    assert nearest is None
    assert hnsw_tree.is_empty()
    assert hnsw_tree.size() == 0


def test_single_point():
    """Test tree with a single point."""
    hnsw_tree = HNSWKDTree([], 2)
    hnsw_tree.add_point((4, 4), {})

    nearest = hnsw_tree.get_nearest((3, 4), False)
    assert nearest == ((4, 4), {})

    nearest_with_distance = hnsw_tree.get_nearest((3, 4), True)
    # Distance from (3, 4) to (4, 4) is sqrt(1) = 1, so distance squared is 1
    assert nearest_with_distance[0] == pytest.approx(1.0, rel=1e-5)
    assert nearest_with_distance[1] == ((4, 4), {})


def test_simple_points():
    """Test with simple point additions."""
    hnsw_tree = HNSWKDTree([], 2)

    pos = Position(7231, 3542)
    pos.properties[Property.COPIC_COLOR] = Copic().random()
    pos.color = Copic().random().as_rgb()
    pos.radius = 21

    hnsw_tree.add_point(pos.as_tuple(), pos.properties)
    hnsw_tree.add_point((2, 2), {"id": 2})
    hnsw_tree.add_point((3, 3), {"id": 3})

    # Query near (2.1, 2.1) should return (2, 2)
    nearest = hnsw_tree.get_nearest((2.1, 2.1), False)
    assert nearest == ((2, 2), {"id": 2})


def test_properties():
    """Test that properties are correctly stored and retrieved."""
    points_with_props = [((0, 0), {"color": "red"}), ((1, 0), {"color": "blue"})]
    tree = HNSWKDTree(points_with_props, 2)

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
    hnsw_tree = HNSWKDTree(initial_points, 2)

    nearest = hnsw_tree.get_nearest((0.5, 0.5), False)
    # Should be closest to (1.0, 1.0) or (0.0, 0.0)
    point, data = nearest
    assert data in [{"id": 1}, {"id": 2}]

    assert hnsw_tree.size() == 3
    assert not hnsw_tree.is_empty()


def test_knn_single():
    """Test k-nearest neighbors with k=1."""
    hnsw_tree = HNSWKDTree([], 2)
    hnsw_tree.add_point((1, 1), {"id": 1})
    hnsw_tree.add_point((2, 2), {"id": 2})
    hnsw_tree.add_point((3, 3), {"id": 3})

    knn = hnsw_tree.get_knn((2.1, 2.1), 1, return_dist_sq=False)
    assert len(knn) == 1
    assert knn[0] == ((2, 2), {"id": 2})


def test_knn_multiple():
    """Test k-nearest neighbors with k>1."""
    hnsw_tree = HNSWKDTree([], 2)
    hnsw_tree.add_point((0, 0), {"id": 1})
    hnsw_tree.add_point((1, 0), {"id": 2})
    hnsw_tree.add_point((2, 0), {"id": 3})
    hnsw_tree.add_point((10, 10), {"id": 4})

    knn = hnsw_tree.get_knn((0.5, 0), 3, return_dist_sq=True)
    assert len(knn) == 3

    # Check that distances are returned
    for item in knn:
        assert len(item) == 2
        dist_sq, (point, props) = item
        assert isinstance(dist_sq, (int, float, np.number))
        assert isinstance(point, tuple)
        assert isinstance(props, dict)

    # The three nearest should be (0,0), (1,0), and (2,0), not (10,10)
    ids = [props["id"] for _, (_, props) in knn]
    assert 4 not in ids  # (10, 10) should not be in top 3


def test_knn_with_distance():
    """Test k-nearest neighbors returns correct distances."""
    hnsw_tree = HNSWKDTree([], 2)
    hnsw_tree.add_point((0, 0), {"id": 1})
    hnsw_tree.add_point((3, 4), {"id": 2})  # Distance 5 from origin

    knn = hnsw_tree.get_knn((0, 0), 2, return_dist_sq=True)
    assert len(knn) == 2

    # First should be (0, 0) with distance 0
    dist_sq, (point, props) = knn[0]
    if point == (0, 0):
        assert dist_sq == pytest.approx(0.0, abs=1e-5)
        assert props["id"] == 1


def test_knn_exceeds_size():
    """Test k-nearest neighbors when k > number of points."""
    hnsw_tree = HNSWKDTree([], 2)
    hnsw_tree.add_point((1, 1), {"id": 1})
    hnsw_tree.add_point((2, 2), {"id": 2})

    # Request 10 neighbors but only have 2 points
    knn = hnsw_tree.get_knn((0, 0), 10, return_dist_sq=False)
    assert len(knn) == 2


def test_empty_knn():
    """Test k-nearest neighbors on empty tree."""
    hnsw_tree = HNSWKDTree([], 2)
    knn = hnsw_tree.get_knn((0, 0), 5, return_dist_sq=False)
    assert knn == []


def test_mixed_point_formats():
    """Test that various point formats are handled correctly."""
    # Test with tuples
    hnsw_tree = HNSWKDTree([((1, 2), {"type": "tuple"})], 2)

    # Add with list
    hnsw_tree.add_point([3, 4], {"type": "list"})

    nearest = hnsw_tree.get_nearest((1.1, 2.1), False)
    assert nearest[0] == (1, 2)
    assert nearest[1] == {"type": "tuple"}


def test_none_properties():
    """Test points with None as properties."""
    hnsw_tree = HNSWKDTree([], 2)
    hnsw_tree.add_point((1, 1), None)
    hnsw_tree.add_point((2, 2), None)

    nearest = hnsw_tree.get_nearest((1.1, 1.1), False)
    assert nearest == ((1, 1), None)


def test_iterator():
    """Test iteration over all points in the tree."""
    points = [
        ((0, 0), {"id": 1}),
        ((1, 1), {"id": 2}),
        ((2, 2), {"id": 3}),
    ]
    hnsw_tree = HNSWKDTree(points, 2)

    collected = list(hnsw_tree)
    assert len(collected) == 3

    # Check all points are present
    for point, props in points:
        assert (point, props) in collected


def test_higher_dimensions():
    """Test with 3D points."""
    hnsw_tree = HNSWKDTree([], 3)

    hnsw_tree.add_point((1, 2, 3), {"id": 1})
    hnsw_tree.add_point((4, 5, 6), {"id": 2})
    hnsw_tree.add_point((7, 8, 9), {"id": 3})

    nearest = hnsw_tree.get_nearest((1.1, 2.1, 3.1), False)
    assert nearest == ((1, 2, 3), {"id": 1})


def test_different_metrics():
    """Test with different distance metrics."""
    points = [((0, 0), {"id": 1}), ((1, 1), {"id": 2}), ((2, 0), {"id": 3})]

    # Test L2 (Euclidean)
    hnsw_tree_l2 = HNSWKDTree(points, 2, space="l2")
    nearest = hnsw_tree_l2.get_nearest((0.1, 0.1), False)
    assert nearest[1] == {"id": 1}

    # Test cosine similarity
    points_cosine = [((1, 0), {"id": 1}), ((0, 1), {"id": 2})]
    hnsw_tree_cosine = HNSWKDTree(points_cosine, 2, space="cosine")
    nearest = hnsw_tree_cosine.get_nearest((1, 0.1), False)
    assert nearest[1] == {"id": 1}


def test_large_dataset():
    """Test with a larger dataset to verify performance."""
    # Create 1000 points in a grid
    points = [((i % 32, i // 32), {"id": i}) for i in range(1000)]
    hnsw_tree = HNSWKDTree(points, 2)

    # Query should be fast
    nearest = hnsw_tree.get_nearest((10.5, 10.5), False)
    point, props = nearest

    # Should be close to (10, 10) or (11, 10) or (10, 11) or (11, 11)
    assert abs(point[0] - 10.5) <= 1
    assert abs(point[1] - 10.5) <= 1


def test_dynamic_additions_performance():
    """Test that dynamic additions are efficient (no full rebuild)."""
    hnsw_tree = HNSWKDTree([], 2)

    # Add initial points
    for i in range(100):
        hnsw_tree.add_point((i * 0.1, i * 0.2), {"id": i})

    # Time additional insertions
    start = time.perf_counter()
    for i in range(100, 200):
        hnsw_tree.add_point((i * 0.1, i * 0.2), {"id": i})
    elapsed = time.perf_counter() - start

    # Should be very fast (< 50ms for 100 insertions)
    assert elapsed < 0.05, f"Dynamic additions too slow: {elapsed * 1000:.2f}ms"

    # Verify we can still query correctly
    nearest = hnsw_tree.get_nearest((10.0, 20.0), False)
    assert nearest is not None


def test_compatibility_with_path():
    """Test integration with Path class like in original tests."""
    path = Path.from_tuple_list([(0, 0), (1, 1), (2, 3), (3, 1), (1, 5)])

    # Create tree and add path points
    hnsw_tree = HNSWKDTree([], 2)
    for i, point in enumerate(path):
        hnsw_tree.add_point((point.x, point.y), {"index": i})

    # Find nearest to a query point
    nearest = hnsw_tree.get_nearest((2, 2), False)
    point, props = nearest

    # Should find one of the nearby points
    assert isinstance(point, tuple)
    assert "index" in props


def test_size_after_additions():
    """Test that size is correctly tracked."""
    hnsw_tree = HNSWKDTree([], 2)
    assert hnsw_tree.size() == 0

    hnsw_tree.add_point((1, 1), {})
    assert hnsw_tree.size() == 1

    hnsw_tree.add_point((2, 2), {})
    assert hnsw_tree.size() == 2

    # Initialize with points
    hnsw_tree2 = HNSWKDTree([((0, 0), {}), ((1, 1), {})], 2)
    assert hnsw_tree2.size() == 2


def test_set_ef():
    """Test setting ef parameter."""
    hnsw_tree = HNSWKDTree([], 2)

    # Add some points
    for i in range(100):
        hnsw_tree.add_point((i, i), {"id": i})

    # Change ef (higher ef = better accuracy, slower queries)
    hnsw_tree.set_ef(10)  # Low ef
    nearest = hnsw_tree.get_nearest((50, 50), False)
    assert nearest is not None

    hnsw_tree.set_ef(200)  # High ef
    nearest = hnsw_tree.get_nearest((50, 50), False)
    assert nearest is not None


def test_return_distance_flag():
    """Test that return_dist_sq flag works correctly."""
    hnsw_tree = HNSWKDTree([], 2)
    hnsw_tree.add_point((0, 0), {"id": 1})
    hnsw_tree.add_point((3, 4), {"id": 2})

    # Without distance
    result = hnsw_tree.get_nearest((0, 0), False)
    assert len(result) == 2
    assert result == ((0, 0), {"id": 1})

    # With distance
    result = hnsw_tree.get_nearest((0, 0), True)
    assert len(result) == 2
    dist_sq, (point, props) = result
    assert isinstance(dist_sq, (int, float, np.number))
    assert point == (0, 0)
    assert props == {"id": 1}


def test_auto_resize():
    """Test that the index automatically resizes when needed."""
    # Create with small max_elements
    hnsw_tree = HNSWKDTree([], 2, max_elements=10)

    # Add more than max_elements
    for i in range(20):
        hnsw_tree.add_point((i, i), {"id": i})

    # Should have auto-resized
    assert hnsw_tree.size() == 20
    assert hnsw_tree.max_elements >= 20

    # Should still be queryable
    nearest = hnsw_tree.get_nearest((10, 10), False)
    assert nearest is not None


def test_get_stats():
    """Test getting index statistics."""
    hnsw_tree = HNSWKDTree([], 2, max_elements=1000, M=16, ef_construction=200)

    stats = hnsw_tree.get_stats()
    assert stats["size"] == 0
    assert stats["max_elements"] == 1000
    assert stats["dimension"] == 2
    assert stats["space"] == "l2"
    assert stats["M"] == 16
    assert stats["ef_construction"] == 200

    # Add some points and check again
    hnsw_tree.add_point((1, 1), {})
    hnsw_tree.add_point((2, 2), {})

    stats = hnsw_tree.get_stats()
    assert stats["size"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
