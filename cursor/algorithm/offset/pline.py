"""
Arc-native polyline types: ``PlineVertex`` and ``Pline``.

Ported from cavalier_contours. A polyline here is a sequence of vertices, each an
``(x, y, bulge)`` triple. The twist that makes the whole library work is *bulge*:
it is ``tan(sweep_angle / 4)`` for the segment that **starts** at that vertex, so

  * ``bulge == 0``  -> the segment to the next vertex is a straight line
  * ``bulge > 0``   -> a counter-clockwise arc
  * ``bulge < 0``   -> a clockwise arc

with ``|bulge|`` growing from 0 (flat) to 1 (a half circle). A single
representation thus carries lines and arcs together, and — crucially for
offsetting — the offset of an arc is another arc, so rounded joins stay *exact*
instead of decaying into chords. That is the property a straight-segment offset
throws away and this one keeps.

The last vertex of a closed polyline has an implicit final segment back to the
first vertex, governed by the last vertex's own bulge.

numpy backing
-------------
A ``Pline`` stores its vertices in one contiguous ``(N, 3)`` float64 array. The
per-segment arc math upstairs is scalar (see :mod:`cursor.algorithm.offset.segment`)
and pulls individual vertices out as :class:`~cursor.algorithm.offset.geom.Vector2`,
but the array lets the genuinely data-parallel passes — bounding boxes for every
segment, distance from many probe points to the whole polyline — run as vectorized
numpy, which is where the time actually goes on a dense recording.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator

import numpy as np

from .geom import FUZZY_EPS, Vector2


@dataclass(frozen=True, slots=True)
class PlineVertex:
    """One ``(x, y, bulge)`` vertex. ``bulge`` describes the segment starting here."""

    x: float
    y: float
    bulge: float

    @property
    def pos(self) -> Vector2:
        return Vector2(self.x, self.y)

    def with_bulge(self, bulge: float) -> PlineVertex:
        return PlineVertex(self.x, self.y, bulge)

    def bulge_is_zero(self, eps: float = FUZZY_EPS) -> bool:
        return abs(self.bulge) < eps

    def bulge_is_pos(self) -> bool:
        return self.bulge > 0.0

    def bulge_is_neg(self) -> bool:
        return self.bulge < 0.0

    def fuzzy_eq_eps(self, other: PlineVertex, eps: float) -> bool:
        return abs(self.x - other.x) < eps and abs(self.y - other.y) < eps and abs(self.bulge - other.bulge) < eps


class Pline:
    """
    A polyline of ``(x, y, bulge)`` vertices, open or closed.

    Vertices live in a growable ``(N, 3)`` float64 array. Index and iterate to get
    :class:`PlineVertex` views; use :meth:`vertex_data` for the raw array when a
    vectorized pass wants it.
    """

    __slots__ = ("_data", "_len", "is_closed")

    def __init__(self, is_closed: bool = False, capacity: int = 8):
        self._data = np.empty((max(capacity, 1), 3), dtype=np.float64)
        self._len = 0
        self.is_closed = is_closed

    # --- construction -----------------------------------------------------

    @classmethod
    def from_vertices(cls, vertices: Iterable[Iterable[float]], is_closed: bool = False) -> Pline:
        """Build from an iterable of ``(x, y, bulge)`` (or ``(x, y)``, bulge defaulting to 0)."""
        rows = []
        for v in vertices:
            v = tuple(v)
            if len(v) == 2:
                rows.append((v[0], v[1], 0.0))
            elif len(v) == 3:
                rows.append((v[0], v[1], v[2]))
            else:
                raise ValueError(f"vertex must be (x, y) or (x, y, bulge), got {v!r}")
        pl = cls(is_closed=is_closed, capacity=len(rows) or 1)
        if rows:
            pl._data[: len(rows)] = rows
            pl._len = len(rows)
        return pl

    @classmethod
    def _from_array(cls, data: np.ndarray, is_closed: bool) -> Pline:
        """Wrap an existing ``(N, 3)`` array without copying its rows one by one."""
        pl = cls(is_closed=is_closed, capacity=max(len(data), 1))
        n = len(data)
        pl._data[:n] = data
        pl._len = n
        return pl

    # --- sequence protocol ------------------------------------------------

    def __len__(self) -> int:
        return self._len

    def __getitem__(self, i: int) -> PlineVertex:
        if i < 0:
            i += self._len
        if not (0 <= i < self._len):
            raise IndexError(i)
        x, y, b = self._data[i]
        return PlineVertex(float(x), float(y), float(b))

    def __iter__(self) -> Iterator[PlineVertex]:
        for i in range(self._len):
            x, y, b = self._data[i]
            yield PlineVertex(float(x), float(y), float(b))

    def __repr__(self) -> str:
        state = "closed" if self.is_closed else "open"
        return f"Pline({self._len} verts, {state})"

    # --- mutation ---------------------------------------------------------

    def add(self, x: float, y: float, bulge: float = 0.0) -> None:
        if self._len == len(self._data):
            self._data = np.resize(self._data, (max(len(self._data) * 2, 1), 3))
        self._data[self._len] = (x, y, bulge)
        self._len += 1

    def add_vertex(self, v: PlineVertex) -> None:
        self.add(v.x, v.y, v.bulge)

    def set_bulge(self, i: int, bulge: float) -> None:
        if i < 0:
            i += self._len
        self._data[i, 2] = bulge

    def set_vertex(self, i: int, v: PlineVertex) -> None:
        if i < 0:
            i += self._len
        self._data[i] = (v.x, v.y, v.bulge)

    def set(self, i: int, x: float, y: float, bulge: float) -> None:
        if i < 0:
            i += self._len
        self._data[i] = (x, y, bulge)

    def set_last(self, v: PlineVertex) -> None:
        self._data[self._len - 1] = (v.x, v.y, v.bulge)

    def remove_last(self) -> None:
        self._len -= 1

    def remove(self, i: int) -> None:
        if i < 0:
            i += self._len
        self._data[i : self._len - 1] = self._data[i + 1 : self._len]
        self._len -= 1

    def clear(self) -> None:
        self._len = 0

    def add_or_replace_vertex(self, v: PlineVertex, pos_eps: float) -> None:
        """
        Append ``v``, unless its position coincides with the current last vertex — then
        just adopt ``v``'s bulge on that last vertex. This keeps the joined raw offset
        curve free of zero-length segments.
        """
        if self._len == 0:
            self.add_vertex(v)
            return
        lx, ly = self._data[self._len - 1, 0], self._data[self._len - 1, 1]
        if abs(lx - v.x) < pos_eps and abs(ly - v.y) < pos_eps:
            self._data[self._len - 1, 2] = v.bulge
            return
        self.add_vertex(v)

    def add_or_replace(self, x: float, y: float, bulge: float, pos_eps: float) -> None:
        self.add_or_replace_vertex(PlineVertex(x, y, bulge), pos_eps)

    # --- wrapping index math (polyline treated as circular) ---------------

    def next_wrapping_index(self, i: int) -> int:
        nxt = i + 1
        return 0 if nxt >= self._len else nxt

    def prev_wrapping_index(self, i: int) -> int:
        return self._len - 1 if i == 0 else i - 1

    def fwd_wrapping_dist(self, start_index: int, end_index: int) -> int:
        if start_index <= end_index:
            return end_index - start_index
        return self._len - start_index + end_index

    def fwd_wrapping_index(self, start_index: int, offset: int) -> int:
        s = start_index + offset
        return s if s < self._len else s - self._len

    def remove_repeat_pos(self, pos_eps: float) -> Pline | None:
        """
        A copy with consecutive coincident vertices merged (keeping the later bulge),
        or ``None`` if there were none — matching the crate, which avoids the copy in
        the common case. The offset engine calls this to sanitize its input.
        """
        if self._len < 2:
            return None

        changed = False
        result: list[list[float]] = [list(self._data[0])]
        prev_x, prev_y = result[0][0], result[0][1]
        for i in range(1, self._len):
            x, y, b = self._data[i]
            if abs(x - prev_x) < pos_eps and abs(y - prev_y) < pos_eps:
                # Repeat position: drop this vertex but carry its bulge to the one kept.
                result[-1][2] = b
                changed = True
            else:
                result.append([x, y, b])
                prev_x, prev_y = x, y

        # Closed polyline whose last vertex sits on the first: drop the last.
        if self.is_closed:
            lx, ly = self._data[self._len - 1, 0], self._data[self._len - 1, 1]
            if abs(lx - self._data[0, 0]) < pos_eps and abs(ly - self._data[0, 1]) < pos_eps:
                result.pop()
                changed = True

        if not changed:
            return None

        out = Pline(is_closed=self.is_closed, capacity=len(result) or 1)
        for x, y, b in result:
            out.add(x, y, b)
        return out

    # --- access -----------------------------------------------------------

    def last(self) -> PlineVertex:
        return self[self._len - 1]

    def vertex_data(self) -> np.ndarray:
        """A read-only ``(N, 3)`` view of the vertices — for vectorized passes."""
        view = self._data[: self._len]
        view.flags.writeable = False
        return view

    def iter_segments(self) -> Iterator[tuple[PlineVertex, PlineVertex]]:
        """
        Yield each segment as a ``(v1, v2)`` pair.

        A closed polyline yields the wrap-around segment from the last vertex back
        to the first; an open one stops at the final vertex.
        """
        n = self._len
        if n < 2:
            return
        for i in range(n - 1):
            yield self[i], self[i + 1]
        if self.is_closed:
            yield self[n - 1], self[0]

    def segment_count(self) -> int:
        if self._len < 2:
            return 0
        return self._len if self.is_closed else self._len - 1

    def copy(self) -> Pline:
        return Pline._from_array(self.vertex_data(), self.is_closed)
