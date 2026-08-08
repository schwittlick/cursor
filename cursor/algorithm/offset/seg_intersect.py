"""
Intersection of two polyline segments, ported from ``polyline::pline_seg_intersect``.

This is the bridge from the raw geometric primitives in :mod:`geom` (which work on
lines and circles) to the segments the offset engine actually deals in (lines and
*arcs*). It dispatches on the four combinations — line/line, line/arc, arc/line,
arc/arc — and, importantly, keeps intersects **sticky to segment endpoints**: when
a computed intersect lands within epsilon of a segment end, the exact endpoint is
substituted. That consistency is what lets the offset engine's slicing and
stitching line up cleanly instead of drifting by an epsilon at every junction.
"""

from __future__ import annotations

from dataclasses import dataclass

from .geom import (
    Vector2,
    angle_from_bulge,
    angle_is_within_sweep,
    angle_of,
    circle_circle_intr,
    delta_angle,
    dist_squared,
    line_circle_intr,
    line_line_intr,
    normalize_radians,
    point_from_parametric,
    point_within_arc_sweep,
)
from .pline import PlineVertex
from .segment import seg_arc_radius_and_center


@dataclass(frozen=True, slots=True)
class SegIntr:
    """
    Result of :func:`pline_seg_intr`.

    ``kind`` is one of:
      * ``"none"``            — no intersect
      * ``"tangent"``         — one tangent point (``point1``)
      * ``"one"``             — one non-tangent point (``point1``)
      * ``"two"``             — two points (``point1``, ``point2``)
      * ``"overlapping_lines"`` / ``"overlapping_arcs"`` — collinear/coincident
        overlap spanning ``point1`` to ``point2``

    For the two-point and overlap cases the points are ordered by the *second*
    segment's direction, matching the crate (the offset engine relies on this).
    """

    kind: str
    point1: Vector2 | None = None
    point2: Vector2 | None = None


def pline_seg_intr(v1: PlineVertex, v2: PlineVertex, u1: PlineVertex, u2: PlineVertex, pos_eps: float) -> SegIntr:
    """Intersect segments v1->v2 and u1->u2. ``pos_eps`` is the position tolerance."""
    v_is_line = v1.bulge_is_zero()
    u_is_line = u1.bulge_is_zero()

    if v_is_line and u_is_line:
        res = line_line_intr(v1.pos, v2.pos, u1.pos, u2.pos, pos_eps)
        if res.kind in ("none", "false"):
            return SegIntr("none")
        if res.kind == "true":
            return SegIntr("one", point1=point_from_parametric(v1.pos, v2.pos, res.seg1_t))
        # overlapping
        return SegIntr(
            "overlapping_lines",
            point1=point_from_parametric(u1.pos, u2.pos, res.seg2_t0),
            point2=point_from_parametric(u1.pos, u2.pos, res.seg2_t1),
        )

    if v_is_line:
        return _line_arc_intr(v1.pos, v2.pos, u1, u2, u_is_line, pos_eps)

    if u_is_line:
        return _line_arc_intr(u1.pos, u2.pos, v1, v2, u_is_line, pos_eps)

    return _arc_arc_intr(v1, v2, u1, u2, pos_eps)


def _line_arc_intr(
    p0: Vector2, p1: Vector2, a1: PlineVertex, a2: PlineVertex, u_is_line: bool, pos_eps: float
) -> SegIntr:
    """Intersect a line segment p0->p1 with an arc segment a1->a2."""
    arc_radius, arc_center = seg_arc_radius_and_center(a1, a2)

    def point_lies_on_arc(pt: Vector2) -> bool:
        return (
            point_within_arc_sweep(arc_center, a1.pos, a2.pos, a1.bulge_is_neg(), pt, pos_eps)
            and abs(dist_squared(pt, arc_center) ** 0.5 - arc_radius) < pos_eps
        )

    line_len = (p1 - p0).length()

    def point_in_sweep(t: float) -> Vector2 | None:
        if not ((0.0 - pos_eps) < t * line_len < (line_len + pos_eps)):
            return None
        p = point_from_parametric(p0, p1, t)
        if point_within_arc_sweep(arc_center, a1.pos, a2.pos, a1.bulge_is_neg(), p, pos_eps):
            return p
        return None

    res = line_circle_intr(p0, p1, arc_radius, arc_center, pos_eps)
    if res.kind == "none":
        return SegIntr("none")

    if res.kind == "tangent":
        # Endpoints are sticky — see module docstring.
        if point_lies_on_arc(p0):
            return SegIntr("tangent", point1=p0)
        if point_lies_on_arc(p1):
            return SegIntr("tangent", point1=p1)
        p = point_in_sweep(res.t0)
        return SegIntr("tangent", point1=p) if p is not None else SegIntr("none")

    # two circle intersects
    t0_pt = point_in_sweep(res.t0)
    t1_pt = point_in_sweep(res.t1)
    if t0_pt is None and t1_pt is None:
        return SegIntr("none")

    if t0_pt is None or t1_pt is None:
        point = t0_pt if t0_pt is not None else t1_pt
        if point_lies_on_arc(p0):
            return SegIntr("one", point1=p0)
        if point_lies_on_arc(p1):
            return SegIntr("one", point1=p1)
        return SegIntr("one", point1=point)

    # both in sweep: substitute endpoints where they lie on the arc
    point1, point2 = t0_pt, t1_pt
    on0, on1 = point_lies_on_arc(p0), point_lies_on_arc(p1)
    if on0 and on1:
        if dist_squared(p0, point1) < dist_squared(p0, point2):
            point1, point2 = p0, p1
        else:
            point1, point2 = p1, p0
    elif on0:
        if dist_squared(p0, point1) < dist_squared(p0, point2):
            point1, point2 = p0, point2
        else:
            point1, point2 = point1, p0
    elif on1:
        if dist_squared(p1, point1) < dist_squared(p1, point2):
            point1, point2 = p1, point2
        else:
            point1, point2 = point1, p1

    # order by second segment's direction
    if u_is_line or dist_squared(point1, a1.pos) < dist_squared(point2, a1.pos):
        return SegIntr("two", point1=point1, point2=point2)
    return SegIntr("two", point1=point2, point2=point1)


def _arc_arc_intr(v1: PlineVertex, v2: PlineVertex, u1: PlineVertex, u2: PlineVertex, pos_eps: float) -> SegIntr:
    """Intersect two arc segments."""
    r1, c1 = seg_arc_radius_and_center(v1, v2)
    r2, c2 = seg_arc_radius_and_center(u1, u2)

    def start_and_sweep(sp: Vector2, center: Vector2, bulge: float) -> tuple[float, float]:
        return normalize_radians(angle_of(center, sp)), angle_from_bulge(bulge)

    def both_sweep(pt: Vector2) -> bool:
        return point_within_arc_sweep(c1, v1.pos, v2.pos, v1.bulge_is_neg(), pt, pos_eps) and point_within_arc_sweep(
            c2, u1.pos, u2.pos, u1.bulge_is_neg(), pt, pos_eps
        )

    def on_arc1(pt: Vector2) -> bool:
        return (
            point_within_arc_sweep(c1, v1.pos, v2.pos, v1.bulge_is_neg(), pt, pos_eps)
            and abs(dist_squared(pt, c1) ** 0.5 - r1) < pos_eps
        )

    def on_arc2(pt: Vector2) -> bool:
        return (
            point_within_arc_sweep(c2, u1.pos, u2.pos, u1.bulge_is_neg(), pt, pos_eps)
            and abs(dist_squared(pt, c2) ** 0.5 - r2) < pos_eps
        )

    res = circle_circle_intr(r1, c1, r2, c2, pos_eps)

    if res.kind == "none":
        return SegIntr("none")

    if res.kind == "tangent":
        point = res.point1
        if on_arc1(u1.pos):
            return SegIntr("tangent", point1=u1.pos)
        if on_arc1(u2.pos):
            return SegIntr("tangent", point1=u2.pos)
        if on_arc2(v1.pos):
            return SegIntr("tangent", point1=v1.pos)
        if on_arc2(v2.pos):
            return SegIntr("tangent", point1=v2.pos)
        if both_sweep(point):
            return SegIntr("tangent", point1=point)
        return SegIntr("none")

    if res.kind == "two":
        point1, point2 = res.point1, res.point2
        # collect up to two endpoint-substituted intersects
        end_pts: list[Vector2] = []

        def try_add(pt: Vector2) -> None:
            if len(end_pts) >= 2:
                return
            for existing in end_pts:
                if existing.fuzzy_eq_eps(pt, pos_eps):
                    return
            end_pts.append(pt)

        if on_arc1(u1.pos):
            try_add(u1.pos)
        if on_arc1(u2.pos):
            try_add(u2.pos)
        if on_arc2(v1.pos):
            try_add(v1.pos)
        if on_arc2(v2.pos):
            try_add(v2.pos)

        e0 = end_pts[0] if len(end_pts) >= 1 else None
        e1 = end_pts[1] if len(end_pts) >= 2 else None

        p1_in = both_sweep(point1)
        p2_in = both_sweep(point2)

        if p1_in and p2_in:
            if e0 is None and e1 is None:
                return SegIntr("two", point1=point1, point2=point2)
            if e0 is not None and e1 is None:
                if dist_squared(e0, point1) < dist_squared(e0, point2):
                    return SegIntr("two", point1=e0, point2=point2)
                return SegIntr("two", point1=point1, point2=e0)
            # both endpoints
            if dist_squared(e0, point1) < dist_squared(e1, point1):
                return SegIntr("two", point1=e0, point2=e1)
            return SegIntr("two", point1=e1, point2=e0)

        target_in = point1 if p1_in else (point2 if p2_in else None)
        if target_in is not None:
            if e0 is None and e1 is None:
                return SegIntr("one", point1=target_in)
            if e1 is None:
                return SegIntr("one", point1=e0)
            return SegIntr("two", point1=e0, point2=e1)

        # neither circle point in sweep, only endpoints could count
        if e0 is None and e1 is None:
            return SegIntr("none")
        if e1 is None:
            return SegIntr("one", point1=e0)
        return SegIntr("two", point1=e0, point2=e1)

    # overlapping circles: figure out how the two arc sweeps overlap
    same_dir = v1.bulge_is_neg() == u1.bulge_is_neg()
    a1_start, a1_sweep = start_and_sweep(v1.pos, c1, v1.bulge)
    if same_dir:
        a2_start, a2_sweep = start_and_sweep(u1.pos, c2, u1.bulge)
    else:
        a2_start, a2_sweep = start_and_sweep(u2.pos, c2, -u1.bulge)

    a1_end = a1_start + a1_sweep
    a2_end = a2_start + a2_sweep
    avg_radius = (r1 + r2) / 2.0

    touch_1 = abs(avg_radius * delta_angle(a1_start, a2_end)) < pos_eps
    touch_2 = abs(avg_radius * delta_angle(a2_start, a1_end)) < pos_eps

    if touch_1 and touch_2:
        return SegIntr("two", point1=u1.pos, point2=u2.pos)
    if touch_1:
        return SegIntr("one", point1=v1.pos)
    if touch_2:
        point = u1.pos if same_dir else u2.pos
        return SegIntr("one", point1=point)

    arc2_starts_in_arc1 = angle_is_within_sweep(a2_start, a1_start, a1_sweep)
    arc2_ends_in_arc1 = angle_is_within_sweep(a2_end, a1_start, a1_sweep)
    if arc2_starts_in_arc1 and arc2_ends_in_arc1:
        return SegIntr("overlapping_arcs", point1=u1.pos, point2=u2.pos)
    if arc2_starts_in_arc1:
        if same_dir:
            return SegIntr("overlapping_arcs", point1=u1.pos, point2=v2.pos)
        return SegIntr("overlapping_arcs", point1=v2.pos, point2=u2.pos)
    if arc2_ends_in_arc1:
        if same_dir:
            return SegIntr("overlapping_arcs", point1=v1.pos, point2=u2.pos)
        return SegIntr("overlapping_arcs", point1=u1.pos, point2=v1.pos)

    arc1_starts_in_arc2 = angle_is_within_sweep(a1_start, a2_start, a2_sweep)
    if arc1_starts_in_arc2:
        if same_dir:
            return SegIntr("overlapping_arcs", point1=v1.pos, point2=v2.pos)
        return SegIntr("overlapping_arcs", point1=v2.pos, point2=v1.pos)

    return SegIntr("none")
