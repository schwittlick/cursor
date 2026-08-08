"""
Arc-native 2D polyline parallel offsetting.

A from-scratch Python port of the core offset algorithm of the Rust crate
`cavalier_contours <https://github.com/jbuckmccready/cavalier_contours>`_
(dual Apache-2.0 / MIT). Polylines carry per-segment *bulge* values, so lines and
circular arcs share one representation and offset joins stay exact — feed an offset
back in for nested/concentric contours and no chord error accumulates.

Quick start::

    from cursor.algorithm.offset import Pline, parallel_offset

    square = Pline.from_vertices([(0, 0), (10, 0), (10, 10), (0, 10)], is_closed=True)
    inner = parallel_offset(square, 2.0)   # -> list[Pline]

To move between this and the rest of the cursor library (which plots point-based
:class:`cursor.path.Path` objects), use :mod:`cursor.algorithm.offset.adapter`,
which tessellates arcs to points on the way out and reads plain paths on the way in.

See the module docstrings for the algorithm; ``cursor/tests/algorithm/`` checks it
against test vectors ported from the Rust crate.
"""

from .offset import OffsetOptions, parallel_offset
from .pline import Pline, PlineVertex

__all__ = ["Pline", "PlineVertex", "parallel_offset", "OffsetOptions"]
