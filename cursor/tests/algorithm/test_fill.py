import math

import pytest
from shapely.geometry import Polygon

from cursor.algorithm.fill import detect_regions, hatch
from cursor.collection import Collection
from cursor.path import Path


def line(*points) -> Path:
    p = Path()
    for x, y in points:
        p.add(x, y)
    return p


def square(size: float = 10.0, gap: float = 0.0) -> Collection:
    """Four sides of a square, each side short of the corner by `gap`."""
    c = Collection()
    h = gap / 2.0
    c.add(line((h, 0), (size - h, 0)))
    c.add(line((size, h), (size, size - h)))
    c.add(line((size - h, size), (h, size)))
    c.add(line((0, size - h), (0, h)))
    return c


def test_detects_a_closed_square():
    regions = detect_regions(square())
    assert len(regions) == 1
    assert regions[0].area == pytest.approx(100.0)


def test_open_square_is_not_a_region_without_a_gap_allowance():
    assert detect_regions(square(gap=1.0)) == []


def test_gap_bridges_an_open_square():
    regions = detect_regions(square(gap=1.0), gap=1.0)
    assert len(regions) == 1
    assert regions[0].area == pytest.approx(100.0, rel=0.1)


def test_min_area_drops_the_spurious_faces_that_gap_creates():
    # a stub stopping short of two sides. Extended far enough it pokes through
    # both and cuts a corner off the square - a face that is not really there.
    c = square()
    c.add(line((1, 3), (3, 1)))

    assert len(detect_regions(c)) == 1  # the stub just dangles
    assert len(detect_regions(c, gap=2.0)) == 2  # now it severs the corner
    assert len(detect_regions(c, gap=2.0, min_area=10.0)) == 1  # 8 mm^2 corner dropped


def test_regions_come_back_smallest_first():
    c = square(10.0)
    for path in square(4.0):
        path.translate(20, 0)
        c.add(path)
    areas = [r.area for r in detect_regions(c)]
    assert areas == sorted(areas)


def test_empty_collection_has_no_regions():
    assert detect_regions(Collection()) == []


@pytest.mark.parametrize("angle", [0.0, 45.0, 90.0, 137.0])
def test_hatch_stays_inside_the_region(angle):
    region = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    for path in hatch(region, spacing=1.0, angle_deg=angle):
        for v in path:
            assert -1e-6 <= v.x <= 10 + 1e-6
            assert -1e-6 <= v.y <= 10 + 1e-6


def test_hatch_line_count_follows_spacing():
    region = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    assert len(hatch(region, spacing=1.0, angle_deg=0.0)) == 10
    assert len(hatch(region, spacing=2.0, angle_deg=0.0)) == 5


def test_hatch_covers_roughly_the_area():
    region = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    drawn = sum(
        math.dist(path[i].as_tuple(), path[i + 1].as_tuple())
        for path in hatch(region, spacing=0.5, angle_deg=0.0)
        for i in range(len(path) - 1)
    )
    assert drawn == pytest.approx(region.area / 0.5, rel=0.05)


def test_hatch_alternates_direction_to_save_pen_up_travel():
    region = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    rows = list(hatch(region, spacing=1.0, angle_deg=0.0))
    # consecutive rows end and start near each other, one spacing apart
    for a, b in zip(rows, rows[1:]):
        assert math.dist(a[-1].as_tuple(), b[0].as_tuple()) < 2.0


def test_hatch_skips_the_holes_in_a_ring():
    ring = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)], [[(4, 4), (6, 4), (6, 6), (4, 6)]])
    for path in hatch(ring, spacing=0.5, angle_deg=0.0):
        for v in path:
            assert not (4 < v.x < 6 and 4 < v.y < 6)


def test_hatch_of_an_empty_region_is_empty():
    assert len(hatch(Polygon(), spacing=1.0)) == 0


def test_hatch_rejects_a_non_positive_spacing():
    with pytest.raises(ValueError):
        hatch(Polygon([(0, 0), (1, 0), (1, 1)]), spacing=0)
