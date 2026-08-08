from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum, auto

from cursor.bb import BoundingBox
from cursor.hpgl.hpgl import HPGL

# the cell model these layouts are built on lives in metrics, so that the writer, the
# parser and this module all space text the same way
from cursor.hpgl.metrics import (  # noqa: F401  (re-exported for callers of this module)
    CHAR_CELL_HEIGHT_FACTOR,
    CHAR_CELL_WIDTH_FACTOR,
    DEFAULT_CHAR_ASPECT,
    DEFAULT_PLOTTER_UNIT,
    MAX_LABEL_LENGTH,
    FontMetrics,
)


class Align(Enum):
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()


class VAlign(Enum):
    TOP = auto()
    CENTER = auto()
    BOTTOM = auto()


@dataclass
class TextBlock:
    """A word-wrapped paragraph, ready to be emitted as a series of LB commands."""

    lines: list[str]
    metrics: FontMetrics

    @property
    def width(self) -> float:
        if not self.lines:
            return 0.0
        return max(self.metrics.text_width(line) for line in self.lines)

    @property
    def height(self) -> float:
        return len(self.lines) * self.metrics.line_height

    def fits(self, box: BoundingBox) -> bool:
        return self.width <= box.w and self.height <= box.h


def wrap(text: str, metrics: FontMetrics, width: float) -> list[str]:
    """
    Word-wrap text into lines no wider than width (in plotter units).

    Words longer than a full line are hard-broken. Existing newlines are kept as
    paragraph breaks.
    """
    max_chars = metrics.max_chars(width)
    if max_chars <= 0:
        return []

    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        current = ""
        for word in paragraph.split():
            while len(word) > max_chars:
                if current:
                    lines.append(current)
                    current = ""
                lines.append(word[:max_chars])
                word = word[max_chars:]

            candidate = f"{current} {word}" if current else word
            if len(candidate) > max_chars:
                lines.append(current)
                current = word
            else:
                current = candidate

        lines.append(current)

    return lines


def layout(text: str, metrics: FontMetrics, width: float) -> TextBlock:
    return TextBlock(wrap(text, metrics, width), metrics)


def fit(
    text: str,
    box: BoundingBox,
    char_aspect: float = DEFAULT_CHAR_ASPECT,
    extra_space: float = 0.0,
    extra_line: float = 0.0,
    plotter_unit: int = DEFAULT_PLOTTER_UNIT,
    rotation: int = 0,
    min_char_height_cm: float = 0.05,
    max_char_height_cm: float | None = None,
    iterations: int = 40,
) -> TextBlock:
    """
    Find the largest character size at which text still fits into box.

    The character aspect ratio (width/height) is kept constant, so the letterforms stay
    natural and only the scale changes. Bisects on character height: growing the type
    both enlarges every line and forces more of them, so "fits" is monotonic in size.
    """
    page = reading_box(box, rotation)

    if max_char_height_cm is None:
        # a single line of type can at most be as tall as the box
        max_char_height_cm = page.h / plotter_unit / 10 / CHAR_CELL_HEIGHT_FACTOR

    def block_at(char_height_cm: float) -> TextBlock:
        metrics = FontMetrics(char_height_cm * char_aspect, char_height_cm, extra_space, extra_line, plotter_unit)
        return layout(text, metrics, page.w)

    lo, hi = min_char_height_cm, max_char_height_cm
    best = block_at(lo)
    if not best.fits(page):
        logging.warning(f"Text does not fit into {page} even at the minimum size of {lo}cm")
        return best

    for _ in range(iterations):
        mid = (lo + hi) / 2
        candidate = block_at(mid)
        if candidate.fits(page):
            best, lo = candidate, mid
        else:
            hi = mid

    return best


QUARTER_TURNS = (0, 90, 180, 270)


def reading_size(box: BoundingBox, rotation: int = 0) -> tuple[float, float]:
    """
    The box as the reader sees it: (width along the baseline, height across the lines).

    A quarter turn swaps the two, which is how a portrait block is placed on a plotter
    whose own coordinate frame is landscape.
    """
    if rotation not in QUARTER_TURNS:
        raise ValueError(f"Rotation must be one of {QUARTER_TURNS}, got {rotation}")

    if rotation in (90, 270):
        return box.h, box.w
    return box.w, box.h


def reading_box(box: BoundingBox, rotation: int = 0) -> BoundingBox:
    """The box in reading orientation, anchored at the origin. Wrap text to its width."""
    width, height = reading_size(box, rotation)
    return BoundingBox(0, 0, width, height)


def _to_plotter(box: BoundingBox, rotation: int, lx: float, ly: float) -> tuple[float, float]:
    """
    Map a position in reading space onto the plotter.

    Reading space runs left to right along the baseline (lx) and top to bottom across the
    lines (ly), with its origin in the corner the reader sees as top left. Which plotter
    corner that is, and which axes the two directions follow, is what the rotation picks.
    """
    match rotation:
        case 0:
            return box.x + lx, box.y2 - ly
        case 90:
            return box.x + ly, box.y + lx
        case 180:
            return box.x2 - lx, box.y + ly
        case 270:
            return box.x2 - ly, box.y2 - lx

    raise ValueError(f"Rotation must be one of {QUARTER_TURNS}, got {rotation}")


def draw(
    hpgl: HPGL,
    block: TextBlock,
    box: BoundingBox,
    align: Align = Align.LEFT,
    valign: VAlign = VAlign.TOP,
    rotation: int = 0,
    emit_font: bool = True,
) -> None:
    """
    Emit a laid-out text block into an HPGL command stream.

    One PA + LB pair is written per line, which keeps the pen position under our control
    instead of the plotter's, sidesteps the label buffer limit, and stays parseable by
    HPGLParser. Lines are placed from the top of box downwards, in reading orientation.

    rotation turns the text within box by a quarter turn at a time (DI), so a block can
    be set portrait on a landscape plotter. The block must have been wrapped to the
    matching reading_box.
    """
    metrics = block.metrics
    width, height = reading_size(box, rotation)

    if emit_font:
        hpgl.SI(metrics.char_width_cm, metrics.char_height_cm)
        hpgl.ES(metrics.extra_space, metrics.extra_line)
        hpgl.DI(rotation)

    slack = height - block.height
    match valign:
        case VAlign.TOP:
            top = 0.0
        case VAlign.CENTER:
            top = slack / 2
        case VAlign.BOTTOM:
            top = slack

    for index, line in enumerate(block.lines):
        if not line:
            continue

        # LB draws from the bottom left of the character cell, so drop by one char height
        ly = top + index * metrics.line_height + metrics.char_height

        free = width - metrics.text_width(line)
        match align:
            case Align.LEFT:
                lx = 0.0
            case Align.CENTER:
                lx = free / 2
            case Align.RIGHT:
                lx = free

        for offset in range(0, len(line), MAX_LABEL_LENGTH):
            chunk = line[offset : offset + MAX_LABEL_LENGTH]
            x, y = _to_plotter(box, rotation, lx + offset * metrics.advance_x, ly)
            hpgl.PA(int(x), int(y))
            hpgl.LB(chunk)
