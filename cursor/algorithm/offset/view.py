"""
Slice views over a polyline, ported from ``polyline::pline_view``.

The offset engine slices the raw offset polyline at its self-intersections and
keeps the pieces that survive the distance test. A *slice* is not copied out — it
is described by a :class:`PlineViewData`: which segment it starts on, how many
segments it spans, and the trimmed start/end vertices. :meth:`PlineViewData.vertices`
materializes it against the source polyline only when needed (for the distance
tests and, finally, for stitching).

``inverted_direction`` is carried faithfully but the offset engine never sets it;
it exists for the boolean operations that are out of scope for this milestone.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from .geom import Vector2, dist_squared
from .pline import Pline, PlineVertex
from .segment import seg_split_at_point


@dataclass(slots=True)
class PlineViewData:
    start_index: int
    end_index_offset: int
    updated_start: PlineVertex
    updated_end_bulge: float
    end_point: Vector2
    inverted_direction: bool = False

    def vertex_count(self) -> int:
        return self.end_index_offset + 2

    def get_vertex(self, source: Pline, index: int) -> PlineVertex:
        """The ``index``-th vertex of the slice, reconstructed from ``source``."""
        n = self.vertex_count()
        if not (0 <= index < n):
            raise IndexError(index)

        if self.inverted_direction:
            if index == 0:
                return PlineVertex(self.end_point.x, self.end_point.y, -self.updated_end_bulge)
            if index < self.end_index_offset:
                bulge_i = source.fwd_wrapping_index(self.start_index, self.end_index_offset - index)
                i = source.next_wrapping_index(bulge_i)
                return source[i].with_bulge(-source[bulge_i].bulge)
            if index == self.end_index_offset:
                i = source.fwd_wrapping_index(self.start_index, self.end_index_offset - index + 1)
                return source[i].with_bulge(-self.updated_start.bulge)
            return self.updated_start.with_bulge(0.0)

        if index == 0:
            return self.updated_start
        if index < self.end_index_offset:
            return source[source.fwd_wrapping_index(self.start_index, index)]
        if index == self.end_index_offset:
            i = source.fwd_wrapping_index(self.start_index, self.end_index_offset)
            return source[i].with_bulge(self.updated_end_bulge)
        return PlineVertex(self.end_point.x, self.end_point.y, 0.0)

    def vertices(self, source: Pline) -> list[PlineVertex]:
        return [self.get_vertex(source, i) for i in range(self.vertex_count())]

    def iter_segments(self, source: Pline) -> Iterator[tuple[PlineVertex, PlineVertex]]:
        verts = self.vertices(source)
        for i in range(len(verts) - 1):
            yield verts[i], verts[i + 1]

    def to_pline(self, source: Pline) -> Pline:
        """Materialize the slice as a standalone open polyline."""
        return Pline.from_vertices([(v.x, v.y, v.bulge) for v in self.vertices(source)], is_closed=False)

    # --- constructors -----------------------------------------------------

    @classmethod
    def from_entire_pline(cls, source: Pline) -> PlineViewData:
        vc = len(source)
        if source.is_closed:
            return cls(0, vc - 1, source[0], source.last().bulge, source[0].pos, False)
        return cls(0, vc - 2, source[0], source[vc - 2].bulge, source[vc - 1].pos, False)

    @classmethod
    def create_on_single_segment(
        cls, source: Pline, start_index: int, updated_start: PlineVertex, end_intersect: Vector2, pos_eps: float
    ) -> PlineViewData | None:
        if updated_start.pos.fuzzy_eq_eps(end_intersect, pos_eps):
            return None
        return cls(start_index, 0, updated_start, updated_start.bulge, end_intersect, False)

    @classmethod
    def create(
        cls,
        source: Pline,
        start_index: int,
        end_intersect: Vector2,
        intersect_index: int,
        updated_start: PlineVertex,
        traverse_count: int,
        pos_eps: float,
    ) -> PlineViewData:
        assert traverse_count != 0
        current = source[intersect_index]
        if end_intersect.fuzzy_eq_eps(current.pos, pos_eps):
            offset = traverse_count - 1
            if offset != 0:
                updated_end_bulge = source[source.prev_wrapping_index(intersect_index)].bulge
            else:
                updated_end_bulge = updated_start.bulge
        else:
            nxt = source.next_wrapping_index(intersect_index)
            split = seg_split_at_point(current, source[nxt], end_intersect, pos_eps)
            offset = traverse_count
            updated_end_bulge = split.updated_start.bulge
        return cls(start_index, offset, updated_start, updated_end_bulge, end_intersect, False)

    @classmethod
    def from_slice_points(
        cls,
        source: Pline,
        start_point: Vector2,
        start_index: int,
        end_point: Vector2,
        end_index: int,
        pos_eps: float,
    ) -> PlineViewData | None:
        """The slice of ``source`` running from ``start_point`` to ``end_point``."""
        # Catch start_point sitting exactly on the end of its segment.
        if not source.is_closed and start_index >= end_index:
            start_at_seg_end = False
        else:
            nxt = source.next_wrapping_index(start_index)
            if source[nxt].pos.fuzzy_eq_eps(start_point, pos_eps):
                start_index, start_at_seg_end = nxt, True
            else:
                start_at_seg_end = False

        index_dist = source.fwd_wrapping_dist(start_index, end_index)
        if index_dist == 0 and source.is_closed and not start_point.fuzzy_eq_eps(end_point, pos_eps):
            seg_start = source[start_index].pos
            if dist_squared(seg_start, start_point) < dist_squared(seg_start, end_point):
                traverse_count = 0
            else:
                traverse_count = len(source)
        else:
            traverse_count = index_dist

        start_v1 = source[start_index]
        start_v2 = source[source.next_wrapping_index(start_index)]
        if start_at_seg_end:
            if traverse_count == 0:
                updated_start = seg_split_at_point(start_v1, start_v2, end_point, pos_eps).updated_start
            else:
                updated_start = start_v1
        else:
            start_split = seg_split_at_point(start_v1, start_v2, start_point, pos_eps)
            updated_for_start = start_split.split_vertex
            if traverse_count == 0:
                updated_start = seg_split_at_point(updated_for_start, start_v2, end_point, pos_eps).updated_start
            else:
                updated_start = updated_for_start

        if traverse_count == 0:
            return cls.create_on_single_segment(source, start_index, updated_start, end_point, pos_eps)
        if (
            traverse_count == 1
            and end_point.fuzzy_eq_eps(source[end_index].pos, pos_eps)
            and updated_start.pos.fuzzy_eq_eps(end_point, pos_eps)
        ):
            return None
        return cls.create(source, start_index, end_point, end_index, updated_start, traverse_count, pos_eps)
