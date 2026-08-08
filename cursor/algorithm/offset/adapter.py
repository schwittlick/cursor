"""
Bridge between the arc-native offset world and the rest of the cursor library.

The offset engine speaks :class:`~cursor.algorithm.offset.pline.Pline` (with exact
arcs); the plotters speak :class:`cursor.path.Path` (a list of points). This module
converts between them:

  * :func:`pline_to_path` / :func:`plines_to_paths` — tessellate arcs into points at
    a controlled chord tolerance, on the way *out* to a plotter.
  * :func:`path_to_pline` — read a point path back in as a straight-segment polyline
    (all bulges zero), on the way *in*.

Tessellation happens only at this boundary, deliberately. Keep offsets in ``Pline``
form for as long as possible — a nested/concentric offset chain stays exact and only
becomes points when it is finally handed to a renderer.
"""

from __future__ import annotations

import math

from cursor.path import Path

from .geom import angle_of, delta_angle_signed
from .pline import Pline
from .segment import seg_arc_radius_and_center

# Default max distance between the true arc and its chord approximation, in the same
# units as the geometry. 0.05 is well below plotter resolution at typical drawing scale.
DEFAULT_CHORD_TOLERANCE = 0.05


def _arc_point_count(radius: float, sweep: float, chord_tol: float) -> int:
    """How many chords to approximate an arc of ``sweep`` radians within ``chord_tol``."""
    if radius <= 0.0 or chord_tol <= 0.0:
        return 1
    # Max angular step whose chord sags no more than chord_tol below the arc.
    ratio = 1.0 - chord_tol / radius
    if ratio <= -1.0:
        return 1
    max_step = 2.0 * math.acos(max(ratio, -1.0))
    if max_step <= 0.0:
        return 1
    return max(1, math.ceil(abs(sweep) / max_step))


def pline_vertices_as_points(
    pline: Pline, chord_tolerance: float = DEFAULT_CHORD_TOLERANCE
) -> list[tuple[float, float]]:
    """Tessellate ``pline`` into a flat list of ``(x, y)`` points (arcs become chords)."""
    pts: list[tuple[float, float]] = []
    n = len(pline)
    if n == 0:
        return pts
    if n == 1:
        return [(pline[0].x, pline[0].y)]

    first = pline[0]
    pts.append((first.x, first.y))

    for v1, v2 in pline.iter_segments():
        if v1.bulge_is_zero():
            pts.append((v2.x, v2.y))
            continue
        radius, center = seg_arc_radius_and_center(v1, v2)
        start_angle = angle_of(center, v1.pos)
        end_angle = angle_of(center, v2.pos)
        sweep = delta_angle_signed(start_angle, end_angle, v1.bulge_is_neg())
        steps = _arc_point_count(radius, sweep, chord_tolerance)
        for i in range(1, steps + 1):
            a = start_angle + sweep * (i / steps)
            pts.append((center.x + radius * math.cos(a), center.y + radius * math.sin(a)))

    # A closed polyline's tessellation ends back at the first point; make that explicit.
    if pline.is_closed and pts and pts[0] != pts[-1]:
        pts.append(pts[0])
    return pts


def pline_to_path(pline: Pline, chord_tolerance: float = DEFAULT_CHORD_TOLERANCE) -> Path:
    """Tessellate a :class:`Pline` into a :class:`cursor.path.Path`."""
    path = Path()
    for x, y in pline_vertices_as_points(pline, chord_tolerance):
        path.add(x, y)
    return path


def plines_to_paths(plines: list[Pline], chord_tolerance: float = DEFAULT_CHORD_TOLERANCE) -> list[Path]:
    """Tessellate each of several plines (e.g. an offset result) into paths."""
    return [pline_to_path(pl, chord_tolerance) for pl in plines]


def path_to_pline(path: Path, is_closed: bool = False) -> Pline:
    """
    Read a :class:`cursor.path.Path` in as a straight-segment :class:`Pline`.

    Every bulge is zero — a point path carries no arc information. If the path's last
    point coincides with its first it is dropped and ``is_closed`` is implied, matching
    the polyline convention that a closed ring does not repeat its start vertex.
    """
    verts = [(float(p.x), float(p.y), 0.0) for p in path]
    if len(verts) >= 2 and verts[0][0] == verts[-1][0] and verts[0][1] == verts[-1][1]:
        verts.pop()
        is_closed = True
    return Pline.from_vertices(verts, is_closed=is_closed)
