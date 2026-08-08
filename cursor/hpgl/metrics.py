"""
The geometry of HP-GL text, shared by everything that emits, tracks or parses labels.

HP-GL sizes characters with SI (width and height in cm) and builds a cell around each
glyph: the cell is 1.5x as wide and 2.0x as tall as the character itself. ES then adds
extra space as a fraction of that cell, so a negative ES tightens the setting. Getting
this wrong is silent -- the plot simply comes out spaced differently than the preview --
so all three of the writer, the parser and the layout read it from here.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

CHAR_CELL_WIDTH_FACTOR = 1.5
CHAR_CELL_HEIGHT_FACTOR = 2.0

# plotters have a limited label buffer, longer LB payloads get truncated or dropped
MAX_LABEL_LENGTH = 150

# what SI without parameters gives you on a HP 7550A loaded with A3
DEFAULT_CHAR_SIZE_CM = (0.285, 0.375)
DEFAULT_CHAR_ASPECT = DEFAULT_CHAR_SIZE_CM[0] / DEFAULT_CHAR_SIZE_CM[1]
DEFAULT_PLOTTER_UNIT = 40  # plotter units per mm

# LO, the label origin: where the label sits relative to the point it is drawn at.
# 1..9 run left/centre/right by bottom/centre/top, 11..19 repeat those with a half
# character of clearance. 10 is not a valid origin.
LABEL_ORIGINS = tuple(origin for origin in range(1, 20) if origin != 10)
DEFAULT_LABEL_ORIGIN = 1


def rotate(origin: tuple[float, float], point: tuple[float, float], angle: float) -> tuple[float, float]:
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


@dataclass(frozen=True)
class FontMetrics:
    """
    The geometry of a HP-GL text state (SI + ES), expressed in plotter units.

    Everything a layout needs follows from those two commands.
    """

    char_width_cm: float
    char_height_cm: float
    extra_space: float = 0.0
    extra_line: float = 0.0
    plotter_unit: int = DEFAULT_PLOTTER_UNIT

    @classmethod
    def default(cls, plotter_unit: int = DEFAULT_PLOTTER_UNIT) -> FontMetrics:
        return cls(*DEFAULT_CHAR_SIZE_CM, plotter_unit=plotter_unit)

    @property
    def char_width(self) -> float:
        return self.char_width_cm * 10 * self.plotter_unit

    @property
    def char_height(self) -> float:
        return self.char_height_cm * 10 * self.plotter_unit

    @property
    def advance_x(self) -> float:
        """How far the pen moves right per character."""
        return self.char_width * CHAR_CELL_WIDTH_FACTOR * (1.0 + self.extra_space)

    @property
    def line_height(self) -> float:
        """How far the pen moves down per line."""
        return self.char_height * CHAR_CELL_HEIGHT_FACTOR * (1.0 + self.extra_line)

    def text_width(self, text: str) -> float:
        return len(text) * self.advance_x

    def max_chars(self, width: float) -> int:
        if self.advance_x <= 0:
            return 0
        return int(width / self.advance_x)

    def scaled(self, factor: float) -> FontMetrics:
        return FontMetrics(
            self.char_width_cm * factor,
            self.char_height_cm * factor,
            self.extra_space,
            self.extra_line,
            self.plotter_unit,
        )


def label_origin_offset(origin: int, width: float, metrics: FontMetrics) -> tuple[float, float]:
    """
    Where a label of the given width starts, relative to the point LB was issued at.

    LB draws from the bottom left by default (LO1), so every other origin is a matter of
    shifting the label back by some part of its own extent. The result is in the text's
    own frame, before any DI rotation.

    Origins 11..19 add half a character of clearance, pushed in whichever direction the
    label already extends, so the text clears the point it labels. A centred axis has no
    such direction and takes no offset.
    """
    if origin not in LABEL_ORIGINS:
        raise ValueError(f"Label origin must be one of {LABEL_ORIGINS}, got {origin}")

    clearance = origin > 10
    anchor = origin - 10 if clearance else origin

    # 1,2,3 sit left of the point, 4,5,6 centre on it, 7,8,9 sit right of it
    horizontal = (anchor - 1) // 3
    # 1,4,7 sit above the point, 2,5,8 centre on it, 3,6,9 sit below it
    vertical = (anchor - 1) % 3

    dx = (0.0, -width / 2, -width)[horizontal]
    dy = (0.0, -metrics.char_height / 2, -metrics.char_height)[vertical]

    if clearance:
        dx += (metrics.char_width / 2, 0.0, -metrics.char_width / 2)[horizontal]
        dy += (metrics.char_height / 2, 0.0, -metrics.char_height / 2)[vertical]

    return dx, dy
