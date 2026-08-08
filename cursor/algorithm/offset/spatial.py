"""
A uniform-grid spatial index over polyline segments.

The offset engine asks the same shape of question over and over: "which segments of
this polyline are near this point / this box?" — in the distance-validity test, in
the intersection scans, and in the self-intersection search. Answered by scanning
every segment, those are the quadratic hot spots (the offset of a several-hundred
segment line spends almost all its time there).

This index answers them in roughly constant time per query by bucketing each
segment's bounding box into the grid cells it covers; a query returns the segments in
the cells its box touches. The result is always a *superset* of the truly-overlapping
segments — never fewer — so callers keep their exact per-segment test and get bit-for-bit
the same answer as the brute-force scan, only faster.

This is the pragmatic stand-in for the crate's packed Hilbert R-tree. A grid is
simpler and dependency-free, and it suits the roughly-uniform segment sizes of plotter
geometry; segments whose box is unusually large (spanning many cells) are held in a
small overflow list that every query checks, which keeps it robust rather than
pathological when a stray long segment appears.
"""

from __future__ import annotations

import math

import numpy as np

from .pline import Pline, PlineVertex
from .segment import segment_bboxes

# A segment whose bounding box would occupy more than this many cells is kept in the
# always-checked overflow list instead of being bucketed (guards against one huge
# segment filling the grid).
_CELL_SPAN_CAP = 32


class SpatialGrid:
    """Buckets ``(N, 4)`` bounding boxes into a uniform grid for box/point queries."""

    def __init__(self, boxes: np.ndarray):
        self.boxes = boxes
        self.n = len(boxes)
        self.buckets: dict[tuple[int, int], list[int]] = {}
        self.overflow: list[int] = []

        if self.n == 0:
            self.cell = 1.0
            return

        # Cell ~ a typical segment's extent (median resists the odd long segment), so a
        # normal box lands in a handful of cells.
        widths = boxes[:, 2] - boxes[:, 0]
        heights = boxes[:, 3] - boxes[:, 1]
        self.cell = max(float(np.median(np.maximum(widths, heights))), 1e-9)

        c = self.cell
        ix0 = np.floor(boxes[:, 0] / c).astype(np.int64)
        iy0 = np.floor(boxes[:, 1] / c).astype(np.int64)
        ix1 = np.floor(boxes[:, 2] / c).astype(np.int64)
        iy1 = np.floor(boxes[:, 3] / c).astype(np.int64)
        span = (ix1 - ix0 + 1) * (iy1 - iy0 + 1)

        for i in range(self.n):
            if span[i] > _CELL_SPAN_CAP:
                self.overflow.append(i)
                continue
            for gx in range(int(ix0[i]), int(ix1[i]) + 1):
                for gy in range(int(iy0[i]), int(iy1[i]) + 1):
                    self.buckets.setdefault((gx, gy), []).append(i)

    def query(self, min_x: float, min_y: float, max_x: float, max_y: float) -> set[int]:
        """Indices of every segment whose bucket the query box touches (a superset)."""
        if self.n == 0:
            return set()
        c = self.cell
        gx0, gy0 = int(math.floor(min_x / c)), int(math.floor(min_y / c))
        gx1, gy1 = int(math.floor(max_x / c)), int(math.floor(max_y / c))

        # If the query box itself spans an enormous number of cells, scanning them all
        # would cost more than a brute pass — just return everything (still correct).
        if (gx1 - gx0 + 1) * (gy1 - gy0 + 1) > 4 * self.n + 16:
            return set(range(self.n))

        hits: set[int] = set(self.overflow)
        for gx in range(gx0, gx1 + 1):
            for gy in range(gy0, gy1 + 1):
                bucket = self.buckets.get((gx, gy))
                if bucket:
                    hits.update(bucket)
        return hits

    def query_point(self, x: float, y: float, radius: float) -> set[int]:
        return self.query(x - radius, y - radius, x + radius, y + radius)


class PlineSegmentIndex:
    """
    A :class:`SpatialGrid` over a polyline's segments, paired with the segments
    themselves so callers can go straight from a query to the ``(v1, v2)`` pair.

    Segment ``i`` here is the ``i``-th segment of ``pline.iter_segments()`` — the same
    order everything else in the engine uses — so an index returned by a query indexes
    both :attr:`segments` and the source polyline's segment ``i``.
    """

    def __init__(self, pline: Pline):
        self.pline = pline
        self.segments: list[tuple[PlineVertex, PlineVertex]] = list(pline.iter_segments())
        self.grid = SpatialGrid(segment_bboxes(pline))

    def query(self, min_x: float, min_y: float, max_x: float, max_y: float) -> set[int]:
        return self.grid.query(min_x, min_y, max_x, max_y)

    def query_point(self, x: float, y: float, radius: float) -> set[int]:
        return self.grid.query_point(x, y, radius)
