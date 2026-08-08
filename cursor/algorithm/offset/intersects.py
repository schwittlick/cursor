"""
Finding intersections *of* and *between* polylines, ported from
``polyline::internal::pline_intersects``.

The offset engine needs two things from this module:

  * ``all_self_intersects`` — everywhere a (raw offset) polyline crosses itself.
    Split into *local* (adjacent segments sharing a vertex) and *global*
    (non-adjacent) exactly as the crate does, because the two are found by
    different reasoning.
  * ``find_intersects`` — everywhere two polylines cross, used for the dual-offset
    clipping of open / self-intersecting inputs.

Spatial index
-------------
The crate drives the global search with a Hilbert R-tree; we use the grid index in
:mod:`cursor.algorithm.offset.spatial` instead (simpler, dependency-free, and a good
fit for roughly-uniform plotter geometry). Each segment queries the grid for the few
others whose bounding boxes are near it, and only those reach the exact per-segment
intersection test — turning the naive O(n^2) all-pairs scan into roughly linear work.
The grid returns a superset of the truly-near segments, so the result is identical to
the brute-force scan.
"""

from __future__ import annotations

from dataclasses import dataclass

from .geom import FUZZY_EPS, Vector2
from .pline import Pline, PlineVertex
from .seg_intersect import pline_seg_intr
from .segment import segment_bboxes
from .spatial import SpatialGrid


@dataclass(frozen=True, slots=True)
class BasicIntersect:
    """A point where two segments cross, tagged with both segments' start indices."""

    start_index1: int
    start_index2: int
    point: Vector2


@dataclass(frozen=True, slots=True)
class OverlappingIntersect:
    """A stretch where two segments are coincident, spanning ``point1`` to ``point2``."""

    start_index1: int
    start_index2: int
    point1: Vector2
    point2: Vector2


@dataclass(slots=True)
class IntersectsCollection:
    basic: list[BasicIntersect]
    overlapping: list[OverlappingIntersect]


def _seg_endpoints(pline: Pline) -> list[tuple[PlineVertex, PlineVertex]]:
    return list(pline.iter_segments())


def visit_local_self_intersects(pline: Pline, pos_eps: float) -> IntersectsCollection:
    """
    Intersects between segments that share a vertex.

    For each triple of consecutive vertices (i, j, k) test segment i->j against
    j->k, ignoring the shared vertex j itself; a coincident vertex (singularity)
    or an overlap is recorded specially.
    """
    coll = IntersectsCollection([], [])
    vc = len(pline)
    if vc < 2:
        return coll

    if vc == 2:
        if pline.is_closed and abs(pline[0].bulge + pline[1].bulge) < FUZZY_EPS:
            coll.overlapping.append(OverlappingIntersect(0, 1, pline[0].pos, pline[1].pos))
        return coll

    def visit(i: int, j: int, k: int) -> None:
        v1, v2, v3 = pline[i], pline[j], pline[k]
        if v1.pos.fuzzy_eq_eps(v2.pos, pos_eps):
            coll.overlapping.append(OverlappingIntersect(i, j, v1.pos, v2.pos))
            return
        res = pline_seg_intr(v1, v2, v2, v3, pos_eps)
        if res.kind == "none":
            return
        if res.kind in ("tangent", "one"):
            if not res.point1.fuzzy_eq_eps(v2.pos, pos_eps):
                coll.basic.append(BasicIntersect(i, j, res.point1))
        elif res.kind == "two":
            if not res.point1.fuzzy_eq_eps(v2.pos, pos_eps):
                coll.basic.append(BasicIntersect(i, j, res.point1))
            if not res.point2.fuzzy_eq_eps(v2.pos, pos_eps):
                coll.basic.append(BasicIntersect(i, j, res.point2))
        else:  # overlapping_lines / overlapping_arcs
            coll.overlapping.append(OverlappingIntersect(i, j, res.point1, res.point2))

    for i in range(2, vc):
        visit(i - 2, i - 1, i)

    if pline.is_closed:
        visit(vc - 2, vc - 1, 0)
        visit(vc - 1, 0, 1)

    return coll


def visit_global_self_intersects(pline: Pline, pos_eps: float) -> IntersectsCollection:
    """Intersects between segments that do **not** share a vertex."""
    coll = IntersectsCollection([], [])
    vc = len(pline)
    if vc < 3:
        return coll

    segs = _seg_endpoints(pline)
    boxes = segment_bboxes(pline)
    grid = SpatialGrid(boxes)
    # Segment i starts at vertex i; its end vertex is next_wrapping_index(i).

    for i, (v1, v2) in enumerate(segs):
        bb = boxes[i]
        for j in grid.query(bb[0] - pos_eps, bb[1] - pos_eps, bb[2] + pos_eps, bb[3] + pos_eps):
            # Each unordered pair once, and never a segment against itself.
            if j <= i:
                continue
            ni = pline.next_wrapping_index(i)
            nj = pline.next_wrapping_index(j)
            # Skip segments that share a vertex — those are the local case.
            if i == nj or ni == j or ni == nj:
                continue

            u1, u2 = segs[j]

            def skip_at_end(pt: Vector2, v2=v2, u2=u2) -> bool:
                # An intersect at both segments' end vertices is found again by their
                # successors with it as a start point, so drop it here.
                return v2.pos.fuzzy_eq_eps(pt, pos_eps) and u2.pos.fuzzy_eq_eps(pt, pos_eps)

            res = pline_seg_intr(v1, v2, u1, u2, pos_eps)
            si, sj = i, j
            if res.kind == "none":
                continue
            if res.kind in ("tangent", "one"):
                if not skip_at_end(res.point1):
                    coll.basic.append(BasicIntersect(si, sj, res.point1))
            elif res.kind == "two":
                if not skip_at_end(res.point1):
                    coll.basic.append(BasicIntersect(si, sj, res.point1))
                if not skip_at_end(res.point2):
                    coll.basic.append(BasicIntersect(si, sj, res.point2))
            else:  # overlapping
                if not skip_at_end(res.point1):
                    coll.overlapping.append(OverlappingIntersect(si, sj, res.point1, res.point2))

    return coll


def all_self_intersects(pline: Pline, include_overlapping: bool, pos_eps: float) -> list[BasicIntersect]:
    """
    All self-intersects as basic (point) intersects — local plus global.

    When ``include_overlapping`` is true each overlap contributes its two endpoints
    as basic intersects; otherwise overlaps are dropped. The offset engine calls
    this with ``include_overlapping=False``.
    """
    local = visit_local_self_intersects(pline, pos_eps)
    glob = visit_global_self_intersects(pline, pos_eps)

    out: list[BasicIntersect] = []
    out.extend(local.basic)
    out.extend(glob.basic)
    if include_overlapping:
        for o in (*local.overlapping, *glob.overlapping):
            out.append(BasicIntersect(o.start_index1, o.start_index2, o.point1))
            out.append(BasicIntersect(o.start_index1, o.start_index2, o.point2))
    return out


def find_intersects(pline1: Pline, pline2: Pline, pos_eps: float) -> IntersectsCollection:
    """
    All intersects between two polylines.

    Records the segment start index on *each* polyline. Intersects sitting exactly
    on a segment's end vertex are skipped (they resurface on the next segment with
    it as a start point) — except at the genuine final vertex of an open polyline,
    which has no successor. Overlaps can create duplicate endpoint intersects; a
    final pass removes those, matching the crate.
    """
    result = IntersectsCollection([], [])
    if len(pline1) < 2 or len(pline2) < 2:
        return result

    segs1 = _seg_endpoints(pline1)
    segs2 = _seg_endpoints(pline2)
    boxes1 = segment_bboxes(pline1)
    boxes2 = segment_bboxes(pline2)
    grid1 = SpatialGrid(boxes1)

    open1_last = len(pline1) - 2
    open2_last = len(pline2) - 2

    dup1: set[int] = set()
    dup2: set[int] = set()

    for i2, (u1, u2) in enumerate(segs2):
        bb = boxes2[i2]
        for i1 in grid1.query(bb[0] - pos_eps, bb[1] - pos_eps, bb[2] + pos_eps, bb[3] + pos_eps):
            v1, v2 = segs1[i1]

            def skip_at_end(pt: Vector2, v2=v2, u2=u2, i1=i1) -> bool:
                return (v2.pos.fuzzy_eq_eps(pt, pos_eps) and (pline1.is_closed or i1 != open1_last)) or (
                    u2.pos.fuzzy_eq_eps(pt, pos_eps) and (pline2.is_closed or i2 != open2_last)
                )

            res = pline_seg_intr(v1, v2, u1, u2, pos_eps)
            if res.kind == "none":
                continue
            if res.kind in ("tangent", "one"):
                if not skip_at_end(res.point1):
                    result.basic.append(BasicIntersect(i1, i2, res.point1))
            elif res.kind == "two":
                if not skip_at_end(res.point1):
                    result.basic.append(BasicIntersect(i1, i2, res.point1))
                if not skip_at_end(res.point2):
                    result.basic.append(BasicIntersect(i1, i2, res.point2))
            else:  # overlapping
                result.overlapping.append(OverlappingIntersect(i1, i2, res.point1, res.point2))
                if v2.pos.fuzzy_eq_eps(res.point1, pos_eps) or v2.pos.fuzzy_eq_eps(res.point2, pos_eps):
                    dup1.add(pline1.next_wrapping_index(i1))
                if u2.pos.fuzzy_eq_eps(res.point1, pos_eps) or u2.pos.fuzzy_eq_eps(res.point2, pos_eps):
                    dup2.add(pline2.next_wrapping_index(i2))

    if not dup1 and not dup2:
        return result

    filtered = []
    for intr in result.basic:
        if intr.start_index1 in dup1 and intr.point.fuzzy_eq_eps(pline1[intr.start_index1].pos, pos_eps):
            continue
        if intr.start_index2 in dup2 and intr.point.fuzzy_eq_eps(pline2[intr.start_index2].pos, pos_eps):
            continue
        filtered.append(intr)
    result.basic = filtered
    return result
