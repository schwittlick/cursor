"""
Polyline measurements: path length, signed area, extents.

Ported from the corresponding ``PlineSource`` methods in the Rust crate. These are
what the offset test oracle compares (a result polyline is identified by its area,
length, and bounding box), and they are useful in their own right.
"""

from __future__ import annotations

from .geom import angle_from_bulge
from .pline import Pline
from .segment import seg_bounding_box, seg_length


def path_length(pline: Pline) -> float:
    return sum(seg_length(v1, v2) for v1, v2 in pline.iter_segments())


def area(pline: Pline) -> float:
    """
    Signed area of a closed polyline (0 for an open one).

    Shoelace formula extended for bulge arcs: each arc adds (CCW) or subtracts (CW)
    its circular-segment area — the sector minus the chord triangle. Positive for a
    counter-clockwise polygon, negative for clockwise, exactly as the crate defines it.
    """
    if not pline.is_closed:
        return 0.0
    double_area = 0.0
    for v1, v2 in pline.iter_segments():
        double_area += v1.x * v2.y - v1.y * v2.x
        if not v1.bulge_is_zero():
            b = abs(v1.bulge)
            sweep = angle_from_bulge(b)
            base = (v2.pos - v1.pos).length()
            radius = base * ((b * b + 1.0) / (4.0 * b))
            sagitta = b * base / 2.0
            height = radius - sagitta
            double_arc = sweep * radius * radius - base * height
            if v1.bulge_is_neg():
                double_arc = -double_arc
            double_area += double_arc
    return double_area / 2.0


def extents(pline: Pline) -> tuple[float, float, float, float] | None:
    """Axis-aligned bounds ``(min_x, min_y, max_x, max_y)``, or ``None`` if empty."""
    if len(pline) == 0:
        return None
    if len(pline) == 1:
        v = pline[0]
        return (v.x, v.y, v.x, v.y)
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    for v1, v2 in pline.iter_segments():
        bx0, by0, bx1, by1 = seg_bounding_box(v1, v2)
        min_x, min_y = min(min_x, bx0), min(min_y, by0)
        max_x, max_y = max(max_x, bx1), max(max_y, by1)
    return (min_x, min_y, max_x, max_y)
