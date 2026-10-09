"""
Closed-area detection and hatch filling.

This exists for traced scans: a heap of open polylines that read as closed
shapes to the eye but almost never are, so the regions have to be recovered
geometrically rather than read off a flag. detect_regions() recovers them,
hatch() fills one.

Both work in whatever units the collection is already in. Call them after
fitting a collection to a plotter, so that a spacing of "0.3 mm" can be
expressed in plotter units and actually come out 0.3 mm on paper.
"""

from __future__ import annotations

import math

from shapely.affinity import rotate
from shapely.geometry import LineString, MultiLineString, Polygon
from shapely.ops import polygonize, unary_union

from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position


def _extend(coords: list[tuple[float, float]], gap: float) -> list[tuple[float, float]]:
    """Push both ends outward along their terminal segment by `gap`."""

    def push(tip, inner):
        dx, dy = tip[0] - inner[0], tip[1] - inner[1]
        length = math.hypot(dx, dy)
        if length == 0:
            return tip
        return (tip[0] + dx / length * gap, tip[1] + dy / length * gap)

    return [push(coords[0], coords[1]), *coords, push(coords[-1], coords[-2])]


def detect_regions(collection: Collection, gap: float = 0.0, min_area: float = 0.0) -> list[Polygon]:
    """
    The closed faces enclosed by a collection's polylines, smallest first.

    A traced outline usually fails to close by a hair, and polygonising it as-is
    silently drops the region. `gap` extends every polyline past both of its
    ends first, which bridges those near misses and the T-junctions where one
    stroke stops short of another. It is a blunt instrument: overshoots cross
    each other and spawn small spurious faces, so raise `min_area` alongside it.
    """
    lines = []
    for path in collection:
        coords = path.as_tuple_list()
        if len(coords) < 2:
            continue
        lines.append(LineString(_extend(coords, gap) if gap > 0 else coords))

    if not lines:
        return []

    faces = polygonize(unary_union(MultiLineString(lines)))
    return sorted((f for f in faces if f.area > min_area), key=lambda f: f.area)


def hatch(region: Polygon, spacing: float, angle_deg: float = 45.0) -> Collection:
    """
    Fill one region with parallel lines `spacing` apart.

    Spacing at or below the pen width reads as solid colour, above it as
    texture. Rows alternate direction, so the pen hops one row sideways between
    them instead of returning across the whole region.
    """
    if spacing <= 0:
        raise ValueError(f"spacing must be positive, got {spacing}")

    filled = Collection()
    if region.is_empty or region.area <= 0:
        return filled

    turned = rotate(region, -angle_deg, origin=(0, 0))
    minx, miny, maxx, maxy = turned.bounds

    rows = []
    y = miny + spacing / 2.0
    while y < maxy:
        cut = LineString([(minx - spacing, y), (maxx + spacing, y)]).intersection(turned)
        parts = cut.geoms if hasattr(cut, "geoms") else [cut]
        segments = [list(p.coords) for p in parts if isinstance(p, LineString) and p.length > 0]
        segments.sort(key=lambda s: s[0][0])
        if segments:
            rows.append(segments)
        y += spacing

    cos_a, sin_a = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
    for i, segments in enumerate(rows):
        if i % 2:
            segments = [s[::-1] for s in reversed(segments)]
        for segment in segments:
            path = Path()
            for x, y in segment:
                path.add_position(Position(x * cos_a - y * sin_a, x * sin_a + y * cos_a))
            filled.add(path)

    return filled
