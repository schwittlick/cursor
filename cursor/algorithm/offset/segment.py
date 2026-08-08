"""
Per-segment arc geometry, ported from ``polyline::pline_seg``.

Given two consecutive vertices ``v1`` and ``v2`` (where ``v1.bulge`` describes the
segment), these answer the questions the offset engine keeps asking: where is the
arc's centre and radius, how long is it, where is its midpoint, what is the
closest point on it to some probe, and how do you split it at a point. A zero
bulge means the segment is a straight line and every function degrades to the
line case.

The functions here are scalar — one segment at a time — which is the right grain
for arc math. The one genuinely data-parallel operation, "bounding box of every
segment at once", is provided separately as :func:`segment_bboxes` operating on a
whole vertex array with numpy.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .geom import (
    FUZZY_EPS,
    Vector2,
    angle_is_within_sweep,
    angle_of,
    bulge_from_angle,
    delta_angle,
    delta_angle_signed,
    dist_squared,
    line_seg_closest_point,
    midpoint,
    point_on_circle,
    point_within_arc_sweep,
)
from .pline import Pline, PlineVertex


def seg_arc_radius_and_center(v1: PlineVertex, v2: PlineVertex) -> tuple[float, Vector2]:
    """Radius and centre of the arc segment v1->v2. Undefined if ``v1.bulge`` is zero."""
    abs_bulge = abs(v1.bulge)
    chord = v2.pos - v1.pos
    chord_len = chord.length()
    radius = chord_len * (abs_bulge * abs_bulge + 1.0) / (4.0 * abs_bulge)

    # Offset from chord midpoint to the arc centre, perpendicular to the chord.
    s = abs_bulge * chord_len / 2.0
    m = radius - s
    offs_x = -m * chord.y / chord_len
    offs_y = m * chord.x / chord_len
    if v1.bulge_is_neg():
        offs_x, offs_y = -offs_x, -offs_y

    center = Vector2(v1.x + chord.x / 2.0 + offs_x, v1.y + chord.y / 2.0 + offs_y)
    return radius, center


@dataclass(frozen=True, slots=True)
class SplitResult:
    """From :func:`seg_split_at_point`: the segment cut in two at a point on it."""

    updated_start: PlineVertex
    """Same position as the original start, with bulge rewritten to reach the split point."""
    split_vertex: PlineVertex
    """At the split point, with bulge set to reach the original end."""


def seg_split_at_point(v1: PlineVertex, v2: PlineVertex, point: Vector2, pos_eps: float) -> SplitResult:
    """Split the segment v1->v2 at ``point`` (assumed to lie on it), preserving curvature."""
    if v1.bulge_is_zero():
        return SplitResult(v1, PlineVertex(point.x, point.y, 0.0))

    if v1.pos.fuzzy_eq_eps(v2.pos, pos_eps) or v1.pos.fuzzy_eq_eps(point, pos_eps):
        return SplitResult(PlineVertex(point.x, point.y, 0.0), PlineVertex(point.x, point.y, v1.bulge))

    if v2.pos.fuzzy_eq_eps(point, pos_eps):
        return SplitResult(v1, PlineVertex(v2.x, v2.y, 0.0))

    _, center = seg_arc_radius_and_center(v1, v2)
    point_angle = angle_of(center, point)

    start_angle = angle_of(center, v1.pos)
    theta1 = delta_angle_signed(start_angle, point_angle, v1.bulge_is_neg())
    bulge1 = bulge_from_angle(theta1)

    end_angle = angle_of(center, v2.pos)
    theta2 = delta_angle_signed(point_angle, end_angle, v1.bulge_is_neg())
    bulge2 = bulge_from_angle(theta2)

    return SplitResult(PlineVertex(v1.x, v1.y, bulge1), PlineVertex(point.x, point.y, bulge2))


def seg_tangent_vector(v1: PlineVertex, v2: PlineVertex, point: Vector2) -> Vector2:
    """Tangent direction (not normalized) at ``point`` on the segment v1->v2."""
    if v1.bulge_is_zero():
        return v2.pos - v1.pos
    _, center = seg_arc_radius_and_center(v1, v2)
    if v1.bulge_is_pos():
        # CCW: rotate the radius vector +90 degrees.
        return Vector2(-(point.y - center.y), point.x - center.x)
    # CW: rotate the radius vector -90 degrees.
    return Vector2(point.y - center.y, -(point.x - center.x))


def seg_closest_point(v1: PlineVertex, v2: PlineVertex, point: Vector2, eps: float) -> Vector2:
    """Closest point on the segment v1->v2 to ``point``."""
    if v1.bulge_is_zero():
        return line_seg_closest_point(v1.pos, v2.pos, point)

    radius, center = seg_arc_radius_and_center(v1, v2)
    if point.fuzzy_eq_eps(center, eps):
        # At the arc centre; every arc point is equidistant, just pick the start.
        return v1.pos

    if point_within_arc_sweep(center, v1.pos, v2.pos, v1.bulge_is_neg(), point, eps):
        return (point - center).normalize().scale(radius) + center

    # Off the sweep: the nearer endpoint wins.
    if dist_squared(v1.pos, point) < dist_squared(v2.pos, point):
        return v1.pos
    return v2.pos


def seg_length(v1: PlineVertex, v2: PlineVertex) -> float:
    if v1.fuzzy_eq_eps(v2, FUZZY_EPS):
        return 0.0
    if v1.bulge_is_zero():
        return (v2.pos - v1.pos).length()
    radius, center = seg_arc_radius_and_center(v1, v2)
    start_angle = angle_of(center, v1.pos)
    end_angle = angle_of(center, v2.pos)
    return radius * abs(delta_angle(start_angle, end_angle))


def seg_midpoint(v1: PlineVertex, v2: PlineVertex) -> Vector2:
    if v1.bulge_is_zero():
        return midpoint(v1.pos, v2.pos)
    radius, center = seg_arc_radius_and_center(v1, v2)
    a1 = angle_of(center, v1.pos)
    a2 = angle_of(center, v2.pos)
    mid_angle = a1 + delta_angle_signed(a1, a2, v1.bulge_is_neg()) / 2.0
    return point_on_circle(radius, center, mid_angle)


def seg_bounding_box(v1: PlineVertex, v2: PlineVertex) -> tuple[float, float, float, float]:
    """
    True axis-aligned bbox of the segment as ``(min_x, min_y, max_x, max_y)``.

    For an arc, an extreme in x or y appears only if the sweep actually crosses the
    corresponding cardinal direction (0, pi/2, pi, 3pi/2); otherwise the endpoints
    bound it.
    """
    if v1.bulge_is_zero():
        return (min(v1.x, v2.x), min(v1.y, v2.y), max(v1.x, v2.x), max(v1.y, v2.y))

    if v1.pos.fuzzy_eq(v2.pos):
        return (v1.x, v1.y, v1.x, v1.y)

    radius, center = seg_arc_radius_and_center(v1, v2)
    start_angle = angle_of(center, v1.pos)
    end_angle = angle_of(center, v2.pos)
    sweep = delta_angle_signed(start_angle, end_angle, v1.bulge_is_neg())

    def crosses(a: float) -> bool:
        return angle_is_within_sweep(a, start_angle, sweep)

    min_x = center.x - radius if crosses(np.pi) else min(v1.x, v2.x)
    min_y = center.y - radius if crosses(1.5 * np.pi) else min(v1.y, v2.y)
    max_x = center.x + radius if crosses(0.0) else max(v1.x, v2.x)
    max_y = center.y + radius if crosses(0.5 * np.pi) else max(v1.y, v2.y)
    return (min_x, min_y, max_x, max_y)


def seg_fast_approx_bounding_box(v1: PlineVertex, v2: PlineVertex) -> tuple[float, float, float, float]:
    """
    A quick bbox that is never smaller than the true one — chord extended by the
    sagitta. Cheaper than :func:`seg_bounding_box` for arcs; used where an
    over-estimate is fine (spatial pre-filtering).
    """
    if v1.bulge_is_zero():
        return (min(v1.x, v2.x), min(v1.y, v2.y), max(v1.x, v2.x), max(v1.y, v2.y))
    b = v1.bulge
    offs_x = b * (v2.y - v1.y) / 2.0
    offs_y = -b * (v2.x - v1.x) / 2.0
    px_min, px_max = min(v1.x + offs_x, v2.x + offs_x), max(v1.x + offs_x, v2.x + offs_x)
    py_min, py_max = min(v1.y + offs_y, v2.y + offs_y), max(v1.y + offs_y, v2.y + offs_y)
    return (
        min(min(v1.x, v2.x), px_min),
        min(min(v1.y, v2.y), py_min),
        max(max(v1.x, v2.x), px_max),
        max(max(v1.y, v2.y), py_max),
    )


def segment_bboxes(pline: Pline) -> np.ndarray:
    """
    Fast approximate bounding boxes for **every** segment at once, as an
    ``(M, 4)`` array of ``(min_x, min_y, max_x, max_y)``.

    This is the vectorized twin of :func:`seg_fast_approx_bounding_box` — the same
    chord-plus-sagitta box, computed for all segments in numpy in one shot. It is
    what the O(n^2) intersection pre-filter and the distance passes build on.
    """
    data = pline.vertex_data()
    n = len(data)
    if n < 2:
        return np.empty((0, 4), dtype=np.float64)

    if pline.is_closed:
        starts = data
        ends = np.roll(data, -1, axis=0)
    else:
        starts = data[:-1]
        ends = data[1:]

    x1, y1, b = starts[:, 0], starts[:, 1], starts[:, 2]
    x2, y2 = ends[:, 0], ends[:, 1]

    # Chord-plus-sagitta corner (only meaningful for arcs; harmless for lines,
    # where the endpoint min/max already dominates).
    offs_x = b * (y2 - y1) / 2.0
    offs_y = -b * (x2 - x1) / 2.0
    px1, px2 = x1 + offs_x, x2 + offs_x
    py1, py2 = y1 + offs_y, y2 + offs_y

    is_line = np.abs(b) < 1e-8
    # For lines, collapse the sagitta corners onto the endpoints.
    px1 = np.where(is_line, x1, px1)
    px2 = np.where(is_line, x2, px2)
    py1 = np.where(is_line, y1, py1)
    py2 = np.where(is_line, y2, py2)

    min_x = np.minimum(np.minimum(x1, x2), np.minimum(px1, px2))
    min_y = np.minimum(np.minimum(y1, y2), np.minimum(py1, py2))
    max_x = np.maximum(np.maximum(x1, x2), np.maximum(px1, px2))
    max_y = np.maximum(np.maximum(y1, y2), np.maximum(py1, py2))
    return np.stack([min_x, min_y, max_x, max_y], axis=1)
