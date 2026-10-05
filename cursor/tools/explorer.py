"""Explore the recorded paths in the mouse_logger data fountain, interactively.

    PYTHONPATH=. .venv/bin/python -m cursor.tools.explorer [--fountain URL] [--limit N]

A PyQt5 window on top of cursor.load.fountain.Fountain. The left panel is the
query: every filter the fountain knows (source, machine, app, recording, time
range, point count, distance, duration, the entropies, aspect, variation, the
bounding box, colour) plus sort, seed, limit and paging. Each metric has a
histogram: grey is the whole population (a random sample), blue is the current
query; drag on it to set that range, double-click to clear it. The canvas shows
the matching paths in the screen frame (0..1 is the primary monitor) or as a
grid of tiles, coloured by time, app, recording or any metric. Hover a path for
its numbers in the status bar, click it for the detail panel, right-drag to set
the bounding box, wheel to zoom, left-drag to pan, double-click to fit.

The panel always shows the equivalent `QUERY = dict(...)` for a composition
(as in compositions/composition105/c105.py); "Copy Python" puts it on the
clipboard. "Save pickle" writes the shown paths as a Collection pickle.

Needs a running fountain (see ~/dev/mouse_logger: `mouse-logger fountain serve`).
"""

from __future__ import annotations

import argparse
import logging
import math
import pathlib
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal

from cursor.load.fountain import LABELS, Fountain, FountainError, Frame

log = logging.getLogger(__name__)


# ------------------------------------------------------------------ metrics
@dataclass(frozen=True)
class Metric:
    key: str
    label: str
    log: bool  # histogram axis and colour ramp in log space
    fmt: str


METRICS = (
    Metric("n_points", "points", True, "{:.0f}"),
    Metric("distance", "distance", True, "{:.3g}"),
    Metric("duration_s", "duration (s)", True, "{:.3g}"),
    Metric("entropy_x", "entropy x", False, "{:.2f}"),
    Metric("entropy_y", "entropy y", False, "{:.2f}"),
    Metric("entropy_dc", "entropy dc", False, "{:.2f}"),
    Metric("aspect", "aspect (h/w)", True, "{:.3g}"),
    Metric("variation_x", "variation x", True, "{:.3g}"),
    Metric("variation_y", "variation y", True, "{:.3g}"),
)
METRIC = {m.key: m for m in METRICS}
SORT_KEYS = ("random", "t0", "id", "entropy_cross") + tuple(m.key for m in METRICS)


def fmt_metric(key: str, v) -> str:
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "∞" if v is not None and v > 0 else ("-∞" if v is not None else "–")
    return METRIC[key].fmt.format(v) if key in METRIC else str(v)


def fmt_time(t_ns, with_date: bool = True) -> str:
    dt = datetime.fromtimestamp(int(t_ns) / 1e9).astimezone()
    return dt.strftime("%Y-%m-%d %H:%M" if with_date else "%H:%M")


# -------------------------------------------------------------------- query
@dataclass
class QueryState:
    """What the panel says, in one place; filters() speaks Fountain's keyword language."""

    ranges: dict[str, tuple[float | None, float | None]] = field(default_factory=dict)
    bbox: tuple[float, float, float, float] | None = None
    bbox_mode: str = "inside"
    since: str | None = None
    until: str | None = None
    source: list[str] = field(default_factory=list)
    machine: list[str] = field(default_factory=list)
    app: list[str] = field(default_factory=list)
    recording: list[str] = field(default_factory=list)
    has_color: bool | None = None
    sort: str | None = None
    order: str = "asc"
    seed: int | None = None
    limit: int = 500
    offset: int = 0
    resample: int | None = None

    def range(self, key: str) -> tuple[float | None, float | None]:
        return self.ranges.get(key, (None, None))

    def filters(self) -> dict:
        """Keywords for Fountain.paths() / frame(), apart from limit, offset and resample."""
        kw: dict = {}
        lo, hi = self.range("n_points")
        if lo is not None:
            kw["min_points"] = int(lo)
        if hi is not None:
            kw["max_points"] = int(hi)
        xlo, xhi = self.range("entropy_x")
        ylo, yhi = self.range("entropy_y")
        if xlo is not None or ylo is not None:
            kw["entropy_min"] = (xlo, ylo)
        if xhi is not None or yhi is not None:
            kw["entropy_max"] = (xhi, yhi)
        lo, hi = self.range("distance")
        if lo is not None:
            kw["distance_min"] = lo
        if hi is not None:
            kw["distance_max"] = hi
        for key, name in (
            ("entropy_dc", "entropy_dc"),
            ("aspect", "aspect"),
            ("variation_x", "variation_x"),
            ("variation_y", "variation_y"),
            ("duration_s", "duration"),
        ):
            lo, hi = self.range(key)
            if lo is not None and hi is not None:
                kw[name] = (lo, hi)
            elif lo is not None:
                kw[name] = lo
            elif hi is not None:
                kw[name] = (None, hi)
        if self.bbox is not None:
            kw["bbox"] = tuple(round(float(v), 4) for v in self.bbox)
            if self.bbox_mode == "intersects":
                kw["bbox_mode"] = "intersects"
        if self.since:
            kw["since"] = self.since
        if self.until:
            kw["until"] = self.until
        if len(self.source) == 1:
            kw["source"] = self.source[0]
        for name in ("machine", "app", "recording"):
            vals = getattr(self, name)
            if vals:
                kw[name] = vals[0] if len(vals) == 1 else list(vals)
        if self.has_color is not None:
            kw["has_color"] = self.has_color
        if self.sort:
            kw["sort"] = self.sort
            if self.sort == "random":
                if self.seed is not None:
                    kw["seed"] = self.seed
            elif self.order == "desc":
                kw["order"] = "desc"
        elif self.order == "desc":
            kw["order"] = "desc"
        return kw

    def kwargs(self) -> dict:
        """Everything Fountain.frame() needs for this query."""
        kw = dict(self.filters(), limit=self.limit)
        if self.offset:
            kw["offset"] = self.offset
        if self.resample:
            kw["resample"] = self.resample
        return kw

    def python(self, total: int | None = None) -> str:
        """The query as a composition would write it."""
        lines = ["QUERY = dict("]
        for k, v in self.filters().items():
            lines.append(f"    {k}={v!r},")
        lines.append(")")
        extra = "".join(f", {k}={v}" for k, v in (("offset", self.offset), ("resample", self.resample)) if v)
        tail = f"  # {total:,} matching" if total is not None else ""
        lines.append(f"pc = Fountain().paths(limit={self.limit}{extra}, **QUERY){tail}")
        return "\n".join(lines)


# ------------------------------------------------------------------- colour
# The categorical slots and the blue ramp follow the data-viz reference palette (fixed order, CVD-checked).
CATEGORICAL = {
    False: ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"],
    True: ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"],
}
SEQUENTIAL = [
    "#cde2fb",
    "#b7d3f6",
    "#9ec5f4",
    "#86b6ef",
    "#6da7ec",
    "#5598e7",
    "#3987e5",
    "#2a78d6",
    "#256abf",
    "#1c5cab",
    "#184f95",
    "#104281",
    "#0d366b",
]
OTHER = {False: "#9a9994", True: "#6f6e69"}
N_SLOTS = 7  # categorical slots in use; everything else is "other"
COLOR_MODES = [
    ("single", "single colour"),
    ("t0", "time recorded"),
    ("app", "app"),
    ("recording", "recording"),
    ("source", "source"),
    ("machine", "machine"),
    ("rgb", "recorded colour"),
]
COLOR_MODES += [(m.key, m.label) for m in METRICS]


def hex_rgb(h: str) -> tuple[int, int, int]:
    return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)


def ramp(u: np.ndarray, stops: list[str]) -> np.ndarray:
    """(n, 3) uint8 colours for u in 0..1 along the stops; NaN gets the middle stop."""
    table = np.array([hex_rgb(s) for s in stops], dtype=np.float64)
    u = np.asarray(u, dtype=np.float64)
    bad = ~np.isfinite(u)
    u = np.where(bad, 0.5, np.clip(u, 0.0, 1.0))
    pos = u * (len(stops) - 1)
    i = np.minimum(pos.astype(int), len(stops) - 2)
    f = (pos - i)[:, None]
    return np.rint(table[i] * (1 - f) + table[i + 1] * f).astype(np.uint8)


def sequential_stops(dark: bool) -> list[str]:
    """Light surface: steps 250..700, low values recede. Dark surface: 600 down to 100, the same idea."""
    return SEQUENTIAL[10::-1] if dark else SEQUENTIAL[3:]


class SlotAssigner:
    """Stable label -> categorical slot within a session, so an app keeps its colour from query to query."""

    def __init__(self, n_slots: int = N_SLOTS):
        self.n = n_slots
        self.slots: dict[str, int] = {}

    def assign(self, labels_by_count: list[str]) -> dict[str, int]:
        present = set(labels_by_count)
        for lab in [k for k in self.slots if k not in present]:
            del self.slots[lab]
        free = [i for i in range(self.n) if i not in self.slots.values()]
        for lab in labels_by_count:
            if lab in self.slots:
                continue
            if not free:
                break
            self.slots[lab] = free.pop(0)
        return dict(self.slots)


def normalise(values: np.ndarray, log_scale: bool) -> tuple[np.ndarray, float, float]:
    """Values to 0..1 between their 1st and 99th percentile (log space if asked); (u, lo, hi)."""
    v = np.asarray(values, dtype=np.float64)
    ok = np.isfinite(v) & ((v > 0) if log_scale else True)
    if not ok.any():
        return np.full(len(v), np.nan), 0.0, 1.0
    lo, hi = np.percentile(v[ok], [1, 99])
    if hi <= lo:
        lo, hi = v[ok].min(), v[ok].max()
    if hi <= lo:
        return np.where(ok, 0.5, np.nan), float(lo), float(hi)
    if log_scale:
        u = (np.log10(np.clip(np.where(ok, v, lo), lo, hi)) - np.log10(lo)) / (np.log10(hi) - np.log10(lo))
    else:
        u = (np.clip(np.where(ok, v, lo), lo, hi) - lo) / (hi - lo)
    return np.where(ok, u, np.nan), float(lo), float(hi)


def colorize(
    frame: Frame, mode: str, dark: bool, assigners: dict[str, SlotAssigner], ink: tuple[int, int, int]
) -> tuple[np.ndarray, dict]:
    """(n, 3) uint8 colour per path and a legend spec for the mode."""
    n = len(frame)
    other = np.array(hex_rgb(OTHER[dark]), dtype=np.uint8)
    out = np.tile(other, (n, 1))
    if mode == "single":
        out[:] = ink
        return out, {"kind": "none", "title": ""}
    if mode in LABELS:
        labels = [lab if lab else "(none)" for lab in frame.labels[mode].tolist()]
        counts = Counter(labels)
        slots = assigners.setdefault(mode, SlotAssigner()).assign([lab for lab, _ in counts.most_common()])
        palette = [np.array(hex_rgb(h), dtype=np.uint8) for h in CATEGORICAL[dark]]
        for k, lab in enumerate(labels):
            if lab in slots:
                out[k] = palette[slots[lab]]
        entries = [
            (lab, tuple(int(c) for c in palette[slot]), counts[lab])
            for lab, slot in sorted(slots.items(), key=lambda kv: kv[1])
        ]
        n_other = sum(c for lab, c in counts.items() if lab not in slots)
        if n_other:
            entries.append(("other", tuple(int(c) for c in other), n_other))
        return out, {"kind": "categorical", "title": mode, "entries": entries}
    if mode == "rgb":
        if frame.rgb is not None:
            for k in np.flatnonzero(frame.has_color):
                s, e = int(frame.offsets[k]), int(frame.offsets[k + 1])
                if e > s:
                    out[k] = np.rint(frame.rgb[s:e].mean(axis=0)).astype(np.uint8)
        return out, {"kind": "none", "title": f"{int(frame.has_color.sum())} of {n} paths carry colour"}
    stops = sequential_stops(dark)
    if mode == "t0":
        u, lo, hi = normalise(frame.t0_ns, False)
        lo_s, hi_s = (fmt_time(lo), fmt_time(hi)) if n else ("", "")
        title = "time recorded"
    else:
        values = frame.metrics.get(mode)
        if values is None:
            return out, {"kind": "none", "title": f"no {mode} in this answer"}
        u, lo, hi = normalise(values, METRIC[mode].log)
        lo_s, hi_s = fmt_metric(mode, lo), fmt_metric(mode, hi)
        title = METRIC[mode].label
    colours = ramp(u, stops)
    good = np.isfinite(u)
    out[good] = colours[good]
    return out, {"kind": "sequential", "title": title, "lo": lo_s, "hi": hi_s, "stops": stops}


# ----------------------------------------------------------------- geometry
def screen_size(frame: Frame | None) -> tuple[int, int]:
    """The most common known screen size in the frame, in logical pixels (1920x1080 when unknown)."""
    if frame is None or len(frame) == 0:
        return 1920, 1080
    w, h = frame.screen_w.astype(np.int64), frame.screen_h.astype(np.int64)
    ok = (w > 0) & (h > 0)
    if not ok.any():
        return 1920, 1080
    pairs, counts = np.unique(np.column_stack([w[ok], h[ok]]), axis=0, return_counts=True)
    best = pairs[int(np.argmax(counts))]
    return int(best[0]), int(best[1])


def nearest_path(wx: np.ndarray, wy: np.ndarray, offsets: np.ndarray, mx: float, my: float, radius: float = 8.0) -> int:
    """Index of the path with a point within radius pixels of (mx, my), nearest first; -1 if none."""
    if len(wx) == 0:
        return -1
    stride = max(1, len(wx) // 2_000_000)
    d2 = (wx[::stride] - mx) ** 2 + (wy[::stride] - my) ** 2
    i = int(np.argmin(d2))
    if d2[i] > radius * radius:
        return -1
    return int(np.searchsorted(offsets, i * stride, side="right") - 1)


def fit_points(x: np.ndarray, y: np.ndarray, box: QtCore.QRectF) -> tuple[np.ndarray, np.ndarray]:
    """Map points into box, keeping their aspect ratio and centring them."""
    x0, x1 = float(x.min()), float(x.max())
    y0, y1 = float(y.min()), float(y.max())
    s = min(box.width() / max(x1 - x0, 1e-9), box.height() / max(y1 - y0, 1e-9))
    ox = box.center().x() - (x0 + x1) / 2 * s
    oy = box.center().y() - (y0 + y1) / 2 * s
    return x * s + ox, y * s + oy


def _polygon(x: np.ndarray, y: np.ndarray) -> QtGui.QPolygonF:
    """A QPolygonF filled straight from numpy (no per-point Python objects)."""
    n = len(x)
    poly = QtGui.QPolygonF(n)
    if n:
        buf = poly.data()
        buf.setsize(16 * n)
        mem = np.frombuffer(buf, np.float64).reshape(-1, 2)
        mem[:, 0] = x
        mem[:, 1] = y
    return poly


def _pen(color: QtGui.QColor, width: float) -> QtGui.QPen:
    pen = QtGui.QPen(color, width)
    pen.setCosmetic(True)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    return pen


def _qcolor(rgb, alpha: int = 255) -> QtGui.QColor:
    return QtGui.QColor(int(rgb[0]), int(rgb[1]), int(rgb[2]), alpha)


def path_summary(frame: Frame, k: int) -> str:
    """One line for the status bar."""
    i = frame.info(k)
    when = fmt_time(i["t0_ns"])
    where = " · ".join(s for s in (i.get("recording"), i.get("app")) if s)
    nums = (
        f"{i.get('n_points', 0):,} pts · {fmt_metric('duration_s', i.get('duration_s'))} s · "
        f"dist {fmt_metric('distance', i.get('distance'))} · "
        f"ex {fmt_metric('entropy_x', i.get('entropy_x'))} ey {fmt_metric('entropy_y', i.get('entropy_y'))} "
        f"dc {fmt_metric('entropy_dc', i.get('entropy_dc'))} · aspect {fmt_metric('aspect', i.get('aspect'))}"
    )
    return f"#{i['id']} · {where} · {when} · {nums}"


# ---------------------------------------------------------------- histogram
class Histogram(QtWidgets.QWidget):
    """Population (grey) and current sample (blue) of one metric; drag to pick a range, double-click to clear."""

    rangeChanged = pyqtSignal(object, object)  # lo, hi; None means open
    NBINS = 36

    def __init__(self, metric: Metric):
        super().__init__()
        self.metric = metric
        self.domain: tuple[float, float] | None = None
        self.base: np.ndarray | None = None
        self.counts: np.ndarray | None = None
        self.lo: float | None = None
        self.hi: float | None = None
        self._drag: tuple[int, int] | None = None
        self.setFixedHeight(38)
        self.setCursor(Qt.CrossCursor)
        self.setToolTip(
            "grey: all paths (random sample), blue: this query\ndrag to set the range, double-click to clear it"
        )

    # ---- value <-> axis
    def _t(self, v):
        return np.log10(v) if self.metric.log else v

    def _inv(self, t):
        return 10.0**t if self.metric.log else t

    def set_domain(self, values: np.ndarray) -> None:
        v = np.asarray(values, dtype=np.float64)
        v = v[np.isfinite(v) & ((v > 0) if self.metric.log else True)]
        if len(v) < 2:
            self.domain = None
            return
        lo, hi = np.percentile(v, [0.5, 99.5])
        if hi <= lo:
            lo, hi = float(v.min()), float(v.max())
        self.domain = (float(lo), float(hi)) if hi > lo else None

    def _bins(self, values) -> np.ndarray | None:
        if self.domain is None or values is None:
            return None
        v = np.asarray(values, dtype=np.float64)
        v = v[np.isfinite(v)]
        lo, hi = self.domain
        t = self._t(np.clip(v, lo, hi))
        counts, _ = np.histogram(t, bins=self.NBINS, range=(self._t(lo), self._t(hi)))
        return counts

    def set_background(self, values: np.ndarray | None) -> None:
        if self.domain is None and values is not None:
            self.set_domain(values)
        self.base = self._bins(values)
        self.update()

    def set_values(self, values: np.ndarray | None) -> None:
        self.counts = self._bins(values)
        self.update()

    def set_range(self, lo, hi) -> None:
        self.lo, self.hi = lo, hi
        self.update()

    def _x(self, v: float) -> float:
        lo, hi = self.domain
        u = (self._t(min(max(v, lo), hi)) - self._t(lo)) / (self._t(hi) - self._t(lo))
        return u * (self.width() - 1)

    def _v(self, x: float) -> float:
        lo, hi = self.domain
        u = min(max(x / max(self.width() - 1, 1), 0.0), 1.0)
        return float(self._inv(self._t(lo) + u * (self._t(hi) - self._t(lo))))

    # ---- mouse
    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.LeftButton and self.domain is not None:
            self._drag = (e.x(), e.x())
            self.update()

    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        if self._drag is not None:
            self._drag = (self._drag[0], e.x())
            self.update()

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() != Qt.LeftButton or self._drag is None:
            return
        x0, x1 = sorted(self._drag)
        self._drag = None
        self.update()
        if x1 - x0 < 3:
            return
        lo = None if x0 <= 1 else self._v(x0)
        hi = None if x1 >= self.width() - 2 else self._v(x1)
        self.rangeChanged.emit(lo, hi)

    def mouseDoubleClickEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            self._drag = None
            self.rangeChanged.emit(None, None)

    # ---- paint
    def paintEvent(self, _e) -> None:
        pal = self.palette()
        dark = pal.color(QtGui.QPalette.Base).lightness() < 128
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(self.rect(), pal.color(QtGui.QPalette.Base))
        if self.domain is None:
            p.setPen(pal.color(QtGui.QPalette.PlaceholderText))
            p.drawText(self.rect(), Qt.AlignCenter, "no data")
            return
        bw = w / self.NBINS
        p.setPen(Qt.NoPen)
        for counts, color in (
            (self.base, QtGui.QColor(pal.color(QtGui.QPalette.Mid))),
            (self.counts, QtGui.QColor(CATEGORICAL[dark][0])),
        ):
            if counts is None or counts.max() == 0:
                continue
            color.setAlpha(140 if counts is self.base else 210)
            p.setBrush(color)
            top = counts / counts.max() * (h - 3)
            for i, hh in enumerate(top):
                if hh > 0:
                    p.drawRect(QtCore.QRectF(i * bw + 0.5, h - 1 - hh, max(bw - 1, 1), hh))
        # dim what the current range excludes
        shade = QtGui.QColor(pal.color(QtGui.QPalette.Window))
        shade.setAlpha(160)
        if self.lo is not None:
            p.fillRect(QtCore.QRectF(0, 0, self._x(self.lo), h), shade)
        if self.hi is not None:
            x = self._x(self.hi)
            p.fillRect(QtCore.QRectF(x, 0, w - x, h), shade)
        if self._drag is not None:
            x0, x1 = sorted(self._drag)
            band = QtGui.QColor(pal.color(QtGui.QPalette.Highlight))
            band.setAlpha(60)
            p.fillRect(QtCore.QRectF(x0, 0, x1 - x0, h), band)
            p.setPen(_pen(pal.color(QtGui.QPalette.Highlight), 1))
            p.drawLine(x0, 0, x0, h)
            p.drawLine(x1, 0, x1, h)
        p.setPen(_pen(pal.color(QtGui.QPalette.Mid), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRect(QtCore.QRectF(0.5, 0.5, w - 1, h - 1))


class RangeRow(QtWidgets.QWidget):
    """Label, min and max fields and the histogram of one metric."""

    changed = pyqtSignal()

    def __init__(self, metric: Metric):
        super().__init__()
        self.metric = metric
        self.hist = Histogram(metric)
        self.lo_edit = QtWidgets.QLineEdit()
        self.hi_edit = QtWidgets.QLineEdit()
        for edit, text in ((self.lo_edit, "min"), (self.hi_edit, "max")):
            edit.setPlaceholderText(text)
            edit.setFixedWidth(70)
            edit.setAlignment(Qt.AlignRight)
            edit.editingFinished.connect(self._edited)
        label = QtWidgets.QLabel(metric.label)
        grid = QtWidgets.QGridLayout(self)
        grid.setContentsMargins(0, 2, 0, 2)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(2)
        grid.addWidget(label, 0, 0)
        grid.addWidget(self.lo_edit, 0, 1)
        grid.addWidget(QtWidgets.QLabel("–"), 0, 2)
        grid.addWidget(self.hi_edit, 0, 3)
        grid.addWidget(self.hist, 1, 0, 1, 4)
        grid.setColumnStretch(0, 1)
        self.hist.rangeChanged.connect(self._dragged)

    @staticmethod
    def _parse(text: str) -> float | None:
        text = text.strip().replace(",", ".")
        if not text:
            return None
        try:
            v = float(text)
        except ValueError:
            return None
        return v if math.isfinite(v) else None

    def value(self) -> tuple[float | None, float | None]:
        return self._parse(self.lo_edit.text()), self._parse(self.hi_edit.text())

    def _fmt(self, v: float | None) -> str:
        if v is None:
            return ""
        if self.metric.key == "n_points":
            return str(int(round(v)))
        return f"{float(f'{v:.3g}'):g}"

    def set_value(self, lo, hi, emit: bool = True) -> None:
        self.lo_edit.setText(self._fmt(lo))
        self.hi_edit.setText(self._fmt(hi))
        self.hist.set_range(*self.value())
        if emit:
            self.changed.emit()

    def _edited(self) -> None:
        self.hist.set_range(*self.value())
        self.changed.emit()

    def _dragged(self, lo, hi) -> None:
        if self.metric.key == "n_points":
            lo = None if lo is None else math.floor(lo)
            hi = None if hi is None else math.ceil(hi)
        self.set_value(lo, hi)


# -------------------------------------------------------------- query panel
class QueryPanel(QtWidgets.QWidget):
    """Every fountain filter as a control; state() is the QueryState, changed fires on any edit."""

    changed = pyqtSignal()
    run = pyqtSignal()
    copyPython = pyqtSignal()

    def __init__(self, limit: int):
        super().__init__()
        col = QtWidgets.QVBoxLayout(self)
        col.setContentsMargins(8, 8, 8, 8)
        col.setSpacing(6)

        def heading(text: str) -> None:
            lab = QtWidgets.QLabel(text)
            f = lab.font()
            f.setBold(True)
            lab.setFont(f)
            lab.setContentsMargins(0, 8, 0, 0)
            col.addWidget(lab)

        def form() -> QtWidgets.QFormLayout:
            fl = QtWidgets.QFormLayout()
            fl.setContentsMargins(0, 0, 0, 0)
            fl.setHorizontalSpacing(8)
            fl.setVerticalSpacing(4)
            fl.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
            col.addLayout(fl)
            return fl

        # ---- origin
        heading("Origin")
        fl = form()
        self.src_legacy = QtWidgets.QCheckBox("legacy")
        self.src_logger = QtWidgets.QCheckBox("mouse_logger")
        for cb in (self.src_legacy, self.src_logger):
            cb.setChecked(True)
            cb.toggled.connect(self.changed)
        src = QtWidgets.QHBoxLayout()
        src.addWidget(self.src_legacy)
        src.addWidget(self.src_logger)
        src.addStretch(1)
        fl.addRow("source", src)
        self.machine = self._combo("any machine")
        self.app = self._combo("any app")
        self.recording = self._combo("any recording, globs ok")
        fl.addRow("machine", self.machine)
        fl.addRow("app", self.app)
        fl.addRow("recording", self.recording)

        # ---- when
        heading("When")
        fl = form()
        self.since = QtWidgets.QLineEdit()
        self.until = QtWidgets.QLineEdit()
        for edit in (self.since, self.until):
            edit.setPlaceholderText("all · 7d · today · 2026-09-30 14:00")
            edit.editingFinished.connect(self.changed)
        fl.addRow("since", self.since)
        fl.addRow("until", self.until)

        # ---- shape
        heading("Shape")
        self.rows: dict[str, RangeRow] = {}
        for m in METRICS:
            row = RangeRow(m)
            row.changed.connect(self.changed)
            self.rows[m.key] = row
            col.addWidget(row)

        # ---- screen area
        heading("Screen area")
        fl = form()
        self.bbox_use = QtWidgets.QCheckBox("limit to box (right-drag on the canvas)")
        self.bbox_use.toggled.connect(self.changed)
        fl.addRow(self.bbox_use)
        self.bbox_spins = []
        box = QtWidgets.QGridLayout()
        box.setContentsMargins(0, 0, 0, 0)
        for i, name in enumerate(("x0", "y0", "x1", "y1")):
            sp = QtWidgets.QDoubleSpinBox()
            sp.setRange(-5.0, 5.0)
            sp.setDecimals(3)
            sp.setSingleStep(0.05)
            sp.setValue(float(i >= 2))
            sp.valueChanged.connect(self._bbox_edited)
            self.bbox_spins.append(sp)
            box.addWidget(QtWidgets.QLabel(name), i // 2, (i % 2) * 2)
            box.addWidget(sp, i // 2, (i % 2) * 2 + 1)
        fl.addRow(box)
        self.bbox_mode = QtWidgets.QComboBox()
        self.bbox_mode.addItem("every point inside", "inside")
        self.bbox_mode.addItem("touches the box", "intersects")
        self.bbox_mode.currentIndexChanged.connect(self.changed)
        fl.addRow("mode", self.bbox_mode)

        # ---- colour
        heading("Colour")
        fl = form()
        self.has_color = QtWidgets.QComboBox()
        self.has_color.addItem("any", None)
        self.has_color.addItem("recorded with colour", True)
        self.has_color.addItem("without colour", False)
        self.has_color.currentIndexChanged.connect(self.changed)
        fl.addRow("colour", self.has_color)

        # ---- order and size
        heading("Order and size")
        fl = form()
        self.sort = QtWidgets.QComboBox()
        self.sort.addItem("as stored", None)
        for key in SORT_KEYS:
            self.sort.addItem(METRIC[key].label if key in METRIC else key, key)
        self.sort.setCurrentIndex(1)  # random: a fair look at the population
        self.sort.currentIndexChanged.connect(self._sort_changed)
        self.order = QtWidgets.QComboBox()
        self.order.addItem("ascending", "asc")
        self.order.addItem("descending", "desc")
        self.order.currentIndexChanged.connect(self.changed)
        srt = QtWidgets.QHBoxLayout()
        srt.addWidget(self.sort, 2)
        srt.addWidget(self.order, 1)
        fl.addRow("sort", srt)
        self.seed = QtWidgets.QSpinBox()
        self.seed.setRange(0, 2**31 - 1)
        self.seed.setValue(1)
        self.seed.valueChanged.connect(self.changed)
        self.reroll = QtWidgets.QPushButton("reroll")
        self.reroll.setToolTip("new random seed (R)")
        self.reroll.clicked.connect(self.new_seed)
        sd = QtWidgets.QHBoxLayout()
        sd.addWidget(self.seed, 1)
        sd.addWidget(self.reroll)
        fl.addRow("seed", sd)
        self.limit = QtWidgets.QSpinBox()
        self.limit.setRange(1, 100000)
        self.limit.setSingleStep(100)
        self.limit.setValue(limit)
        self.limit.valueChanged.connect(self.changed)
        fl.addRow("limit", self.limit)
        self.offset = QtWidgets.QSpinBox()
        self.offset.setRange(0, 10_000_000)
        self.offset.valueChanged.connect(self.changed)
        self.prev_page = QtWidgets.QToolButton()
        self.prev_page.setText("◀")
        self.prev_page.clicked.connect(lambda: self.page(-1))
        self.next_page = QtWidgets.QToolButton()
        self.next_page.setText("▶")
        self.next_page.clicked.connect(lambda: self.page(+1))
        pg = QtWidgets.QHBoxLayout()
        pg.addWidget(self.offset, 1)
        pg.addWidget(self.prev_page)
        pg.addWidget(self.next_page)
        fl.addRow("offset", pg)
        self.resample = QtWidgets.QSpinBox()
        self.resample.setRange(0, 2000)
        self.resample.setSpecialValueText("raw points")
        self.resample.setToolTip("resample every path to this many points, spaced evenly along it")
        self.resample.valueChanged.connect(self.changed)
        fl.addRow("resample", self.resample)

        # ---- run
        btns = QtWidgets.QHBoxLayout()
        self.auto = QtWidgets.QCheckBox("auto")
        self.auto.setChecked(True)
        self.auto.setToolTip("query on every change")
        self.run_btn = QtWidgets.QPushButton("Run query")
        self.run_btn.setDefault(True)
        self.run_btn.clicked.connect(self.run)
        self.reset_btn = QtWidgets.QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset)
        btns.addWidget(self.auto)
        btns.addStretch(1)
        btns.addWidget(self.reset_btn)
        btns.addWidget(self.run_btn)
        col.addSpacing(6)
        col.addLayout(btns)

        # ---- the query as Python
        heading("For a composition")
        self.snippet = QtWidgets.QPlainTextEdit()
        self.snippet.setReadOnly(True)
        self.snippet.setFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont))
        self.snippet.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.snippet.setFixedHeight(150)
        col.addWidget(self.snippet)
        self.copy_btn = QtWidgets.QPushButton("Copy Python")
        self.copy_btn.clicked.connect(self.copyPython)
        col.addWidget(self.copy_btn, 0, Qt.AlignRight)
        col.addStretch(1)

    # ---- pieces
    def _combo(self, placeholder: str) -> QtWidgets.QComboBox:
        cb = QtWidgets.QComboBox()
        cb.setEditable(True)
        cb.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        cb.addItem("")
        cb.lineEdit().setPlaceholderText(placeholder)
        cb.lineEdit().editingFinished.connect(self.changed)
        cb.currentIndexChanged.connect(self.changed)
        cb.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        cb.completer().setFilterMode(Qt.MatchContains)
        cb.completer().setCaseSensitivity(Qt.CaseInsensitive)
        return cb

    @staticmethod
    def _fill(cb: QtWidgets.QComboBox, values: list[str]) -> None:
        current = cb.currentText()
        cb.blockSignals(True)
        cb.clear()
        cb.addItem("")
        for v in values:
            if v:
                cb.addItem(v)
        cb.setCurrentText(current)
        cb.blockSignals(False)

    def _bbox_edited(self) -> None:
        if self.bbox_use.isChecked():
            self.changed.emit()

    def _sort_changed(self) -> None:
        random = self.sort.currentData() == "random"
        self.seed.setEnabled(random)
        self.reroll.setEnabled(random)
        self.order.setEnabled(not random)
        self.changed.emit()

    # ---- state
    def state(self) -> QueryState:
        def listed(cb: QtWidgets.QComboBox) -> list[str]:
            text = cb.currentText().strip()
            return [v.strip() for v in text.split(",") if v.strip()] if text else []

        sources = [
            name for cb, name in ((self.src_legacy, "legacy"), (self.src_logger, "mouse_logger")) if cb.isChecked()
        ]
        return QueryState(
            ranges={key: row.value() for key, row in self.rows.items()},
            bbox=tuple(sp.value() for sp in self.bbox_spins) if self.bbox_use.isChecked() else None,
            bbox_mode=self.bbox_mode.currentData(),
            since=self.since.text().strip() or None,
            until=self.until.text().strip() or None,
            source=sources if len(sources) == 1 else [],
            machine=listed(self.machine),
            app=listed(self.app),
            recording=listed(self.recording),
            has_color=self.has_color.currentData(),
            sort=self.sort.currentData(),
            order=self.order.currentData(),
            seed=self.seed.value() if self.sort.currentData() == "random" else None,
            limit=self.limit.value(),
            offset=self.offset.value(),
            resample=self.resample.value() or None,
        )

    def set_lists(self, dicts: dict[str, list[str]]) -> None:
        self._fill(self.machine, sorted(dicts.get("machine", [])))
        self._fill(self.app, sorted(dicts.get("app", [])))
        self._fill(self.recording, sorted(dicts.get("recording", [])))

    def set_baseline(self, frame: Frame) -> None:
        for key, row in self.rows.items():
            row.hist.set_background(frame.metrics.get(key))

    def set_sample(self, frame: Frame | None) -> None:
        for key, row in self.rows.items():
            row.hist.set_values(None if frame is None else frame.metrics.get(key))

    def set_bbox(self, bbox: tuple[float, float, float, float] | None) -> None:
        if bbox is None:
            self.bbox_use.setChecked(False)
            return
        self.blockSignals(True)
        for sp, v in zip(self.bbox_spins, bbox):
            sp.blockSignals(True)
            sp.setValue(float(v))
            sp.blockSignals(False)
        self.blockSignals(False)
        if self.bbox_use.isChecked():
            self.changed.emit()
        else:
            self.bbox_use.setChecked(True)

    def set_filter(self, name: str, value: str) -> None:
        """Pin recording/app/machine to one value (from the detail panel)."""
        cb = {"recording": self.recording, "app": self.app, "machine": self.machine}[name]
        cb.setCurrentText(value)
        self.offset.setValue(0)
        self.changed.emit()

    def new_seed(self) -> None:
        self.seed.setValue(int(np.random.default_rng().integers(1, 2**31 - 1)))

    def page(self, direction: int) -> None:
        self.offset.setValue(max(0, self.offset.value() + direction * self.limit.value()))

    def reset(self) -> None:
        self.blockSignals(True)
        for row in self.rows.values():
            row.set_value(None, None, emit=False)
        for cb in (self.machine, self.app, self.recording):
            cb.setCurrentText("")
        self.since.clear()
        self.until.clear()
        self.src_legacy.setChecked(True)
        self.src_logger.setChecked(True)
        self.bbox_use.setChecked(False)
        self.has_color.setCurrentIndex(0)
        self.sort.setCurrentIndex(1)
        self.order.setCurrentIndex(0)
        self.offset.setValue(0)
        self.resample.setValue(0)
        self.blockSignals(False)
        self.changed.emit()

    def show_python(self, text: str) -> None:
        self.snippet.setPlainText(text)


# ------------------------------------------------------------------- canvas
class Canvas(QtWidgets.QWidget):
    """The paths: overlaid in the screen frame (zoom, pan, hover, click, right-drag a box) or as a grid of tiles."""

    hovered = pyqtSignal(int)
    selected = pyqtSignal(int)
    bboxDrawn = pyqtSignal(object)
    MARGIN = 24
    GRID_MARGIN = 8

    def __init__(self):
        super().__init__()
        self.frame: Frame | None = None
        self.colors: np.ndarray | None = None
        self.alpha = 170
        self.line_width = 1.0
        self.mode = "overlay"
        self.cell = 120
        self.sw, self.sh = 1920, 1080
        self.zoom = 1.0
        self.cx = self.cy = 0.5
        self.hover = -1
        self.sel = -1
        self._pix: QtGui.QPixmap | None = None
        self._wxy: tuple[np.ndarray, np.ndarray] | None = None
        self._drag: list | None = None
        self.setMouseTracking(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setMinimumSize(240, 160)
        self.setCursor(Qt.CrossCursor)

    # ---- state
    def set_frame(self, frame: Frame | None) -> None:
        self.frame = frame
        self.sw, self.sh = screen_size(frame)
        self.hover = self.sel = -1
        self._invalidate()
        self._update_geometry()
        self.update()

    def set_colors(self, colors: np.ndarray | None) -> None:
        self.colors = colors
        self._invalidate()
        self.update()

    def set_style(self, alpha: int | None = None, line_width: float | None = None) -> None:
        if alpha is not None:
            self.alpha = int(alpha)
        if line_width is not None:
            self.line_width = float(line_width)
        self._invalidate()
        self.update()

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.hover = -1
        self._invalidate()
        self._update_geometry()
        self.update()

    def set_cell(self, cell: int) -> None:
        self.cell = max(40, int(cell))
        self._update_geometry()
        self.update()

    def set_selected(self, k: int) -> None:
        self.sel = k
        self.update()

    def fit(self) -> None:
        self.zoom, self.cx, self.cy = 1.0, 0.5, 0.5
        self._invalidate()
        self.update()

    def zoom_to(self, k: int) -> None:
        if self.frame is None or "x0" not in self.frame.metrics:
            return
        m = self.frame.metrics
        bw = max(float(m["x1"][k] - m["x0"][k]), 0.002) * self.sw
        bh = max(float(m["y1"][k] - m["y0"][k]), 0.002) * self.sh
        wanted = 0.7 * min(max(self.width() - 2 * self.MARGIN, 1) / bw, max(self.height() - 2 * self.MARGIN, 1) / bh)
        self.zoom = min(max(wanted / self._fit_scale(), 0.2), 500.0)
        self.cx = float(m["x0"][k] + m["x1"][k]) / 2
        self.cy = float(m["y0"][k] + m["y1"][k]) / 2
        self._invalidate()
        self.update()

    def _invalidate(self) -> None:
        self._pix = None
        self._wxy = None

    # ---- overlay transform
    def _fit_scale(self) -> float:
        m = self.MARGIN
        return min(max(self.width() - 2 * m, 1) / self.sw, max(self.height() - 2 * m, 1) / self.sh)

    def _scale(self) -> float:
        return self._fit_scale() * self.zoom

    def to_widget(self, x, y):
        s = self._scale()
        return self.width() / 2 + (x - self.cx) * self.sw * s, self.height() / 2 + (y - self.cy) * self.sh * s

    def to_norm(self, px: float, py: float) -> tuple[float, float]:
        s = self._scale()
        return self.cx + (px - self.width() / 2) / (self.sw * s), self.cy + (py - self.height() / 2) / (self.sh * s)

    # ---- grid layout
    def _cols(self) -> int:
        return max(1, (self.width() - 2 * self.GRID_MARGIN) // self.cell)

    def _update_geometry(self) -> None:
        if self.mode == "grid" and self.frame is not None and len(self.frame):
            rows = math.ceil(len(self.frame) / self._cols())
            want = rows * self.cell + 2 * self.GRID_MARGIN
        else:
            want = 160
        if self.minimumHeight() != want:
            self.setMinimumHeight(want)

    def _tile_rect(self, k: int) -> QtCore.QRectF:
        r, c = divmod(k, self._cols())
        m, cell = self.GRID_MARGIN, self.cell
        return QtCore.QRectF(m + c * cell, m + r * cell, cell - 6, cell - 6)

    def _tile_at(self, pos: QtCore.QPoint) -> int:
        if self.frame is None:
            return -1
        c = (pos.x() - self.GRID_MARGIN) // self.cell
        r = (pos.y() - self.GRID_MARGIN) // self.cell
        if c < 0 or c >= self._cols() or r < 0:
            return -1
        k = int(r * self._cols() + c)
        return k if k < len(self.frame) and self._tile_rect(k).contains(QtCore.QPointF(pos)) else -1

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self._invalidate()
        self._update_geometry()

    # ---- hit test
    def _hit(self, pos: QtCore.QPoint) -> int:
        if self.frame is None or len(self.frame) == 0:
            return -1
        if self.mode == "grid":
            return self._tile_at(pos)
        if self._wxy is None:
            self._render()
        wx, wy = self._wxy
        return nearest_path(wx, wy, self.frame.offsets, pos.x(), pos.y())

    # ---- mouse
    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            self._drag = ["pan", e.pos(), False]
        elif e.button() == Qt.RightButton and self.mode == "overlay":
            self._drag = ["bbox", e.pos(), e.pos()]

    def mouseMoveEvent(self, e: QtGui.QMouseEvent) -> None:
        if self._drag is not None and self._drag[0] == "pan":
            if self.mode != "overlay":
                return
            d = e.pos() - self._drag[1]
            if self._drag[2] or d.manhattanLength() > 3:
                s = self._scale()
                self.cx -= d.x() / (self.sw * s)
                self.cy -= d.y() / (self.sh * s)
                self._drag[1] = e.pos()
                self._drag[2] = True
                self._invalidate()
                self.update()
            return
        if self._drag is not None and self._drag[0] == "bbox":
            self._drag[2] = e.pos()
            self.update()
            return
        k = self._hit(e.pos())
        if k != self.hover:
            self.hover = k
            self.hovered.emit(k)
            self.update()

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent) -> None:
        drag, self._drag = self._drag, None
        if drag is None:
            return
        if drag[0] == "pan" and e.button() == Qt.LeftButton and not drag[2]:
            k = self._hit(e.pos())
            self.sel = k
            self.selected.emit(k)
        elif drag[0] == "bbox" and e.button() == Qt.RightButton:
            a, b = drag[1], drag[2]
            if abs(a.x() - b.x()) > 3 and abs(a.y() - b.y()) > 3:
                x0, y0 = self.to_norm(min(a.x(), b.x()), min(a.y(), b.y()))
                x1, y1 = self.to_norm(max(a.x(), b.x()), max(a.y(), b.y()))
                self.bboxDrawn.emit((x0, y0, x1, y1))
        self.update()

    def mouseDoubleClickEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.LeftButton and self.mode == "overlay":
            self._drag = None
            self.fit()

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        if self.mode != "overlay":
            e.ignore()
            return
        steps = e.angleDelta().y() / 120.0
        if steps == 0:
            return
        nx, ny = self.to_norm(e.x(), e.y())
        self.zoom = min(max(self.zoom * (1.2**steps), 0.2), 500.0)
        s = self._scale()
        self.cx = nx - (e.x() - self.width() / 2) / (self.sw * s)
        self.cy = ny - (e.y() - self.height() / 2) / (self.sh * s)
        self._invalidate()
        self.update()
        e.accept()

    def leaveEvent(self, _e) -> None:
        if self.hover != -1:
            self.hover = -1
            self.hovered.emit(-1)
            self.update()

    # ---- paint
    def _render(self) -> None:
        """The overlay as a pixmap, plus the widget-space points for hit tests."""
        pal = self.palette()
        W, H = self.width(), self.height()
        pix = QtGui.QPixmap(max(W, 1), max(H, 1))
        pix.fill(pal.color(QtGui.QPalette.Base))
        p = QtGui.QPainter(pix)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        x0, y0 = self.to_widget(0.0, 0.0)
        x1, y1 = self.to_widget(1.0, 1.0)
        p.setPen(_pen(pal.color(QtGui.QPalette.Mid), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRect(QtCore.QRectF(x0, y0, x1 - x0, y1 - y0))
        frame = self.frame
        self._wxy = (np.zeros(0), np.zeros(0))
        if frame is not None and len(frame):
            wx, wy = self.to_widget(frame.x.astype(np.float64), frame.y.astype(np.float64))
            self._wxy = (wx, wy)
            m = frame.metrics
            if all(k in m for k in ("x0", "y0", "x1", "y1")):
                bx0, by0 = self.to_widget(m["x0"], m["y0"])
                bx1, by1 = self.to_widget(m["x1"], m["y1"])
                visible = np.flatnonzero((bx1 >= 0) & (bx0 <= W) & (by1 >= 0) & (by0 <= H))
            else:
                visible = np.arange(len(frame))
            colors = self.colors if self.colors is not None and len(self.colors) == len(frame) else None
            ink = pal.color(QtGui.QPalette.Text)
            pen = _pen(ink, self.line_width)
            off = frame.offsets
            for k in visible.tolist():
                s, e = int(off[k]), int(off[k + 1])
                if e - s < 1:
                    continue
                c = _qcolor(colors[k], self.alpha) if colors is not None else QtGui.QColor(ink)
                if colors is None:
                    c.setAlpha(self.alpha)
                pen.setColor(c)
                p.setPen(pen)
                if e - s == 1:
                    p.drawPoint(QtCore.QPointF(wx[s], wy[s]))
                else:
                    p.drawPolyline(_polygon(wx[s:e], wy[s:e]))
        p.end()
        self._pix = pix

    def _draw_path(self, p: QtGui.QPainter, k: int, color: QtGui.QColor, width: float) -> None:
        wx, wy = self._wxy
        s, e = int(self.frame.offsets[k]), int(self.frame.offsets[k + 1])
        if e - s < 1:
            return
        p.setPen(_pen(color, width))
        p.setBrush(Qt.NoBrush)
        p.drawPolyline(_polygon(wx[s:e], wy[s:e]))
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawEllipse(QtCore.QPointF(wx[s], wy[s]), 3.5, 3.5)
        p.setBrush(self.palette().color(QtGui.QPalette.Base))
        p.setPen(_pen(color, 1.5))
        p.drawEllipse(QtCore.QPointF(wx[e - 1], wy[e - 1]), 3.0, 3.0)

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        pal = self.palette()
        if self.mode == "grid":
            self._paint_grid(e)
            return
        if self._pix is None:
            self._render()
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.drawPixmap(0, 0, self._pix)
        hi = pal.color(QtGui.QPalette.Highlight)
        if self.frame is not None and len(self.frame):
            if 0 <= self.sel < len(self.frame):
                self._draw_path(p, self.sel, hi, 2.0)
            if 0 <= self.hover < len(self.frame) and self.hover != self.sel:
                c = QtGui.QColor(hi)
                c.setAlpha(200)
                self._draw_path(p, self.hover, c, 2.5)
        else:
            p.setPen(pal.color(QtGui.QPalette.PlaceholderText))
            p.drawText(self.rect(), Qt.AlignCenter, "no paths" if self.frame is not None else "")
        if self._drag is not None and self._drag[0] == "bbox":
            a, b = self._drag[1], self._drag[2]
            band = QtGui.QColor(hi)
            band.setAlpha(40)
            p.setBrush(band)
            p.setPen(_pen(hi, 1))
            p.drawRect(QtCore.QRectF(QtCore.QPointF(a), QtCore.QPointF(b)).normalized())

    def _paint_grid(self, e: QtGui.QPaintEvent) -> None:
        pal = self.palette()
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.fillRect(e.rect(), pal.color(QtGui.QPalette.Window))
        frame = self.frame
        if frame is None or len(frame) == 0:
            p.setPen(pal.color(QtGui.QPalette.PlaceholderText))
            p.drawText(self.rect(), Qt.AlignCenter, "no paths" if frame is not None else "")
            return
        cols, cell, m = self._cols(), self.cell, self.GRID_MARGIN
        r0 = max(0, (e.rect().top() - m) // cell)
        r1 = (e.rect().bottom() - m) // cell + 1
        k0, k1 = int(r0 * cols), int(min(len(frame), r1 * cols))
        colors = self.colors if self.colors is not None and len(self.colors) == len(frame) else None
        ink = pal.color(QtGui.QPalette.Text)
        hi = pal.color(QtGui.QPalette.Highlight)
        for k in range(k0, k1):
            tile = self._tile_rect(k)
            p.setPen(_pen(hi, 2) if k == self.sel else Qt.NoPen)
            p.setBrush(pal.color(QtGui.QPalette.AlternateBase if k in (self.hover, self.sel) else QtGui.QPalette.Base))
            p.drawRoundedRect(tile, 5, 5)
            x, y = frame.points(k)
            if len(x) == 0:
                continue
            fx, fy = fit_points(
                x.astype(np.float64) * self.sw, y.astype(np.float64) * self.sh, tile.adjusted(9, 9, -9, -9)
            )
            color = _qcolor(colors[k]) if colors is not None else QtGui.QColor(ink)
            p.setPen(_pen(color, max(self.line_width, 1.2)))
            p.setBrush(Qt.NoBrush)
            if len(fx) == 1:
                p.drawPoint(QtCore.QPointF(fx[0], fy[0]))
            else:
                p.drawPolyline(_polygon(fx, fy))
            p.setPen(Qt.NoPen)
            p.setBrush(color)
            p.drawEllipse(QtCore.QPointF(fx[0], fy[0]), 2.6, 2.6)


# ------------------------------------------------------------------- legend
class Legend(QtWidgets.QWidget):
    """What the colours mean: swatches for categories, a ramp for magnitudes."""

    ROW = 18

    def __init__(self):
        super().__init__()
        self.spec: dict = {"kind": "none", "title": ""}
        self.setFixedHeight(self.ROW)

    def set_spec(self, spec: dict) -> None:
        self.spec = spec
        if spec["kind"] == "categorical":
            self.setFixedHeight(self.ROW * (len(spec["entries"]) + 1))
        elif spec["kind"] == "sequential":
            self.setFixedHeight(self.ROW * 3)
        else:
            self.setFixedHeight(self.ROW if spec.get("title") else 0)
        self.update()

    def paintEvent(self, _e) -> None:
        pal = self.palette()
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        fm = p.fontMetrics()
        spec = self.spec
        p.setPen(pal.color(QtGui.QPalette.Text))
        if spec["kind"] == "none":
            p.drawText(QtCore.QRectF(0, 0, self.width(), self.ROW), Qt.AlignVCenter, spec.get("title", ""))
            return
        p.drawText(QtCore.QRectF(0, 0, self.width(), self.ROW), Qt.AlignVCenter, spec["title"])
        if spec["kind"] == "categorical":
            for i, (label, rgb, count) in enumerate(spec["entries"]):
                y = self.ROW * (i + 1)
                p.setPen(Qt.NoPen)
                p.setBrush(_qcolor(rgb))
                p.drawRoundedRect(QtCore.QRectF(2, y + 4, 12, 10), 2, 2)
                p.setPen(pal.color(QtGui.QPalette.Text))
                text = fm.elidedText(label, Qt.ElideMiddle, self.width() - 70)
                p.drawText(QtCore.QRectF(20, y, self.width() - 20, self.ROW), Qt.AlignVCenter, text)
                p.setPen(pal.color(QtGui.QPalette.PlaceholderText))
                p.drawText(
                    QtCore.QRectF(0, y, self.width() - 4, self.ROW), Qt.AlignVCenter | Qt.AlignRight, f"{count:,}"
                )
        else:
            y = self.ROW + 2
            grad = QtGui.QLinearGradient(0, 0, self.width(), 0)
            stops = spec["stops"]
            for i, h in enumerate(stops):
                grad.setColorAt(i / (len(stops) - 1), QtGui.QColor(h))
            p.setPen(Qt.NoPen)
            p.setBrush(grad)
            p.drawRoundedRect(QtCore.QRectF(0, y, self.width(), 8), 2, 2)
            p.setPen(pal.color(QtGui.QPalette.PlaceholderText))
            p.drawText(QtCore.QRectF(0, y + 10, self.width(), self.ROW), Qt.AlignVCenter, spec["lo"])
            p.drawText(QtCore.QRectF(0, y + 10, self.width(), self.ROW), Qt.AlignVCenter | Qt.AlignRight, spec["hi"])


# ------------------------------------------------------------------- detail
class PathPicture(QtWidgets.QWidget):
    """One path on its own, shaded light to dark along its duration, with where it sat on the screen."""

    def __init__(self):
        super().__init__()
        self.frame: Frame | None = None
        self.k = -1
        self.setMinimumHeight(220)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

    def set_path(self, frame: Frame | None, k: int) -> None:
        self.frame, self.k = frame, k
        self.update()

    def paintEvent(self, _e) -> None:
        pal = self.palette()
        dark = pal.color(QtGui.QPalette.Base).lightness() < 128
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.fillRect(self.rect(), pal.color(QtGui.QPalette.Base))
        p.setPen(_pen(pal.color(QtGui.QPalette.Mid), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRect(QtCore.QRectF(0.5, 0.5, self.width() - 1, self.height() - 1))
        if self.frame is None or not (0 <= self.k < len(self.frame)):
            p.setPen(pal.color(QtGui.QPalette.PlaceholderText))
            p.drawText(self.rect(), Qt.AlignCenter, "click a path")
            return
        frame, k = self.frame, self.k
        sw, sh = screen_size(frame)
        x, y = frame.points(k)
        if len(x) == 0:
            return
        box = QtCore.QRectF(self.rect()).adjusted(16, 16, -16, -16)
        fx, fy = fit_points(x.astype(np.float64) * sw, y.astype(np.float64) * sh, box)
        n = len(fx)
        t = frame.t
        if t is not None and n > 1:
            s = int(frame.offsets[k])
            tt = t[s : s + n].astype(np.float64)
            u = (tt - tt[0]) / max(tt[-1] - tt[0], 1.0)
        else:
            u = np.linspace(0, 1, n)
        cols = ramp(u, sequential_stops(dark))
        for i in range(n - 1):
            p.setPen(_pen(_qcolor(cols[i]), 2.0))
            p.drawLine(QtCore.QPointF(fx[i], fy[i]), QtCore.QPointF(fx[i + 1], fy[i + 1]))
        p.setPen(Qt.NoPen)
        p.setBrush(_qcolor(cols[0]))
        p.drawEllipse(QtCore.QPointF(fx[0], fy[0]), 4, 4)
        p.setBrush(pal.color(QtGui.QPalette.Base))
        p.setPen(_pen(_qcolor(cols[-1]), 2))
        p.drawEllipse(QtCore.QPointF(fx[-1], fy[-1]), 3.5, 3.5)
        # where on the screen
        mw = 48.0
        mh = mw * sh / sw
        mm = QtCore.QRectF(self.width() - 8 - mw, 8, mw, mh)
        p.setBrush(Qt.NoBrush)
        p.setPen(_pen(pal.color(QtGui.QPalette.Mid), 1))
        p.drawRect(mm)
        bx0, bx1 = float(x.min()), float(x.max())
        by0, by1 = float(y.min()), float(y.max())
        hi = pal.color(QtGui.QPalette.Highlight)
        p.setPen(_pen(hi, 1))
        hb = QtGui.QColor(hi)
        hb.setAlpha(70)
        p.setBrush(hb)
        p.drawRect(
            QtCore.QRectF(mm.left() + bx0 * mw, mm.top() + by0 * mh, max((bx1 - bx0) * mw, 2), max((by1 - by0) * mh, 2))
        )


class DetailView(QtWidgets.QWidget):
    """The selected path: its picture, every number the fountain has, and shortcuts to narrow the query."""

    pin = pyqtSignal(str, str)  # (field, value)
    zoomTo = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.frame: Frame | None = None
        self.k = -1
        col = QtWidgets.QVBoxLayout(self)
        col.setContentsMargins(8, 8, 8, 8)
        col.setSpacing(6)
        self.picture = PathPicture()
        col.addWidget(self.picture)
        self.text = QtWidgets.QTextBrowser()
        self.text.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.text.viewport().setAutoFillBackground(False)
        self.text.setOpenLinks(False)
        wrap = QtGui.QTextOption()
        wrap.setWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.text.document().setDefaultTextOption(wrap)
        col.addWidget(self.text, 1)
        row = QtWidgets.QGridLayout()
        self.btn_rec = QtWidgets.QPushButton("only this recording")
        self.btn_app = QtWidgets.QPushButton("only this app")
        self.btn_zoom = QtWidgets.QPushButton("zoom to it")
        self.btn_copy = QtWidgets.QPushButton("copy id")
        self.btn_rec.clicked.connect(lambda: self._pin("recording"))
        self.btn_app.clicked.connect(lambda: self._pin("app"))
        self.btn_zoom.clicked.connect(lambda: self.zoomTo.emit(self.k))
        self.btn_copy.clicked.connect(self._copy)
        row.addWidget(self.btn_rec, 0, 0)
        row.addWidget(self.btn_app, 0, 1)
        row.addWidget(self.btn_zoom, 1, 0)
        row.addWidget(self.btn_copy, 1, 1)
        col.addLayout(row)
        self.clear()

    def _pin(self, name: str) -> None:
        if self.frame is not None and 0 <= self.k < len(self.frame):
            value = self.frame.labels[name][self.k]
            if value:
                self.pin.emit(name, value)

    def _copy(self) -> None:
        if self.frame is not None and 0 <= self.k < len(self.frame):
            QtWidgets.QApplication.clipboard().setText(str(int(self.frame.id[self.k])))

    def clear(self) -> None:
        self.set_path(None, -1)

    def set_path(self, frame: Frame | None, k: int) -> None:
        self.frame, self.k = frame, k
        self.picture.set_path(frame, k)
        ok = frame is not None and 0 <= k < len(frame)
        for b in (self.btn_rec, self.btn_app, self.btn_zoom, self.btn_copy):
            b.setEnabled(ok)
        if not ok:
            self.text.setHtml("")
            return
        i = frame.info(k)
        t1 = i["t0_ns"] / 1e9 + (i.get("duration_s") or 0)
        rows = [
            ("id", f"{i['id']}"),
            ("source", i.get("source") or "–"),
            ("machine", i.get("machine") or "–"),
            ("recording", i.get("recording") or "–"),
            ("app", i.get("app") or "–"),
            ("recorded", f"{fmt_time(i['t0_ns'])} → {datetime.fromtimestamp(t1).strftime('%H:%M:%S')}"),
            ("screen", f"{i['screen_w']} × {i['screen_h']}" if i["screen_w"] else "unknown"),
        ]
        for m in METRICS:
            if m.key in i:
                rows.append((m.label, fmt_metric(m.key, i[m.key])))
        if all(key in i for key in ("x0", "y0", "x1", "y1")):
            rows.append(("box", f"{i['x0']:.3f}, {i['y0']:.3f} – {i['x1']:.3f}, {i['y1']:.3f}"))
        if i.get("has_color"):
            rows.append(("colour", "recorded"))
        html = "".join(f"<tr><td style='color:gray;padding-right:8px'>{a}</td><td>{b}</td></tr>" for a, b in rows)
        self.text.setHtml(f"<table cellspacing=0>{html}</table>")


# ------------------------------------------------------------------- window
class _Bridge(QtCore.QObject):
    done = pyqtSignal(int, str, object)  # generation, kind, Frame or Exception


class _Job(QtCore.QRunnable):
    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def run(self) -> None:
        self.fn()


class Window(QtWidgets.QMainWindow):
    def __init__(self, fountain: Fountain, limit: int = 500):
        super().__init__()
        self.fountain = fountain
        self.frame: Frame | None = None
        self.baseline: Frame | None = None
        self.population = 0
        self.assigners: dict[str, SlotAssigner] = {}
        self._gen = 0
        self.pool = QtCore.QThreadPool()
        self.pool.setMaxThreadCount(2)
        self.bridge = _Bridge()
        self.bridge.done.connect(self._on_done)
        self.setWindowTitle("cursor · fountain explorer")

        # ---- query panel, left
        self.panel = QueryPanel(limit)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.panel)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setMinimumWidth(400)
        dock = QtWidgets.QDockWidget("Query")
        dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        dock.setWidget(scroll)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        # ---- canvas, centre
        centre = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(centre)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        bar = QtWidgets.QToolBar()
        bar.setMovable(False)
        bar.setIconSize(QtCore.QSize(16, 16))

        def lab(text: str) -> QtWidgets.QLabel:
            w = QtWidgets.QLabel(text)
            w.setContentsMargins(10, 0, 4, 0)
            return w

        bar.addWidget(lab("View"))
        self.view_mode = QtWidgets.QComboBox()
        self.view_mode.addItem("overlay", "overlay")
        self.view_mode.addItem("grid", "grid")
        self.view_mode.currentIndexChanged.connect(self._view_changed)
        bar.addWidget(self.view_mode)
        bar.addWidget(lab("Colour by"))
        self.color_mode = QtWidgets.QComboBox()
        for key, label in COLOR_MODES:
            self.color_mode.addItem(label, key)
        self.color_mode.currentIndexChanged.connect(self._recolor)
        bar.addWidget(self.color_mode)
        bar.addWidget(lab("Opacity"))
        self.alpha = QtWidgets.QSlider(Qt.Horizontal)
        self.alpha.setRange(15, 255)
        self.alpha.setValue(170)
        self.alpha.setFixedWidth(90)
        self.alpha.valueChanged.connect(lambda v: self.canvas.set_style(alpha=v))
        bar.addWidget(self.alpha)
        bar.addWidget(lab("Width"))
        self.width_spin = QtWidgets.QDoubleSpinBox()
        self.width_spin.setRange(0.3, 8.0)
        self.width_spin.setSingleStep(0.2)
        self.width_spin.setValue(1.0)
        self.width_spin.valueChanged.connect(lambda v: self.canvas.set_style(line_width=v))
        bar.addWidget(self.width_spin)
        bar.addWidget(lab("Tile"))
        self.cell_spin = QtWidgets.QSpinBox()
        self.cell_spin.setRange(40, 600)
        self.cell_spin.setSingleStep(10)
        self.cell_spin.setValue(120)
        self.cell_spin.setSuffix(" px")
        self.cell_spin.valueChanged.connect(lambda v: self.canvas.set_cell(v))
        bar.addWidget(self.cell_spin)
        vbox.addWidget(bar)
        self.canvas = Canvas()
        self.canvas_scroll = QtWidgets.QScrollArea()
        self.canvas_scroll.setWidgetResizable(True)
        self.canvas_scroll.setWidget(self.canvas)
        self.canvas_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        vbox.addWidget(self.canvas_scroll, 1)
        self.setCentralWidget(centre)

        # ---- legend and detail, right
        right = QtWidgets.QWidget()
        rcol = QtWidgets.QVBoxLayout(right)
        rcol.setContentsMargins(8, 8, 8, 0)
        self.legend = Legend()
        rcol.addWidget(self.legend)
        self.detail = DetailView()
        rcol.addWidget(self.detail, 1)
        rdock = QtWidgets.QDockWidget("Path")
        rdock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        rdock.setWidget(right)
        rdock.setMinimumWidth(300)
        self.addDockWidget(Qt.RightDockWidgetArea, rdock)
        self.resizeDocks([dock, rdock], [400, 340], Qt.Horizontal)

        # ---- actions
        tb = QtWidgets.QToolBar("Actions")
        tb.setMovable(False)
        self.addToolBar(tb)

        def action(text: str, shortcut: str | None, slot, tip: str = "") -> QtWidgets.QAction:
            a = QtWidgets.QAction(text, self)
            if shortcut:
                a.setShortcut(QtGui.QKeySequence(shortcut))
                tip = f"{tip} ({shortcut})" if tip else shortcut
            a.setToolTip(tip)
            a.triggered.connect(slot)
            tb.addAction(a)
            return a

        action("Run", "F5", self.run_query, "run the query now")
        action("Reroll", "R", self.panel.new_seed, "new random seed")
        action("Fit", "F", self.canvas.fit, "fit the screen frame")
        action("Grid", "G", self._toggle_grid, "overlay or grid")
        tb.addSeparator()
        action("Copy Python", "Ctrl+Shift+C", self.copy_python, "the QUERY for a composition")
        action("Copy ids", None, self.copy_ids, "ids=[...] of the shown paths")
        action("Save PNG…", "Ctrl+S", self.save_png, "the canvas as an image")
        action("Save pickle…", "Ctrl+Shift+S", self.save_pickle, "the shown paths as a Collection pickle")
        prev_a = QtWidgets.QAction("prev page", self)
        prev_a.setShortcut(QtGui.QKeySequence("PgUp"))
        prev_a.triggered.connect(lambda: self.panel.page(-1))
        next_a = QtWidgets.QAction("next page", self)
        next_a.setShortcut(QtGui.QKeySequence("PgDown"))
        next_a.triggered.connect(lambda: self.panel.page(+1))
        self.addActions([prev_a, next_a])

        # ---- wiring
        self.count_label = QtWidgets.QLabel()
        self.statusBar().addPermanentWidget(self.count_label)
        self.timer = QtCore.QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(350)
        self.timer.timeout.connect(self._auto_run)
        self.panel.changed.connect(self._schedule)
        self.panel.run.connect(self.run_query)
        self.panel.copyPython.connect(self.copy_python)
        self.canvas.hovered.connect(self._hovered)
        self.canvas.selected.connect(self._selected)
        self.canvas.bboxDrawn.connect(self.panel.set_bbox)
        self.detail.pin.connect(self.panel.set_filter)
        self.detail.zoomTo.connect(self._zoom_to)
        self._last_total: int | None = None
        self.panel.show_python(self.panel.state().python())
        self.statusBar().showMessage(f"connecting to {fountain.url}…")

    # ---- plumbing
    def start(self) -> None:
        """Fetch the population sample and run the first query (call once the event loop runs)."""
        self._submit(
            -1, "baseline", lambda: self.fountain.frame(sort="random", seed=0, limit=5000, resample=2, timestamps=False)
        )
        self.run_query()

    def _submit(self, gen: int, kind: str, fn) -> None:
        def work() -> None:
            try:
                res = fn()
            except Exception as e:  # shown in the status bar
                res = e
            self.bridge.done.emit(gen, kind, res)

        self.pool.start(_Job(work))

    def _schedule(self) -> None:
        self.panel.show_python(self.panel.state().python(self._last_total))
        self.timer.start()

    def _auto_run(self) -> None:
        if self.panel.auto.isChecked():
            self.run_query()

    def run_query(self) -> None:
        self.timer.stop()
        self._gen += 1
        gen = self._gen
        kw = self.panel.state().kwargs()
        self.statusBar().showMessage("querying…")
        self._submit(gen, "query", lambda: self.fountain.frame(colors=True, **kw))

    def _on_done(self, gen: int, kind: str, res) -> None:
        if kind == "baseline":
            if isinstance(res, Exception):
                self.statusBar().showMessage(f"no population sample: {res}")
                return
            self.baseline = res
            self.population = res.total
            self.panel.set_lists(res.dicts)
            self.panel.set_baseline(res)
            if self.frame is not None:
                self.panel.set_sample(self.frame)
            self._update_counts()
            return
        if gen != self._gen:
            return
        if isinstance(res, Exception):
            self.statusBar().showMessage(f"query failed: {res}")
            log.warning("query failed: %s", res)
            return
        self.show_frame(res)

    def show_frame(self, frame: Frame) -> None:
        self.frame = frame
        self._last_total = frame.total
        self.canvas.set_frame(frame)
        self._recolor()
        self.panel.set_sample(frame)
        self.panel.show_python(self.panel.state().python(frame.total))
        self.detail.clear()
        self._update_counts()
        self.statusBar().showMessage(
            f"{len(frame):,} paths, {frame.n_points_total:,} points, {frame.took_ms:.0f} ms on the fountain"
        )

    def _update_counts(self) -> None:
        parts = []
        if self.frame is not None:
            parts.append(f"{self.frame.total:,} match")
            parts.append(f"{len(self.frame):,} shown")
        if self.population:
            parts.append(f"{self.population:,} in the fountain")
        self.count_label.setText(" · ".join(parts))

    def _dark(self) -> bool:
        return self.canvas.palette().color(QtGui.QPalette.Base).lightness() < 128

    def _recolor(self) -> None:
        if self.frame is None:
            return
        ink = self.canvas.palette().color(QtGui.QPalette.Text)
        colors, spec = colorize(
            self.frame,
            self.color_mode.currentData(),
            self._dark(),
            self.assigners,
            (ink.red(), ink.green(), ink.blue()),
        )
        self.canvas.set_colors(colors)
        self.legend.set_spec(spec)

    # ---- view
    def _view_changed(self) -> None:
        self.canvas.set_mode(self.view_mode.currentData())

    def _toggle_grid(self) -> None:
        self.view_mode.setCurrentIndex(1 - self.view_mode.currentIndex())

    def _hovered(self, k: int) -> None:
        if self.frame is not None and 0 <= k < len(self.frame):
            self.statusBar().showMessage(path_summary(self.frame, k))
        elif self.frame is not None:
            self.statusBar().clearMessage()

    def _selected(self, k: int) -> None:
        if self.frame is not None and 0 <= k < len(self.frame):
            self.detail.set_path(self.frame, k)
        else:
            self.detail.clear()

    def _zoom_to(self, k: int) -> None:
        if self.view_mode.currentData() != "overlay":
            self.view_mode.setCurrentIndex(0)
        self.canvas.set_selected(k)
        self.canvas.zoom_to(k)

    # ---- actions
    def copy_python(self) -> None:
        QtWidgets.QApplication.clipboard().setText(self.panel.state().python(self._last_total))
        self.statusBar().showMessage("query copied as Python", 3000)

    def copy_ids(self) -> None:
        if self.frame is None:
            return
        QtWidgets.QApplication.clipboard().setText("ids=[" + ", ".join(str(int(i)) for i in self.frame.id) + "]")
        self.statusBar().showMessage(f"{len(self.frame):,} ids copied", 3000)

    def _default_dir(self) -> str:
        try:
            from cursor.data import DataDirHandler

            return DataDirHandler().data_dir.as_posix()
        except Exception:
            return pathlib.Path.home().as_posix()

    def save_png(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save the canvas", f"{self._default_dir()}/explorer.png", "PNG image (*.png)"
        )
        if path:
            self.canvas.grab().save(path, "PNG")
            self.statusBar().showMessage(f"saved {path}", 5000)

    def save_pickle(self) -> None:
        if self.frame is None or len(self.frame) == 0:
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save the shown paths as a Collection pickle",
            f"{self._default_dir()}/fountain_{len(self.frame)}.pickle",
            "pickle (*.pickle)",
        )
        if path:
            pc = self.frame.collection(name="fountain explorer")
            pc.save_pickle(pathlib.Path(path))
            self.statusBar().showMessage(f"saved {len(pc)} paths to {path}", 5000)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--fountain",
        default=None,
        help="fountain URL (default: $CURSOR_FOUNTAIN_URL, config_local.ini or http://127.0.0.1:7777)",
    )
    ap.add_argument("--limit", type=int, default=500, help="paths per query to start with (default 500)")
    ap.add_argument("-v", action="store_true", help="debug logging")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if a.v else logging.INFO, format="%(levelname)s: %(message)s")
    logging.getLogger("httpx").setLevel(logging.DEBUG if a.v else logging.WARNING)
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    fountain = Fountain(a.fountain)
    try:
        fountain.health()
    except FountainError as e:
        log.warning("%s (start it: cd ~/dev/mouse_logger && uv run mouse-logger fountain serve ...)", e)
    w = Window(fountain, a.limit)
    w.resize(1680, 980)
    w.show()
    QtCore.QTimer.singleShot(0, w.start)
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
