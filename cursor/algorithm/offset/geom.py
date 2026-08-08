"""
Foundational 2D geometry for the polyline offset engine.

This is a faithful Python port of the ``core::math`` layer of the Rust crate
`cavalier_contours <https://github.com/jbuckmccready/cavalier_contours>`_ (dual
Apache-2.0 / MIT): the ``Vector2`` type, the scalar angle/quadratic helpers, and
the three intersection primitives (line-line, line-circle, circle-circle) that
everything above is built from.

Everything here is *scalar* — one point, one segment at a time — and deliberately
so. The arc geometry that offsetting needs is intrinsically per-segment, and
keeping it as plain float math keeps it readable and close to the source it was
translated from. numpy earns its place one layer up, in the bulk passes
(bounding boxes, candidate-pair pruning, distance filtering) where there is real
data parallelism to exploit; see :mod:`cursor.algorithm.offset.pline`.

Fuzzy comparisons carry an explicit epsilon throughout, matching the Rust crate's
convention. The default, :data:`FUZZY_EPS` (1e-8), is for bare float equality;
position and distance comparisons in the higher layers use their own, coarser
epsilons (``pos_equal_eps`` = 1e-5, etc.) passed down explicitly.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# The crate's `f64::fuzzy_epsilon()`: the tolerance for bare floating-point
# equality, distinct from the coarser position/distance epsilons the offset
# engine threads through explicitly.
FUZZY_EPS = 1e-8

TAU = 2.0 * math.pi


# ---------------------------------------------------------------------------
# Vector2
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Vector2:
    """A 2D point/direction. Immutable, so it is safe to share and hash."""

    x: float
    y: float

    def __add__(self, o: Vector2) -> Vector2:
        return Vector2(self.x + o.x, self.y + o.y)

    def __sub__(self, o: Vector2) -> Vector2:
        return Vector2(self.x - o.x, self.y - o.y)

    def __neg__(self) -> Vector2:
        return Vector2(-self.x, -self.y)

    def scale(self, s: float) -> Vector2:
        return Vector2(self.x * s, self.y * s)

    def dot(self, o: Vector2) -> float:
        return self.x * o.x + self.y * o.y

    def perp_dot(self, o: Vector2) -> float:
        """``self.x*o.y - self.y*o.x`` — signed area, and the sign of the turn self->o."""
        return self.x * o.y - self.y * o.x

    def length_squared(self) -> float:
        return self.x * self.x + self.y * self.y

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def normalize(self) -> Vector2:
        return self.scale(1.0 / self.length())

    def safe_normalize(self) -> Vector2:
        """Normalize, or return zero if too short to do so robustly (degenerate segment)."""
        if self.length_squared() <= FUZZY_EPS * FUZZY_EPS:
            return Vector2(0.0, 0.0)
        return self.normalize()

    def perp(self) -> Vector2:
        """90° counter-clockwise rotation."""
        return Vector2(-self.y, self.x)

    def unit_perp(self) -> Vector2:
        return self.perp().normalize()

    def safe_unit_perp(self) -> Vector2:
        return self.perp().safe_normalize()

    def rotate_about(self, origin: Vector2, angle: float) -> Vector2:
        t = self - origin
        s, c = math.sin(angle), math.cos(angle)
        return Vector2(t.x * c - t.y * s, t.x * s + t.y * c) + origin

    def fuzzy_eq_eps(self, o: Vector2, eps: float) -> bool:
        return abs(self.x - o.x) < eps and abs(self.y - o.y) < eps

    def fuzzy_eq(self, o: Vector2) -> bool:
        return self.fuzzy_eq_eps(o, FUZZY_EPS)


def v2(x: float, y: float) -> Vector2:
    return Vector2(x, y)


# ---------------------------------------------------------------------------
# Scalar fuzzy helpers (the crate's FuzzyEq / FuzzyOrd, for floats)
# ---------------------------------------------------------------------------


def fuzzy_eq_zero(value: float, eps: float = FUZZY_EPS) -> bool:
    return abs(value) < eps


def fuzzy_eq(a: float, b: float, eps: float = FUZZY_EPS) -> bool:
    return abs(a - b) < eps


def fuzzy_in_range(value: float, lo: float, hi: float, eps: float) -> bool:
    return (lo - eps) < value < (hi + eps)


# ---------------------------------------------------------------------------
# Angle / arc helpers  (core::math::base_math)
# ---------------------------------------------------------------------------


def normalize_radians(angle: float) -> float:
    """Fold an angle into [0, 2*pi]."""
    if 0.0 <= angle <= TAU:
        return angle
    return angle - math.floor(angle / TAU) * TAU


def delta_angle(a1: float, a2: float) -> float:
    """Smallest signed rotation taking a1 to a2, in (-pi, pi]."""
    diff = normalize_radians(a2 - a1)
    if diff > math.pi:
        diff -= TAU
    return diff


def delta_angle_signed(a1: float, a2: float, negative: bool) -> float:
    """:func:`delta_angle` forced to the requested sign — for arc-direction edge cases."""
    diff = delta_angle(a1, a2)
    return -abs(diff) if negative else abs(diff)


def angle_is_between_eps(test: float, start: float, end: float, eps: float) -> bool:
    """Is ``test`` in the CCW sweep from ``start`` to ``end`` (fuzzy-inclusive)?"""
    end_sweep = normalize_radians(end - start)
    mid_sweep = normalize_radians(test - start)
    return mid_sweep < end_sweep + eps


def angle_is_within_sweep(test: float, start: float, sweep: float, eps: float = FUZZY_EPS) -> bool:
    """Is ``test`` inside the sweep of ``sweep`` radians from ``start`` (CCW if positive)?"""
    end = start + sweep
    if sweep < 0.0:
        return angle_is_between_eps(test, end, start, eps)
    return angle_is_between_eps(test, start, end, eps)


def bulge_from_angle(angle: float) -> float:
    """Bulge for an arc sweep angle: ``tan(angle / 4)``. Sign follows the angle."""
    return math.tan(angle / 4.0)


def angle_from_bulge(bulge: float) -> float:
    """Arc sweep angle for a bulge: ``4 * atan(bulge)``. Sign follows the bulge."""
    return 4.0 * math.atan(bulge)


def angle_of(p0: Vector2, p1: Vector2) -> float:
    """Polar angle of the direction p0 -> p1."""
    return math.atan2(p1.y - p0.y, p1.x - p0.x)


def dist_squared(p0: Vector2, p1: Vector2) -> float:
    d = p0 - p1
    return d.dot(d)


def midpoint(p0: Vector2, p1: Vector2) -> Vector2:
    return Vector2((p0.x + p1.x) / 2.0, (p0.y + p1.y) / 2.0)


def point_on_circle(radius: float, center: Vector2, angle: float) -> Vector2:
    return Vector2(center.x + radius * math.cos(angle), center.y + radius * math.sin(angle))


def point_from_parametric(p0: Vector2, p1: Vector2, t: float) -> Vector2:
    return p0 + (p1 - p0).scale(t)


def parametric_from_point(p0: Vector2, p1: Vector2, point: Vector2) -> float:
    """
    Parametric t of ``point`` along the line p0 -> p1, assuming it lies on the line.

    Uses whichever axis has the larger span, so vertical/horizontal lines and
    small denominators don't blow up.
    """
    x_diff = p1.x - p0.x
    y_diff = p1.y - p0.y
    if abs(x_diff) < abs(y_diff):
        return (point.y - p0.y) / y_diff
    return (point.x - p0.x) / x_diff


def line_seg_closest_point(p0: Vector2, p1: Vector2, point: Vector2) -> Vector2:
    """Closest point on the *segment* p0->p1 to ``point``."""
    v = p1 - p0
    w = point - p0
    c1 = w.dot(v)
    if c1 < FUZZY_EPS:
        return p0
    c2 = v.length_squared()
    if c2 < c1 + FUZZY_EPS:
        return p1
    return p0 + v.scale(c1 / c2)


def _perp_dot_test(p0: Vector2, p1: Vector2, point: Vector2) -> float:
    return (p1.x - p0.x) * (point.y - p0.y) - (p1.y - p0.y) * (point.x - p0.x)


def is_left(p0: Vector2, p1: Vector2, point: Vector2) -> bool:
    return _perp_dot_test(p0, p1, point) > 0.0


def is_left_or_coincident_eps(p0: Vector2, p1: Vector2, point: Vector2, eps: float) -> bool:
    return _perp_dot_test(p0, p1, point) > -eps


def is_right_or_coincident_eps(p0: Vector2, p1: Vector2, point: Vector2, eps: float) -> bool:
    return _perp_dot_test(p0, p1, point) < eps


def point_within_arc_sweep(
    center: Vector2,
    arc_start: Vector2,
    arc_end: Vector2,
    is_clockwise: bool,
    point: Vector2,
    eps: float,
) -> bool:
    """
    Is ``point`` inside the infinite cone swept from ``arc_start`` to ``arc_end``
    about ``center``? (The angular test for "on this arc", radius checked separately.)
    """
    if is_clockwise:
        return is_right_or_coincident_eps(center, arc_start, point, eps) and is_left_or_coincident_eps(
            center, arc_end, point, eps
        )
    return is_left_or_coincident_eps(center, arc_start, point, eps) and is_right_or_coincident_eps(
        center, arc_end, point, eps
    )


# ---------------------------------------------------------------------------
# Intersection primitives
#
# Each returns a small tagged result. The `kind` string is what the callers
# switch on, mirroring the Rust enums (NoIntersect / TangentIntersect / ...).
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class LineLineIntr:
    """Result of :func:`line_line_intr`. `kind` in {none, true, false, overlapping}."""

    kind: str
    seg1_t: float = 0.0
    seg2_t: float = 0.0
    seg2_t0: float = 0.0
    seg2_t1: float = 0.0


def line_line_intr(v1: Vector2, v2: Vector2, u1: Vector2, u2: Vector2, eps: float) -> LineLineIntr:
    """
    Intersect line segments v1->v2 and u1->u2, returning parametric values.

    Parametric so the caller can decide inclusivity; the segment-level wrapper in
    :mod:`cursor.algorithm.offset.seg_intersect` turns these into points.
    """
    v = v2 - v1
    u = u2 - u1
    v_pdot_u = v.perp_dot(u)
    w = v1 - u1

    seg1_len = v.length()
    seg2_len = u.length()

    if not fuzzy_eq_zero(v_pdot_u, eps):
        # Not parallel.
        seg1_t = u.perp_dot(w) / v_pdot_u
        seg2_t = v.perp_dot(w) / v_pdot_u
        if not fuzzy_in_range(seg1_t * seg1_len, 0.0, seg1_len, eps) or not fuzzy_in_range(
            seg2_t * seg2_len, 0.0, seg2_len, eps
        ):
            return LineLineIntr("false", seg1_t=seg1_t, seg2_t=seg2_t)
        return LineLineIntr("true", seg1_t=seg1_t, seg2_t=seg2_t)

    # Parallel, maybe collinear.
    v_pdot_w = v.perp_dot(w)
    u_pdot_w = u.perp_dot(w)
    if not fuzzy_eq_zero(v_pdot_w, eps) or not fuzzy_eq_zero(u_pdot_w, eps):
        return LineLineIntr("none")

    v_is_point = v1.fuzzy_eq_eps(v2, eps)
    u_is_point = u1.fuzzy_eq_eps(u2, eps)

    if v_is_point and u_is_point:
        if v1.fuzzy_eq_eps(u1, eps):
            return LineLineIntr("true", seg1_t=0.0, seg2_t=0.0)
        return LineLineIntr("none")

    if v_is_point:
        seg2_t = parametric_from_point(u1, u2, v1)
        if fuzzy_in_range(seg2_t * seg2_len, 0.0, seg2_len, eps):
            return LineLineIntr("true", seg1_t=0.0, seg2_t=seg2_t)
        return LineLineIntr("none")

    if u_is_point:
        seg1_t = parametric_from_point(v1, v2, u1)
        if fuzzy_in_range(seg1_t * seg1_len, 0.0, seg1_len, eps):
            return LineLineIntr("true", seg1_t=seg1_t, seg2_t=0.0)
        return LineLineIntr("none")

    # Neither a point: test for overlap.
    w2 = v2 - u1
    if fuzzy_eq_zero(u.x, eps):
        seg2_t0, seg2_t1 = w.y / u.y, w2.y / u.y
    else:
        seg2_t0, seg2_t1 = w.x / u.x, w2.x / u.x
    if seg2_t0 > seg2_t1:
        seg2_t0, seg2_t1 = seg2_t1, seg2_t0

    # "Sticky" thresholds: prefer to call a near-touch an intersect. These mirror
    # the crate's fuzzy_lt_eps (a < b + eps) / fuzzy_gt_eps (a > b - eps).
    if not (seg2_t0 * seg2_len < seg2_len + eps) or not (seg2_t1 * seg2_len > -eps):
        return LineLineIntr("none")

    seg2_t0 = max(seg2_t0, 0.0)
    seg2_t1 = min(seg2_t1, 1.0)

    if fuzzy_eq_zero((seg2_t1 - seg2_t0) * seg2_len, eps):
        # Segments line up end-to-end: a single touch point.
        seg1_t = 0.0 if (v1.fuzzy_eq_eps(u1, eps) or v1.fuzzy_eq_eps(u2, eps)) else 1.0
        return LineLineIntr("true", seg1_t=seg1_t, seg2_t=seg2_t0)

    return LineLineIntr("overlapping", seg2_t0=seg2_t0, seg2_t1=seg2_t1)


@dataclass(frozen=True, slots=True)
class LineCircleIntr:
    """Result of :func:`line_circle_intr`. `kind` in {none, tangent, two}."""

    kind: str
    t0: float = 0.0
    t1: float = 0.0


def line_circle_intr(p0: Vector2, p1: Vector2, radius: float, center: Vector2, eps: float) -> LineCircleIntr:
    """
    Intersect line segment p0->p1 with a circle, returning parametric t values.

    Solves in Cartesian form (line ``Ax+By+C=0`` vs. circle) rather than via the
    quadratic in t — the crate found that more numerically stable. Intersects are
    "sticky": a near-tangent line snaps to a single tangent point.
    """
    dx = p1.x - p0.x
    dy = p1.y - p0.y
    h, k = center.x, center.y

    if p0.fuzzy_eq_eps(p1, eps):
        xh = (p0.x + p1.x) / 2.0 - h
        yk = (p0.y + p1.y) / 2.0 - k
        if fuzzy_eq(xh * xh + yk * yk, radius * radius, eps):
            return LineCircleIntr("tangent", t0=0.0)
        return LineCircleIntr("none")

    p0s = p0 - center
    p1s = p1 - center

    # Note: this branch just avoids a tiny denominator, so it uses the general
    # float epsilon, not the coarser position one (matches the crate).
    if fuzzy_eq_zero(dx):
        x_pos = (p1s.x + p0s.x) / 2.0
        a, b, c = 1.0, 0.0, -x_pos
    else:
        m = dy / dx
        a, b, c = m, -1.0, p1s.y - m * p1s.x

    a2, b2, c2 = a * a, b * b, c * c
    r2 = radius * radius
    a2_b2 = a2 + b2
    shortest_dist = abs(c) / math.sqrt(a2_b2)

    if shortest_dist > radius + eps:
        return LineCircleIntr("none")

    x0 = -a * c / a2_b2 + h
    y0 = -b * c / a2_b2 + k

    if fuzzy_eq(shortest_dist, radius, eps):
        return LineCircleIntr("tangent", t0=parametric_from_point(p0, p1, Vector2(x0, y0)))

    d = r2 - c2 / a2_b2
    mult = math.sqrt(abs(d / a2_b2))
    sol1 = parametric_from_point(p0, p1, Vector2(x0 + b * mult, y0 - a * mult))
    sol2 = parametric_from_point(p0, p1, Vector2(x0 - b * mult, y0 + a * mult))
    t0, t1 = (sol1, sol2) if sol1 < sol2 else (sol2, sol1)
    return LineCircleIntr("two", t0=t0, t1=t1)


@dataclass(frozen=True, slots=True)
class CircleCircleIntr:
    """Result of :func:`circle_circle_intr`. `kind` in {none, tangent, two, overlapping}."""

    kind: str
    point1: Vector2 | None = None
    point2: Vector2 | None = None


def circle_circle_intr(r1: float, c1: Vector2, r2: float, c2: Vector2, eps: float) -> CircleCircleIntr:
    """Intersect two circles (Paul Bourke's construction)."""
    cv = c2 - c1
    d2 = cv.dot(cv)
    d = math.sqrt(d2)

    if fuzzy_eq_zero(d, eps):
        if fuzzy_eq(r1, r2, eps):
            return CircleCircleIntr("overlapping")
        return CircleCircleIntr("none")

    # d must be fuzzy-less-than the radius sum and fuzzy-greater-than the radius
    # difference (fuzzy_lt_eps: a < b + eps; fuzzy_gt_eps: a > b - eps).
    if not (d < r1 + r2 + eps) or not (d > abs(r1 - r2) - eps):
        return CircleCircleIntr("none")

    rad1_sq = r1 * r1
    a = (rad1_sq - r2 * r2 + d2) / (2.0 * d)
    mid = c1 + cv.scale(a / d)
    diff = rad1_sq - a * a

    if diff < 0.0:
        return CircleCircleIntr("tangent", point1=mid)

    h = math.sqrt(diff)
    h_over_d = h / d
    x_term = h_over_d * cv.y
    y_term = h_over_d * cv.x
    pt1 = Vector2(mid.x + x_term, mid.y - y_term)
    pt2 = Vector2(mid.x - x_term, mid.y + y_term)

    if pt1.fuzzy_eq_eps(pt2, eps):
        return CircleCircleIntr("tangent", point1=pt1)
    return CircleCircleIntr("two", point1=pt1, point2=pt2)
