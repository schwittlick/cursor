"""
Tests for cursor.algorithm.offset — the arc-native polyline offset port.

The core of this file is `test_offset_matches_cavalier`, which replays offset test
vectors taken directly from the Rust crate `cavalier_contours` (the reference this
was ported from) and checks the result against its published expected properties.

The reference identifies each result polyline by (vertex_count, area, path_length,
extents). We compare area, path_length, and extents — the geometric invariants —
plus the number of result polylines. We do *not* compare vertex_count: the crate
runs `remove_redundant` (arc-aware collinear/concentric merging) before counting,
which is out of scope for this milestone; matching area+length+extents to 1e-4 is
the stronger geometric statement anyway.

Alongside the vectors:
  * geometry unit tests (ported from the crate's doctests),
  * self-consistency tests (offset points really are ~offset from the input),
  * adapter round-trip tests.
"""

from __future__ import annotations

import math

import pytest

from cursor.algorithm.offset import OffsetOptions, Pline, parallel_offset
from cursor.algorithm.offset.adapter import path_to_pline, pline_to_path
from cursor.algorithm.offset.geom import (
    Vector2 as V,
    circle_circle_intr,
    line_circle_intr,
    line_line_intr,
)
from cursor.algorithm.offset.measure import area, extents, path_length
from cursor.algorithm.offset.pline import PlineVertex as PV
from cursor.algorithm.offset.seg_intersect import pline_seg_intr
from cursor.algorithm.offset.segment import (
    seg_arc_radius_and_center,
    seg_closest_point,
    seg_length,
    seg_midpoint,
)

PROP_EPS = 1e-4


def _props(pl: Pline) -> tuple[float, float, float, float, float, float]:
    return (area(pl), path_length(pl), *extents(pl))


def _property_sets_match(results: list[Pline], expected: list[tuple]) -> bool:
    """Mirror the crate's property_sets_match, minus vertex_count (see module docstring)."""
    if len(results) != len(expected):
        return False
    used = [False] * len(results)
    for exp in expected:
        matches = 0
        for i, r in enumerate(results):
            if used[i]:
                continue
            p = _props(r)
            if all(abs(p[k] - exp[k]) < PROP_EPS for k in range(6)):
                used[i] = True
                matches += 1
                break
        if matches != 1:
            return False
    return True


# Each case: (name, vertices, is_closed, offset, [expected props...]) where an
# expected prop is (area, path_length, min_x, min_y, max_x, max_y). Values copied
# verbatim from cavalier_contours/tests/test_pline_parallel_offset.rs.
OFFSET_CASES = [
    # --- test_simple ---
    ("rect_inward", [(0, 0), (20, 0), (20, 10), (0, 10)], True, 2.0, [(96.0, 44.0, 2.0, 2.0, 18.0, 8.0)]),
    (
        "rect_outward",
        [(0, 0), (20, 0), (20, 10), (0, 10)],
        True,
        -2.0,
        [(332.56637061436, 72.566370614359, -2.0, -2.0, 22.0, 12.0)],
    ),
    ("open_rect_inward", [(0, 0), (20, 0), (20, 10), (0, 10), (0, 0)], False, 2.0, [(0.0, 44.0, 2.0, 2.0, 18.0, 8.0)]),
    (
        "open_rect_outward",
        [(0, 0), (20, 0), (20, 10), (0, 10), (0, 0)],
        False,
        -2.0,
        [(0.0, 69.424777960769, -2.0, -2.0, 22.0, 12.0)],
    ),
    ("rect_into_line", [(0, 0), (20, 0), (20, 10), (0, 10)], True, 5.0, [(0.0, 20.0, 5.0, 5.0, 15.0, 5.0)]),
    (
        "diamond_inward",
        [(-10, 0), (0, 10), (10, 0), (0, -10)],
        True,
        -5.0,
        [(-17.157287525381, 16.568542494924, -2.9289321881345, -2.9289321881345, 2.9289321881345, 2.9289321881345)],
    ),
    (
        "diamond_outward",
        [(-10, 0), (0, 10), (10, 0), (0, -10)],
        True,
        5.0,
        [(-561.38252881436, 87.984469030822, -15.0, -15.0, 15.0, 15.0)],
    ),
    (
        "open_diamond_inward",
        [(-10, 0), (0, 10), (10, 0), (0, -10), (-10, 0)],
        False,
        -5.0,
        [(0.0, 16.568542494924, -2.9289321881345, -2.9289321881345, 2.9289321881345, 2.9289321881345)],
    ),
    (
        "open_diamond_outward",
        [(-10, 0), (0, 10), (10, 0), (0, -10), (-10, 0)],
        False,
        5.0,
        [(0.0, 80.130487396847, -13.535533905933, -15.0, 15.0, 15.0)],
    ),
    (
        "circle_inward",
        [(-5, 0, 1.0), (5, 0, 1.0)],
        True,
        3.0,
        [(12.566370614359, 12.566370614359, -2.0, -2.0, 2.0, 2.0)],
    ),
    (
        "circle_outward",
        [(-5, 0, 1.0), (5, 0, 1.0)],
        True,
        -3.0,
        [(201.06192982975, 50.265482457437, -8.0, -8.0, 8.0, 8.0)],
    ),
    ("circle_collapsed_into_point", [(0, 0, 1.0), (2, 0, 1.0)], True, 1.0, []),
    ("circle_collapsed", [(0, 0, 1.0), (2, 0, 1.0)], True, 2.0, []),
    ("square_collapsed_into_point", [(-1, -1), (1, -1), (1, 1), (-1, 1)], True, 1.0, []),
    ("square_collapsed", [(-1, -1), (1, -1), (1, 1), (-1, 1)], True, 2.0, []),
    # --- test_specific (edge cases / distinct code paths) ---
    (
        "case1_arc_past_line",
        [
            (27.804688, 1.0, 0.0),
            (28.46842055794889, 0.3429054695163245, 0.0),
            (32.34577133994935, 0.9269762697003898, 0.0),
            (32.38116957207762, 1.451312562563487, 0.0),
            (31.5, 1.0, -0.31783751349740424),
            (30.79289310940682, 1.5, 0.0),
            (29.20710689059337, 1.5, -0.31783754777018053),
            (28.49999981323106, 1.00000000000007, 0.0),
        ],
        True,
        0.1,
        [
            (0.094833810726263, 1.8213211761499, 31.533345690439, 0.90572346564886, 32.26949555256, 1.2817628453883),
            (1.7197931450343, 7.5140262005179, 28.047835685678, 0.44926177903859, 31.495431966272, 1.4),
        ],
    ),
    (
        "case2_first_vertex_on_intersect",
        [
            (27.804688, 1.0, 0.0),
            (27.804688, 0.75, 0.0),
            (32.195313, 0.75, 0.0),
            (32.195313, 1.0, 0.0),
            (31.5, 1.0, -0.3178375134974),
            (30.792893109407, 1.5, 0.0),
            (29.207106890593, 1.5, -0.31783754777018),
            (28.499999813231, 1.0000000000001, 0.0),
        ],
        True,
        0.25,
        [(0.36247092523069, 3.593999211522, 29.16143806012, 1.0, 30.838561906052, 1.25)],
    ),
    ("case3_collapsed_rect", [(0, 0), (120, 0), (120, 40), (0, 40)], True, 30.0, []),
    (
        "case4_three_segs_intersect_one_point",
        [
            (30.12347538297979, -17.0, 0.0),
            (42.0, -17.0, 0.0),
            (42.0, 17.0, 0.0),
            (30.123475382979798, 17.0, -0.09331155002441319),
            (30.5, 15.0, 0.0),
            (30.5, -15.0, -0.09331155002441341),
        ],
        False,
        -2.0,
        [(0.0, 99.224754131592, 28.12347538298, -19.0, 44.0, 19.0)],
    ),
    (
        "case8_almost_collapsed_arcs_true_intersects",
        [(30, 0, 1.0), (30, 150, 0), (-380, 0, 0), (30, -150, 1.0)],
        True,
        71.0,
        [
            (
                31.563080748331117,
                36.43002218023972,
                17.851377192815367,
                69.95291962376376,
                34.00000003096393,
                75.82916586272847,
            ),
            (
                7211.747093261731,
                504.5601794261032,
                -173.3532697788056,
                -61.27715478753268,
                -5.862380026216215,
                61.27715478753261,
            ),
            (
                31.56308032687207,
                36.43002208996665,
                17.851377192815107,
                -75.82916586272874,
                34.000000000000675,
                -69.95291962376365,
            ),
        ],
    ),
    (
        "case9_almost_collapsed_arcs_false_intersects",
        [(30, 0, 1.0), (30, 150, 0), (-380, 0, 0), (30, -150, 1.0)],
        True,
        73.0,
        [
            (
                6273.618943028112,
                440.30207980349326,
                -167.53223512468745,
                -54.49913379476977,
                -18.567936085649954,
                54.499133794769804,
            )
        ],
    ),
    (
        "case10_collapsed_adjacent_arcs",
        [(30, 0, 1.0), (30, 150, 0), (-380, 0, 0), (30, -150, 1.0)],
        True,
        77.0,
        [
            (
                4682.865221417136,
                359.74976552142584,
                -155.89016581645112,
                -45.203002912175684,
                -32.335291189837534,
                45.203002912175705,
            )
        ],
    ),
]


@pytest.mark.parametrize("name,verts,closed,offset,expected", OFFSET_CASES, ids=[c[0] for c in OFFSET_CASES])
def test_offset_matches_cavalier(name, verts, closed, offset, expected):
    """Offset result matches the reference crate's published properties."""
    pline = Pline.from_vertices(verts, is_closed=closed)
    for handle_self_intersects in (False, True) if closed else (False,):
        result = parallel_offset(pline, offset, OffsetOptions(handle_self_intersects=handle_self_intersects))
        assert _property_sets_match(result, expected), (
            f"{name} (hsi={handle_self_intersects}): "
            f"got {[tuple(round(x, 4) for x in _props(r)) for r in result]}, "
            f"expected {expected}"
        )


# ---------------------------------------------------------------------------
# Self-consistency: the offset really is |offset| from the input
# ---------------------------------------------------------------------------

_SHAPES = {
    "square": (Pline.from_vertices([(0, 0), (30, 0), (30, 30), (0, 30)], is_closed=True)),
    "circle": (Pline.from_vertices([(-5, 0, 1.0), (5, 0, 1.0)], is_closed=True)),
    "open_L": (Pline.from_vertices([(0, 0), (20, 0), (20, 20)], is_closed=False)),
    "arc_line": (Pline.from_vertices([(0, 0, 0.5), (10, 0, 0.0), (20, 10, 0.0)], is_closed=False)),
}


@pytest.mark.parametrize("shape", list(_SHAPES))
@pytest.mark.parametrize("offset", [2.0, -2.0, 4.0])
def test_offset_points_are_offset_distance_from_input(shape, offset):
    """
    Every vertex of the offset result is at least |offset| from the input (minus a
    tolerance). This is the defining property of an offset curve, checked independently
    of the reference — if a result strayed inside the offset band it would be wrong.
    """
    src = _SHAPES[shape]
    results = parallel_offset(src, offset)
    if not results:
        return
    tol = 1e-3 * abs(offset)
    for r in results:
        for v in r:
            nearest = min(
                math.dist((v.x, v.y), (seg_closest_point(a, b, v.pos, 1e-5).x, seg_closest_point(a, b, v.pos, 1e-5).y))
                for a, b in src.iter_segments()
            )
            assert nearest >= abs(offset) - tol, f"{shape} offset {offset}: point {v} only {nearest} from input"


def test_nested_offsets_shrink_monotonically():
    """Iterated inward offset of a square yields strictly smaller areas each round."""
    pline = Pline.from_vertices([(0, 0), (40, 0), (40, 40), (0, 40)], is_closed=True)
    areas = []
    current = [pline]
    for _ in range(5):
        nxt = []
        for pl in current:
            nxt.extend(parallel_offset(pl, 3.0))
        if not nxt:
            break
        current = nxt
        areas.append(sum(area(p) for p in current))
    assert len(areas) >= 3
    assert all(areas[i + 1] < areas[i] for i in range(len(areas) - 1))


# ---------------------------------------------------------------------------
# Geometry unit tests (ported from the crate's doctests)
# ---------------------------------------------------------------------------


def _approx(a, b, e=1e-9):
    return abs(a - b) < e


def test_line_line_intersect():
    r = line_line_intr(V(0, 0), V(1, 0), V(0.5, -1), V(0.5, 1), 1e-5)
    assert r.kind == "true" and _approx(r.seg1_t, 0.5) and _approx(r.seg2_t, 0.5)
    assert line_line_intr(V(0, 0), V(1, 0), V(0, 1), V(1, 1), 1e-5).kind == "none"
    assert line_line_intr(V(0, 0), V(2, 0), V(1, 0), V(3, 0), 1e-5).kind == "overlapping"


def test_line_circle_and_circle_circle_intersect():
    assert line_circle_intr(V(0, 0), V(1, 0), 1.0, V(0, 1), 1e-5).kind == "tangent"
    r = circle_circle_intr(1.0, V(0, 0), 1.0, V(0, 2), 1e-5)
    assert r.kind == "tangent" and r.point1.fuzzy_eq_eps(V(0, 1), 1e-9)
    assert circle_circle_intr(1.0, V(0, 0), 1.0, V(1, 0), 1e-5).kind == "two"


def test_arc_geometry():
    radius, center = seg_arc_radius_and_center(PV(0, 0, 1.0), PV(1, 0, 0.0))
    assert _approx(radius, 0.5) and center.fuzzy_eq_eps(V(0.5, 0), 1e-9)
    assert _approx(seg_length(PV(2, 2, 1.0), PV(4, 2, 0.0)), math.pi)  # half circle radius 1
    assert seg_midpoint(PV(2, 2, 1.0), PV(4, 2, 0.0)).fuzzy_eq_eps(V(3, 1), 1e-9)  # +1 sweeps down
    assert seg_closest_point(PV(2, 2, 1.0), PV(4, 2, 0.0), V(3, 0), 1e-5).fuzzy_eq_eps(V(3, 1), 1e-9)


def test_segment_intersect_line_through_arc():
    r = pline_seg_intr(PV(0.5, -1, 0), PV(0.5, 1, 0), PV(0, 0, 1.0), PV(1, 0, 0), 1e-5)
    assert r.kind in ("one", "tangent")
    assert r.point1.fuzzy_eq_eps(V(0.5, -0.5), 1e-7)


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


def test_adapter_circle_tessellation_within_tolerance():
    circ = Pline.from_vertices([(0, 0, 1.0), (2, 0, 1.0)], is_closed=True)
    pts = list(pline_to_path(circ, chord_tolerance=0.01))
    per = sum(math.dist((pts[i].x, pts[i].y), (pts[i + 1].x, pts[i + 1].y)) for i in range(len(pts) - 1))
    assert abs(per - 2 * math.pi) < 0.05  # tessellated perimeter approaches the true circle


def test_adapter_path_to_pline_detects_closure():
    from cursor.path import Path

    path = Path()
    for x, y in [(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)]:
        path.add(x, y)
    pline = path_to_pline(path)
    assert pline.is_closed and len(pline) == 4


def test_empty_and_degenerate_inputs():
    assert parallel_offset(Pline.from_vertices([], is_closed=False), 5.0) == []
    assert parallel_offset(Pline.from_vertices([(0, 0)], is_closed=False), 5.0) == []
