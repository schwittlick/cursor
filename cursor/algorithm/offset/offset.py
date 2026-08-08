"""
The parallel offset engine, ported from ``polyline::internal::pline_offset``.

This is the algorithm the whole package exists for. Offsetting a polyline is not
just "shift every segment sideways": where the shape turns tighter than the offset
distance, the shifted pieces overshoot and the naive result self-intersects or
folds back on itself. The crate's approach — reproduced faithfully here — is:

  1. **Raw offset** (:func:`create_raw_offset_polyline`). Offset every segment
     (a line moves sideways; an arc grows or shrinks its radius, collapsing to a
     line if the radius would go negative) and stitch neighbours together, filling
     outward corners with joining arcs. The result is connected but may be locally
     wrong — it can loop over itself.

  2. **Slice** at self-intersections (:func:`slices_from_raw_offset`, or
     :func:`slices_from_dual_raw_offsets` for open / self-intersecting inputs,
     which also offsets by ``-offset`` and clips against that "dual"). Each slice
     is a candidate piece of the true offset.

  3. **Keep** the slices that stay at least ``|offset|`` from the *original*
     polyline (:func:`point_valid_for_offset`) and don't cross it. The overshoot
     loops fail this and are dropped.

  4. **Stitch** the survivors back into whole polylines
     (:func:`stitch_slices_together`), re-closing them if the input was closed.

Because everything is arc-native, the joins in step 1 are exact arcs — the reason
this beats a straight-segment offset for repeated/nested offsetting, where chord
error would otherwise accumulate.

Spatial queries are brute-force here (the R-tree is deferred, see the package
README); the distance and intersection scans loop over the original polyline's
segments. The interfaces are shaped so an index can be slotted in later without
changing the algorithm.
"""

from __future__ import annotations

from dataclasses import dataclass

from .geom import (
    FUZZY_EPS,
    Vector2,
    angle_of,
    bulge_from_angle,
    circle_circle_intr,
    delta_angle,
    delta_angle_signed,
    dist_squared,
    line_circle_intr,
    line_line_intr,
    point_from_parametric,
    point_within_arc_sweep,
)
from .intersects import all_self_intersects, find_intersects
from .pline import Pline, PlineVertex
from .seg_intersect import pline_seg_intr
from .segment import seg_arc_radius_and_center, seg_closest_point, seg_midpoint
from .view import PlineViewData


@dataclass(slots=True)
class OffsetOptions:
    """Tunables for :func:`parallel_offset`, with the crate's defaults."""

    pos_equal_eps: float = 1e-5
    """Two positions closer than this are treated as the same point."""
    slice_join_eps: float = 1e-4
    """Slice endpoints closer than this are treated as connected when stitching."""
    offset_dist_eps: float = 1e-4
    """Slack on the "at least |offset| from the original" distance test."""
    handle_self_intersects: bool = False
    """If true, use dual-offset clipping even for closed inputs (handles self-crossing shapes)."""


@dataclass(slots=True)
class _RawSeg:
    """One parallel-offset segment before neighbours are joined."""

    v1: PlineVertex
    v2: PlineVertex
    orig_v2_pos: Vector2
    collapsed_arc: bool


# ---------------------------------------------------------------------------
# Step 1a: raw offset segments
# ---------------------------------------------------------------------------


def create_untrimmed_raw_offset_segs(pline: Pline, offset: float) -> list[_RawSeg]:
    """Offset each segment independently (before any joining/trimming)."""
    result: list[_RawSeg] = []
    for v1, v2 in pline.iter_segments():
        if v1.bulge_is_zero():
            line_v = v2.pos - v1.pos
            offset_v = line_v.safe_unit_perp().scale(offset)
            result.append(
                _RawSeg(
                    PlineVertex((v1.pos + offset_v).x, (v1.pos + offset_v).y, 0.0),
                    PlineVertex((v2.pos + offset_v).x, (v2.pos + offset_v).y, 0.0),
                    v2.pos,
                    False,
                )
            )
        else:
            arc_radius, arc_center = seg_arc_radius_and_center(v1, v2)
            offs = offset if v1.bulge_is_neg() else -offset
            radius_after = arc_radius + offs
            v1_to_center = (v1.pos - arc_center).safe_normalize()
            v2_to_center = (v2.pos - arc_center).safe_normalize()
            if radius_after < FUZZY_EPS:
                # Arc collapses (radius reached or crossed zero): turn it into a line.
                # Uses the crate's fuzzy_lt(0) so an exactly-zero radius counts as collapsed
                # rather than slipping through as a zero-radius arc (division by zero).
                new_v1_bulge, collapsed = 0.0, True
            else:
                new_v1_bulge, collapsed = v1.bulge, False
            new_v1 = v1_to_center.scale(offs) + v1.pos
            new_v2 = v2_to_center.scale(offs) + v2.pos
            result.append(
                _RawSeg(
                    PlineVertex(new_v1.x, new_v1.y, new_v1_bulge),
                    PlineVertex(new_v2.x, new_v2.y, v2.bulge),
                    v2.pos,
                    collapsed,
                )
            )
    return result


def _is_false_intersect(t: float) -> bool:
    return t < 0.0 or t > 1.0


def _bulge_for_connection(arc_center: Vector2, sp: Vector2, ep: Vector2, is_ccw: bool) -> float:
    a1 = angle_of(arc_center, sp)
    a2 = angle_of(arc_center, ep)
    return bulge_from_angle(delta_angle_signed(a1, a2, not is_ccw))


def _connect_using_arc(s1: _RawSeg, s2: _RawSeg, ccw: bool, result: Pline, pos_eps: float) -> None:
    """Bridge a gap between two raw segments with a joining arc about the original vertex."""
    arc_center = s1.orig_v2_pos
    sp = s1.v2.pos
    ep = s2.v1.pos
    bulge = _bulge_for_connection(arc_center, sp, ep, ccw)
    result.add_or_replace(sp.x, sp.y, bulge, pos_eps)
    result.add_or_replace(ep.x, ep.y, s2.v1.bulge, pos_eps)


# ---------------------------------------------------------------------------
# Step 1b: join adjacent raw offset segments
# ---------------------------------------------------------------------------


def _line_line_join(s1: _RawSeg, s2: _RawSeg, ccw: bool, result: Pline, pos_eps: float) -> None:
    v1, v2, u1, u2 = s1.v1, s1.v2, s2.v1, s2.v2
    if s1.collapsed_arc or s2.collapsed_arc:
        _connect_using_arc(s1, s2, ccw, result, pos_eps)
        return
    res = line_line_intr(v1.pos, v2.pos, u1.pos, u2.pos, pos_eps)
    if res.kind == "none":
        # Parallel: join with a half circle.
        bulge = 1.0 if ccw else -1.0
        result.add_or_replace(v2.x, v2.y, bulge, pos_eps)
        result.add_or_replace(u1.x, u1.y, u1.bulge, pos_eps)
    elif res.kind == "true":
        p = point_from_parametric(v1.pos, v2.pos, res.seg1_t)
        result.add_or_replace(p.x, p.y, 0.0, pos_eps)
    elif res.kind == "overlapping":
        result.add_or_replace(v2.x, v2.y, 0.0, pos_eps)
    else:  # false
        if res.seg1_t > 1.0 and _is_false_intersect(res.seg2_t):
            _connect_using_arc(s1, s2, ccw, result, pos_eps)
        else:
            result.add_or_replace(v2.x, v2.y, 0.0, pos_eps)
            result.add_or_replace(u1.x, u1.y, u1.bulge, pos_eps)


def _line_arc_join(s1: _RawSeg, s2: _RawSeg, ccw: bool, result: Pline, pos_eps: float) -> None:
    v1, v2, u1, u2 = s1.v1, s1.v2, s2.v1, s2.v2
    arc_radius, arc_center = seg_arc_radius_and_center(u1, u2)

    def process(t: float, intersect: Vector2) -> None:
        true_line = not _is_false_intersect(t)
        true_arc = point_within_arc_sweep(arc_center, u1.pos, u2.pos, u1.bulge_is_neg(), intersect, pos_eps)
        if true_line and true_arc:
            a = angle_of(arc_center, intersect)
            end_angle = angle_of(arc_center, u2.pos)
            theta = delta_angle(a, end_angle)
            if (theta > 0.0) == u1.bulge_is_pos():
                result.add_or_replace(intersect.x, intersect.y, bulge_from_angle(theta), pos_eps)
            else:
                result.add_or_replace(intersect.x, intersect.y, u1.bulge, pos_eps)
            return
        if t > 1.0 and not true_arc:
            _connect_using_arc(s1, s2, ccw, result, pos_eps)
            return
        if s1.collapsed_arc:
            _connect_using_arc(s1, s2, ccw, result, pos_eps)
            return
        result.add_or_replace(v2.x, v2.y, 0.0, pos_eps)
        result.add_or_replace_vertex(u1, pos_eps)

    res = line_circle_intr(v1.pos, v2.pos, arc_radius, arc_center, pos_eps)
    if res.kind == "none":
        _connect_using_arc(s1, s2, ccw, result, pos_eps)
    elif res.kind == "tangent":
        process(res.t0, point_from_parametric(v1.pos, v2.pos, res.t0))
    else:
        intr1 = point_from_parametric(v1.pos, v2.pos, res.t0)
        intr2 = point_from_parametric(v1.pos, v2.pos, res.t1)
        if dist_squared(intr1, s1.orig_v2_pos) < dist_squared(intr2, s1.orig_v2_pos):
            process(res.t0, intr1)
        else:
            process(res.t1, intr2)


def _arc_line_join(s1: _RawSeg, s2: _RawSeg, ccw: bool, result: Pline, pos_eps: float) -> None:
    v1, v2, u1, u2 = s1.v1, s1.v2, s2.v1, s2.v2
    arc_radius, arc_center = seg_arc_radius_and_center(v1, v2)

    def process(t: float, intersect: Vector2) -> None:
        true_line = not _is_false_intersect(t)
        true_arc = point_within_arc_sweep(arc_center, v1.pos, v2.pos, v1.bulge_is_neg(), intersect, pos_eps)
        if true_line and true_arc:
            prev = result.last()
            if not prev.bulge_is_zero() and not prev.pos.fuzzy_eq_eps(v2.pos, pos_eps):
                a = angle_of(arc_center, intersect)
                _, prev_center = seg_arc_radius_and_center(prev, v2)
                prev_start_angle = angle_of(prev_center, prev.pos)
                updated_theta = delta_angle(prev_start_angle, a)
                if (updated_theta > 0.0) == prev.bulge_is_pos():
                    result.set_last(result.last().with_bulge(bulge_from_angle(updated_theta)))
            result.add_or_replace(intersect.x, intersect.y, 0.0, pos_eps)
            return
        _connect_using_arc(s1, s2, ccw, result, pos_eps)

    res = line_circle_intr(u1.pos, u2.pos, arc_radius, arc_center, pos_eps)
    if res.kind == "none":
        _connect_using_arc(s1, s2, ccw, result, pos_eps)
    elif res.kind == "tangent":
        process(res.t0, point_from_parametric(u1.pos, u2.pos, res.t0))
    else:
        orig = u1.pos if s2.collapsed_arc else s1.orig_v2_pos
        intr1 = point_from_parametric(u1.pos, u2.pos, res.t0)
        intr2 = point_from_parametric(u1.pos, u2.pos, res.t1)
        if dist_squared(intr1, orig) < dist_squared(intr2, orig):
            process(res.t0, intr1)
        else:
            process(res.t1, intr2)


def _arc_arc_join(s1: _RawSeg, s2: _RawSeg, ccw: bool, result: Pline, pos_eps: float) -> None:
    v1, v2, u1, u2 = s1.v1, s1.v2, s2.v1, s2.v2
    r1, c1 = seg_arc_radius_and_center(v1, v2)
    r2, c2 = seg_arc_radius_and_center(u1, u2)

    def both_sweep(p: Vector2) -> bool:
        return point_within_arc_sweep(c1, v1.pos, v2.pos, v1.bulge_is_neg(), p, pos_eps) and point_within_arc_sweep(
            c2, u1.pos, u2.pos, u1.bulge_is_neg(), p, pos_eps
        )

    def process(intersect: Vector2, true_intersect: bool) -> None:
        if not true_intersect:
            _connect_using_arc(s1, s2, ccw, result, pos_eps)
            return
        prev = result.last()
        if not prev.bulge_is_zero() and not prev.pos.fuzzy_eq_eps(v2.pos, pos_eps):
            a1 = angle_of(c1, intersect)
            _, prev_center = seg_arc_radius_and_center(prev, v2)
            prev_start_angle = angle_of(prev_center, prev.pos)
            updated_theta = delta_angle(prev_start_angle, a1)
            if (updated_theta > 0.0) == prev.bulge_is_pos():
                result.set_last(result.last().with_bulge(bulge_from_angle(updated_theta)))
        a2 = angle_of(c2, intersect)
        end_angle = angle_of(c2, u2.pos)
        theta = delta_angle(a2, end_angle)
        if (theta > 0.0) == u1.bulge_is_pos():
            result.add_or_replace(intersect.x, intersect.y, bulge_from_angle(theta), pos_eps)
        else:
            result.add_or_replace(intersect.x, intersect.y, u1.bulge, pos_eps)

    res = circle_circle_intr(r1, c1, r2, c2, pos_eps)
    if res.kind == "none":
        _connect_using_arc(s1, s2, ccw, result, pos_eps)
    elif res.kind == "tangent":
        process(res.point1, both_sweep(res.point1))
    elif res.kind == "two":
        d1 = dist_squared(res.point1, s1.orig_v2_pos)
        d2 = dist_squared(res.point2, s1.orig_v2_pos)
        if abs(d1 - d2) < pos_eps:
            # Equal distance (input arcs met at a tangent) — prefer a true intersect.
            if both_sweep(res.point1):
                process(res.point1, True)
            else:
                process(res.point2, both_sweep(res.point2))
        elif d1 < d2:
            process(res.point1, both_sweep(res.point1))
        else:
            process(res.point2, both_sweep(res.point2))
    else:  # overlapping
        result.add_or_replace_vertex(u1, pos_eps)


def _join_seg_pair(s1: _RawSeg, s2: _RawSeg, ccw: bool, result: Pline, pos_eps: float) -> None:
    s1_line = s1.v1.bulge_is_zero()
    s2_line = s2.v1.bulge_is_zero()
    if s1_line and s2_line:
        _line_line_join(s1, s2, ccw, result, pos_eps)
    elif s1_line and not s2_line:
        _line_arc_join(s1, s2, ccw, result, pos_eps)
    elif not s1_line and s2_line:
        _arc_line_join(s1, s2, ccw, result, pos_eps)
    else:
        _arc_arc_join(s1, s2, ccw, result, pos_eps)


def create_raw_offset_polyline(pline: Pline, offset: float, pos_eps: float) -> Pline:
    """Build the connected raw offset polyline (before slicing/clipping)."""
    vc = len(pline)
    if vc < 2:
        return Pline(is_closed=pline.is_closed)

    segs = create_untrimmed_raw_offset_segs(pline, offset)
    if not segs:
        return Pline(is_closed=pline.is_closed)
    if len(segs) == 1 and segs[0].collapsed_arc:
        return Pline(is_closed=pline.is_closed)

    ccw = offset < 0.0
    result = Pline(is_closed=pline.is_closed, capacity=vc)
    result.add_vertex(segs[0].v1)

    if len(segs) >= 2:
        _join_seg_pair(segs[0], segs[1], ccw, result, pos_eps)
    first_vertex_replaced = len(result) == 1

    for i in range(1, len(segs) - 1):
        _join_seg_pair(segs[i], segs[i + 1], ccw, result, pos_eps)

    if pline.is_closed and len(result) > 1:
        # Join the closing pair (last segment, first segment) into a temp, then fold it back in.
        closing = Pline(is_closed=False)
        closing.add_vertex(result.last())
        _join_seg_pair(segs[-1], segs[0], ccw, closing, pos_eps)

        result.set_last(closing[0])
        for k in range(1, len(closing)):
            result.add_vertex(closing[k])

        if not first_vertex_replaced:
            updated_first = closing.last().pos
            if result[0].bulge_is_zero():
                result.set(0, updated_first.x, updated_first.y, result[0].bulge)
            elif len(result) > 1:
                _, arc_center = seg_arc_radius_and_center(result[0], result[1])
                a1 = angle_of(arc_center, updated_first)
                a2 = angle_of(arc_center, result[1].pos)
                updated_theta = delta_angle(a1, a2)
                if (updated_theta < 0.0 and result[0].bulge_is_pos()) or (
                    updated_theta > 0.0 and result[0].bulge_is_neg()
                ):
                    result.set(0, updated_first.x, updated_first.y, result[0].bulge)
                else:
                    result.set(0, updated_first.x, updated_first.y, bulge_from_angle(updated_theta))

        # Prune singularities that the closing join may have introduced.
        if len(result) > 1:
            if result[0].pos.fuzzy_eq_eps(result.last().pos, pos_eps):
                result.remove_last()
            if len(result) > 1 and result[0].pos.fuzzy_eq_eps(result[1].pos, pos_eps):
                result.remove(0)
    else:
        result.add_or_replace_vertex(segs[-1].v2, pos_eps)

    if len(result) == 1:
        result.clear()
    return result


# ---------------------------------------------------------------------------
# Step 3: validity tests against the original polyline
# ---------------------------------------------------------------------------


def point_valid_for_offset(original: Pline, offset: float, point: Vector2, pos_eps: float, offset_tol: float) -> bool:
    """
    Is ``point`` at least ``|offset|`` (minus tolerance) from every segment of the
    original polyline? Points closer than that belong to overshoot loops and are cut.
    """
    abs_offset = abs(offset) - offset_tol
    min_dist = abs_offset * abs_offset
    for v1, v2 in original.iter_segments():
        closest = seg_closest_point(v1, v2, point, pos_eps)
        if dist_squared(closest, point) <= min_dist:
            return False
    return True


def _intersects_original(original: Pline, v1: PlineVertex, v2: PlineVertex, pos_eps: float) -> bool:
    for o1, o2 in original.iter_segments():
        if pline_seg_intr(v1, v2, o1, o2, pos_eps).kind != "none":
            return True
    return False


def _slice_is_valid(slice_data: PlineViewData, raw: Pline, original: Pline, offset: float, opts: OffsetOptions) -> bool:
    pos_eps = opts.pos_equal_eps
    offset_tol = opts.offset_dist_eps

    def point_ok(p: Vector2) -> bool:
        return point_valid_for_offset(original, offset, p, pos_eps, offset_tol)

    if slice_data.end_index_offset == 0:
        v1 = slice_data.updated_start
        if not point_ok(v1.pos):
            return False
        v2 = PlineVertex(slice_data.end_point.x, slice_data.end_point.y, 0.0)
        if not point_ok(v2.pos):
            return False
        if not point_ok(seg_midpoint(v1, v2)):
            return False
        return not _intersects_original(original, v1, v2, pos_eps)

    start_seg_mid = seg_midpoint(slice_data.updated_start, raw[raw.next_wrapping_index(slice_data.start_index)])
    if not point_ok(start_seg_mid):
        return False

    end_index = raw.fwd_wrapping_index(slice_data.start_index, slice_data.end_index_offset)
    end_seg_mid = seg_midpoint(
        raw[end_index].with_bulge(slice_data.updated_end_bulge),
        PlineVertex(slice_data.end_point.x, slice_data.end_point.y, 0.0),
    )
    if not point_ok(end_seg_mid):
        return False

    for v1, v2 in slice_data.iter_segments(raw):
        if not point_ok(v1.pos):
            return False
        if _intersects_original(original, v1, v2, pos_eps):
            return False
    return point_ok(slice_data.end_point)


# ---------------------------------------------------------------------------
# Step 2: slicing
# ---------------------------------------------------------------------------


def _build_intersect_lookup(raw: Pline, entries: list[tuple[int, Vector2]]) -> dict[int, list[Vector2]]:
    lookup: dict[int, list[Vector2]] = {}
    for idx, pt in entries:
        lookup.setdefault(idx, []).append(pt)
    for i, lst in lookup.items():
        start = raw[i].pos
        lst.sort(key=lambda p: dist_squared(p, start))
    return lookup


def slices_from_raw_offset(original: Pline, raw: Pline, offset: float, opts: OffsetOptions) -> list[PlineViewData]:
    """Slice a *closed* raw offset polyline at its self-intersections (single-offset path)."""
    result: list[PlineViewData] = []
    if len(raw) < 2:
        return result
    pos_eps = opts.pos_equal_eps

    self_intrs = all_self_intersects(raw, False, pos_eps)
    if not self_intrs:
        if not point_valid_for_offset(original, offset, raw[0].pos, pos_eps, opts.offset_dist_eps):
            return result
        result.append(PlineViewData.from_entire_pline(raw))
        return result

    entries: list[tuple[int, Vector2]] = []
    for si in self_intrs:
        entries.append((si.start_index1, si.point))
        entries.append((si.start_index2, si.point))
    lookup = _build_intersect_lookup(raw, entries)
    sorted_keys = sorted(lookup)

    def next_list(start_index: int) -> tuple[int, list[Vector2]]:
        nxt = raw.next_wrapping_index(start_index)
        for k in sorted_keys:
            if k >= nxt:
                return k, lookup[k]
        return sorted_keys[0], lookup[sorted_keys[0]]

    for start_index in sorted_keys:
        intr_list = lookup[start_index]
        for a in range(len(intr_list) - 1):
            s = PlineViewData.from_slice_points(raw, intr_list[a], start_index, intr_list[a + 1], start_index, pos_eps)
            if s is not None and _slice_is_valid(s, raw, original, offset, opts):
                result.append(s)

        found_index, next_intr = next_list(start_index)
        s = PlineViewData.from_slice_points(raw, intr_list[-1], start_index, next_intr[0], found_index, pos_eps)
        if s is not None and _slice_is_valid(s, raw, original, offset, opts):
            result.append(s)

    return result


def _visit_circle_intersects(
    pline: Pline, center: Vector2, radius: float, pos_eps: float, out: list[tuple[int, Vector2]]
) -> None:
    """Intersects of ``pline`` with a circle — used at open-polyline end caps."""

    def valid_line(t: float) -> bool:
        return not _is_false_intersect(t) and abs(t) > pos_eps

    def valid_arc(arc_center: Vector2, start: Vector2, end: Vector2, bulge: float, intr: Vector2) -> bool:
        return not start.fuzzy_eq_eps(intr, pos_eps) and point_within_arc_sweep(
            arc_center, start, end, bulge < 0.0, intr, pos_eps
        )

    for start_index, (v1, v2) in enumerate(pline.iter_segments()):
        if v1.bulge_is_zero():
            res = line_circle_intr(v1.pos, v2.pos, radius, center, pos_eps)
            if res.kind == "tangent":
                if valid_line(res.t0):
                    out.append((start_index, point_from_parametric(v1.pos, v2.pos, res.t0)))
            elif res.kind == "two":
                if valid_line(res.t0):
                    out.append((start_index, point_from_parametric(v1.pos, v2.pos, res.t0)))
                if valid_line(res.t1):
                    out.append((start_index, point_from_parametric(v1.pos, v2.pos, res.t1)))
        else:
            arc_radius, arc_center = seg_arc_radius_and_center(v1, v2)
            res = circle_circle_intr(arc_radius, arc_center, radius, center, pos_eps)
            if res.kind == "tangent":
                if valid_arc(arc_center, v1.pos, v2.pos, v1.bulge, res.point1):
                    out.append((start_index, res.point1))
            elif res.kind == "two":
                if valid_arc(arc_center, v1.pos, v2.pos, v1.bulge, res.point1):
                    out.append((start_index, res.point1))
                if valid_arc(arc_center, v1.pos, v2.pos, v1.bulge, res.point2):
                    out.append((start_index, res.point2))


def slices_from_dual_raw_offsets(
    original: Pline, raw: Pline, dual: Pline, offset: float, opts: OffsetOptions
) -> list[PlineViewData]:
    """Slice using dual-offset clipping — for open or self-intersecting inputs."""
    result: list[PlineViewData] = []
    if len(raw) < 2:
        return result
    pos_eps = opts.pos_equal_eps

    self_intrs = all_self_intersects(raw, False, pos_eps)
    dual_intrs = find_intersects(raw, dual, pos_eps)

    entries: list[tuple[int, Vector2]] = []
    if not original.is_closed:
        circle_radius = abs(offset)
        _visit_circle_intersects(raw, original[0].pos, circle_radius, pos_eps, entries)
        _visit_circle_intersects(raw, original.last().pos, circle_radius, pos_eps, entries)
    for si in self_intrs:
        entries.append((si.start_index1, si.point))
        entries.append((si.start_index2, si.point))
    for di in dual_intrs.basic:
        entries.append((di.start_index1, di.point))

    if not entries:
        if not point_valid_for_offset(original, offset, raw[0].pos, pos_eps, opts.offset_dist_eps):
            return result
        result.append(PlineViewData.from_entire_pline(raw))
        return result

    lookup = _build_intersect_lookup(raw, entries)
    sorted_keys = sorted(lookup)

    if not original.is_closed:
        # First slice: raw start up to the first intersect (no wrap-around to capture it).
        first_idx = sorted_keys[0]
        s = PlineViewData.from_slice_points(raw, raw[0].pos, 0, lookup[first_idx][0], first_idx, pos_eps)
        if s is not None and _slice_is_valid(s, raw, original, offset, opts):
            result.append(s)

    for start_index in sorted_keys:
        intr_list = lookup[start_index]
        for a in range(len(intr_list) - 1):
            s = PlineViewData.from_slice_points(raw, intr_list[a], start_index, intr_list[a + 1], start_index, pos_eps)
            if s is not None and _slice_is_valid(s, raw, original, offset, opts):
                result.append(s)

        nxt = raw.next_wrapping_index(start_index)
        found = None
        for k in sorted_keys:
            if k >= nxt:
                found = k
                break
        if found is None:
            if original.is_closed:
                found = sorted_keys[0]
            else:
                # Open polyline, no further intersect: final slice to the raw end.
                s = PlineViewData.from_slice_points(
                    raw, intr_list[-1], start_index, raw.last().pos, len(raw) - 1, pos_eps
                )
                if s is not None and _slice_is_valid(s, raw, original, offset, opts):
                    result.append(s)
                return result

        s = PlineViewData.from_slice_points(raw, intr_list[-1], start_index, lookup[found][0], found, pos_eps)
        if s is not None and _slice_is_valid(s, raw, original, offset, opts):
            result.append(s)

    return result


# ---------------------------------------------------------------------------
# Step 4: stitch surviving slices back into whole polylines
# ---------------------------------------------------------------------------


def _materialize(slice_data: PlineViewData, raw: Pline, join_eps: float, into: Pline | None = None) -> Pline:
    out = into if into is not None else Pline(is_closed=False)
    for v in slice_data.vertices(raw):
        out.add_or_replace_vertex(v, join_eps)
    return out


def stitch_slices_together(
    raw: Pline, slices: list[PlineViewData], is_closed: bool, orig_max_index: int, opts: OffsetOptions
) -> list[Pline]:
    """Join slices whose endpoints connect into maximal polylines, re-closing if needed."""
    result: list[Pline] = []
    if not slices:
        return result
    join_eps = opts.slice_join_eps
    pos_eps = opts.pos_equal_eps

    if len(slices) == 1:
        pline = _materialize(slices[0], raw, join_eps)
        if is_closed and len(pline) > 1 and pline[0].pos.fuzzy_eq_eps(pline.last().pos, join_eps):
            pline.is_closed = True
            pline.remove_last()
        result.append(pline)
        return result

    start_points = [s.updated_start.pos for s in slices]
    visited = [False] * len(slices)

    def index_dist(current_start: int, i: int) -> int:
        s = slices[i].start_index
        if current_start <= s:
            return s - current_start
        return orig_max_index - current_start + s

    for i in range(len(slices)):
        if visited[i]:
            continue
        visited[i] = True
        current = Pline(is_closed=False)
        current_index = i
        initial_start = slices[i].updated_start.pos
        loop_count = 0
        while True:
            loop_count += 1
            if loop_count > len(slices) + 1:
                break  # safety, matches the crate's max-loop guard
            cur = slices[current_index]
            _materialize(cur, raw, join_eps, into=current)
            current_loop_start = cur.start_index
            current_end = cur.end_point

            candidates = [
                k for k in range(len(slices)) if not visited[k] and start_points[k].fuzzy_eq_eps(current_end, join_eps)
            ]
            candidates.sort(
                key=lambda k: (
                    index_dist(current_loop_start, k),
                    slices[k].end_point.fuzzy_eq_eps(initial_start, pos_eps),
                )
            )

            if not candidates:
                if len(current) > 1:
                    if is_closed and current[0].pos.fuzzy_eq_eps(current.last().pos, join_eps):
                        current.remove_last()
                        current.is_closed = True
                    result.append(current)
                break

            visited[candidates[0]] = True
            current.remove_last()
            current_index = candidates[0]

    return result


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def parallel_offset(pline: Pline, offset: float, options: OffsetOptions | None = None) -> list[Pline]:
    """
    Offset ``pline`` by ``offset`` (positive/negative selects the side), returning the
    resulting polylines — possibly several, or none if the offset collapses the shape.

    This is the arc-native offset: rounded joins come back as exact arcs, so feeding
    the result back in for nested/concentric offsets does not accumulate error.
    """
    opts = options or OffsetOptions()
    if len(pline) < 2:
        return []

    cleaned = pline.remove_repeat_pos(opts.pos_equal_eps)
    source = cleaned if cleaned is not None else pline
    if len(source) < 2:
        return []

    raw = create_raw_offset_polyline(source, offset, opts.pos_equal_eps)
    if len(raw) == 0:
        return []

    if source.is_closed and not opts.handle_self_intersects:
        slices = slices_from_raw_offset(source, raw, offset, opts)
        return stitch_slices_together(raw, slices, True, len(raw) - 1, opts)

    dual = create_raw_offset_polyline(source, -offset, opts.pos_equal_eps)
    slices = slices_from_dual_raw_offsets(source, raw, dual, offset, opts)
    return stitch_slices_together(raw, slices, source.is_closed, len(raw), opts)
