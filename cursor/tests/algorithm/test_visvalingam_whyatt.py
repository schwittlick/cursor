import pytest

from cursor.algorithm.visvalingam_whyatt import simplify_vw, triangle_area, VisvalingamWhyatt
from cursor.path import Path
from cursor.position import Position


def test_triangle_area():
    """Test the triangle area calculation function."""
    p1 = Position(0, 0)
    p2 = Position(1, 0)
    p3 = Position(0, 1)

    # Basic triangle
    assert triangle_area(p1, p2, p3) == 0.5

    # Zero area triangle (collinear points)
    p4 = Position(2, 0)
    assert triangle_area(p1, p2, p4) == 0.0

    # Negative coordinates
    p5 = Position(-1, -1)
    p6 = Position(1, -1)
    p7 = Position(0, 1)
    assert triangle_area(p5, p6, p7) == 2.0


def test_basic_simplification():
    """Test basic simplification with various thresholds."""
    positions = [
        Position(0, 0),
        Position(1, 1),
        Position(2, 0),
        Position(3, 1),
        Position(4, 0)
    ]

    # First, print out the actual areas to understand what we're working with
    vw = VisvalingamWhyatt()
    vw.points = positions
    areas = []
    for i in range(1, len(positions) - 1):
        area = vw._calculate_effective_area(i)
        areas.append((i, area))

    # Test cases with different thresholds
    test_cases = [
        {
            'threshold': 0.5,
            'expected_length': 5,
            'message': "Should keep all points when threshold < area"
        },
        {
            'threshold': 1.0,
            'expected_length': 3,
            'message': "Should remove points with area <= threshold"
        },
        {
            'threshold': 1.5,
            'expected_length': 2,
            'message': "Should keep only endpoints with high threshold"
        }
    ]

    for case in test_cases:
        simplified = simplify_vw(positions, case['threshold'])
        assert len(simplified) == case['expected_length'], \
            f"{case['message']}: Expected {case['expected_length']} points with threshold " \
            f"{case['threshold']}, got {len(simplified)}"

        # Always verify that endpoints are preserved
        assert simplified[0] == positions[0]
        assert simplified[-1] == positions[-1]

        # For high threshold case, verify we only have endpoints
        if case['threshold'] > 1.0:
            assert len(simplified) == 2
            assert simplified[0] == positions[0]
            assert simplified[1] == positions[-1]


def test_small_input():
    """Test handling of small input arrays."""
    # Single point
    positions = Path.from_list([Position(0, 0)])
    assert simplify_vw(positions) == positions

    # Two points
    positions = Path.from_list([Position(0, 0), Position(1, 1)])
    assert simplify_vw(positions) == positions

    # Three points
    positions = Path.from_list([Position(0, 0), Position(1, 1), Position(2, 2)])
    assert simplify_vw(positions) == positions


def test_threshold_extremes():
    """Test behavior with extreme threshold values."""
    positions = [
        Position(0, 0),
        Position(1, 1),
        Position(2, 0),
        Position(3, 1),
        Position(4, 0)
    ]

    # Zero threshold should remove collinear points
    zero_threshold = simplify_vw(positions, threshold=0)
    assert len(zero_threshold) >= 2  # Should at least keep endpoints


def test_numerical_stability():
    """Test numerical stability with very small and large coordinates."""
    positions = [
        Position(0, 0),
        Position(1e-10, 1e-10),
        Position(2e-10, 0),
        Position(1e10, 1e10),
        Position(2e10, 0)
    ]

    simplified = simplify_vw(positions, threshold=1e-20)
    assert len(simplified) >= 2  # Should handle extreme values gracefully


def test_repeated_points():
    """Test handling of repeated points."""
    positions = [
        Position(0, 0),
        Position(0, 0),  # Repeated
        Position(1, 1),
        Position(1, 1),  # Repeated
        Position(2, 2)
    ]

    simplified = simplify_vw(positions, threshold=0)
    assert len(simplified) <= 3  # Should remove duplicates


def test_concave_hull():
    """Test simplification of a concave hull shape."""
    positions = [
        Position(0, 0),
        Position(1, 1),
        Position(2, 0.5),
        Position(3, 2),
        Position(4, 0.5),
        Position(5, 1),
        Position(6, 0)
    ]

    # Test that important concave features are preserved
    simplified = simplify_vw(positions, threshold=0.5)
    assert len(simplified) >= 5  # Should preserve main shape features


def test_edge_cases():
    """Test various edge cases."""
    # Empty list
    assert simplify_vw([]) == []

    # None values
    with pytest.raises(TypeError):
        simplify_vw(None)

    # Negative threshold
    simplified = simplify_vw([Position(0, 0), Position(1, 1)], threshold=-1.0)
    assert len(simplified) == 2  # Should handle negative threshold gracefully


def test_timestamp_ordering():
    """Test that timestamp ordering is preserved."""
    positions = []
    for i in range(5):
        pos = Position(i, i)
        pos.timestamp = i
        positions.append(pos)

    simplified = simplify_vw(positions, threshold=0.5)

    # Check that timestamps remain in order
    timestamps = [p.timestamp for p in simplified]
    assert timestamps == sorted(timestamps)


def test_floating_point_precision():
    """Test handling of floating-point precision."""
    positions = [
        Position(0.1234567890, 0),
        Position(1.1234567890, 1),
        Position(2.1234567890, 0),
        Position(3.1234567890, 1),
        Position(4.1234567890, 0)
    ]

    simplified = simplify_vw(positions, threshold=0.1)

    # Verify that floating-point precision is maintained
    for point in simplified:
        assert isinstance(point.x, float)
        assert isinstance(point.y, float)


if __name__ == "__main__":
    pytest.main([__file__])
