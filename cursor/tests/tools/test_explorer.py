"""The fountain explorer: query state, colouring, hit tests, and the widgets painted offscreen."""

import os
import time

import numpy as np
import pytest

pytest.importorskip("PyQt5")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtCore, QtTest, QtWidgets  # noqa: E402

from cursor.load.fountain import Fountain, Frame  # noqa: E402
from cursor.tools import explorer as ex  # noqa: E402


def synthetic_frame(n: int = 40, seed: int = 0) -> Frame:
    """n random walks with every column the fountain sends."""
    rng = np.random.default_rng(seed)
    counts = rng.integers(2, 40, n)
    offsets = np.concatenate([[0], np.cumsum(counts)]).astype(np.int64)
    m = int(offsets[-1])
    x = np.empty(m, np.float32)
    y = np.empty(m, np.float32)
    t = np.empty(m, np.int32)
    distance = np.empty(n)
    for k in range(n):
        s, e = int(offsets[k]), int(offsets[k + 1])
        start = rng.random(2) * 0.8 + 0.1
        steps = rng.normal(0, 0.01, (e - s, 2)).cumsum(axis=0)
        x[s:e] = start[0] + steps[:, 0]
        y[s:e] = start[1] + steps[:, 1]
        t[s:e] = np.arange(e - s) * 16
        distance[k] = np.hypot(np.diff(x[s:e]), np.diff(y[s:e])).sum()
    app_names = ["code", "kitty", "dota2", "firefox", "steam", "chromium", "everdo", "cs2", "zoom"]
    apps = np.array(app_names, dtype=object)[rng.integers(0, len(app_names), n)]
    x0 = np.array([x[offsets[k] : offsets[k + 1]].min() for k in range(n)], dtype=np.float64)
    x1 = np.array([x[offsets[k] : offsets[k + 1]].max() for k in range(n)], dtype=np.float64)
    y0 = np.array([y[offsets[k] : offsets[k + 1]].min() for k in range(n)], dtype=np.float64)
    y1 = np.array([y[offsets[k] : offsets[k + 1]].max() for k in range(n)], dtype=np.float64)
    with np.errstate(divide="ignore"):
        aspect = np.where(x1 > x0, (y1 - y0) / np.maximum(x1 - x0, 1e-12), np.inf)
    return Frame(
        total=n * 10,
        took_ms=1.0,
        offsets=offsets,
        x=x,
        y=y,
        t=t,
        rgb=None,
        id=np.arange(n, dtype=np.int64),
        t0_ns=(1.7e18 + np.arange(n) * 6e10).astype(np.int64),
        screen_w=np.full(n, 2560, np.uint16),
        screen_h=np.full(n, 1440, np.uint16),
        has_color=np.zeros(n, bool),
        open=np.zeros(n, bool),
        labels={
            "source": np.array(["legacy", "mouse_logger"], dtype=object)[np.arange(n) % 2],
            "machine": np.array(["", "lush"], dtype=object)[np.arange(n) % 2],
            "app": apps,
            "recording": np.array([f"rec_{k % 5}" for k in range(n)], dtype=object),
        },
        metrics={
            "n_points": counts.astype(np.uint32),
            "distance": distance,
            "duration_s": (counts - 1) * 16 / 1000.0,
            "x0": x0,
            "y0": y0,
            "x1": x1,
            "y1": y1,
            "aspect": aspect,
            "entropy_x": rng.uniform(0, 5, n),
            "entropy_y": rng.uniform(0, 5, n),
            "entropy_dc": rng.uniform(0, 5, n),
            "variation_x": rng.uniform(0, 1, n),
            "variation_y": rng.uniform(0, 1, n),
        },
        dicts={
            "source": ["legacy", "mouse_logger"],
            "machine": ["", "lush"],
            "app": sorted(set(app_names)),
            "recording": [f"rec_{k}" for k in range(5)],
        },
    )


@pytest.fixture(scope="module")
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def frame() -> Frame:
    return synthetic_frame()


def test_query_state_speaks_fountain():
    s = ex.QueryState(
        ranges={
            "n_points": (50, 300),
            "entropy_x": (3.5, None),
            "entropy_dc": (None, 4.0),
            "aspect": (0.5, 2.0),
            "distance": (0.1, None),
            "duration_s": (1.0, None),
        },
        bbox=(0.1, 0.1, 0.6, 0.9),
        bbox_mode="intersects",
        app=["dota2"],
        recording=["a", "b"],
        sort="random",
        seed=7,
        limit=100,
        offset=200,
    )
    kw = s.filters()
    assert kw == {
        "min_points": 50,
        "max_points": 300,
        "entropy_min": (3.5, None),
        "distance_min": 0.1,
        "entropy_dc": (None, 4.0),
        "aspect": (0.5, 2.0),
        "duration": 1.0,
        "bbox": (0.1, 0.1, 0.6, 0.9),
        "bbox_mode": "intersects",
        "app": "dota2",
        "recording": ["a", "b"],
        "sort": "random",
        "seed": 7,
    }
    # the snippet is Python that rebuilds the same dict, and the client accepts it
    ns: dict = {}
    exec(s.python(5).split("\npc = ")[0], ns)
    assert ns["QUERY"] == kw
    assert s.python(5).endswith("pc = Fountain().paths(limit=100, offset=200, **QUERY)  # 5 matching")
    p = Fountain._params(**s.kwargs())
    assert p["entropy_x_min"] == 3.5 and "entropy_y_min" not in p
    assert p["entropy_dc_max"] == 4.0 and "entropy_dc_min" not in p
    assert p["duration_min"] == 1.0 and p["offset"] == 200 and p["limit"] == 100
    # order only matters for a sorted, non-random query; sources only when exactly one is picked
    assert "order" not in ex.QueryState(sort="random", order="desc").filters()
    assert ex.QueryState(sort="distance", order="desc").filters() == {"sort": "distance", "order": "desc"}
    assert ex.QueryState(source=["legacy"]).filters() == {"source": "legacy"}
    assert ex.QueryState(source=["legacy", "mouse_logger"]).filters() == {}


def test_slot_assigner_keeps_colours():
    a = ex.SlotAssigner(3)
    assert a.assign(["b", "a", "c", "d"]) == {"b": 0, "a": 1, "c": 2}
    # c left, d takes its slot, a and b keep theirs although their ranks changed
    assert a.assign(["a", "d", "b"]) == {"b": 0, "a": 1, "d": 2}


def test_colorize_every_mode(frame):
    for mode in [k for k, _ in ex.COLOR_MODES]:
        colors, spec = ex.colorize(frame, mode, False, {}, (0, 0, 0))
        assert colors.shape == (len(frame), 3) and colors.dtype == np.uint8, mode
        assert spec["kind"] in ("none", "categorical", "sequential")
    colors, spec = ex.colorize(frame, "app", False, {}, (0, 0, 0))
    assert spec["kind"] == "categorical"
    assert sum(c for _, _, c in spec["entries"]) == len(frame)
    assert len([e for e in spec["entries"] if e[0] != "other"]) <= ex.N_SLOTS
    dark, spec = ex.colorize(frame, "entropy_x", True, {}, (255, 255, 255))
    assert spec["kind"] == "sequential" and spec["stops"] == ex.sequential_stops(True)
    assert spec["stops"][0] == "#184f95" and ex.sequential_stops(False)[0] == "#86b6ef"
    single, _ = ex.colorize(frame, "single", False, {}, (1, 2, 3))
    assert (single == (1, 2, 3)).all()


def test_nearest_path_and_screen_size(frame):
    offsets = np.array([0, 3, 6])
    wx = np.array([0.0, 10.0, 20.0, 100.0, 110.0, 120.0])
    wy = np.zeros(6)
    assert ex.nearest_path(wx, wy, offsets, 104, 2) == 1
    assert ex.nearest_path(wx, wy, offsets, 21, 1) == 0
    assert ex.nearest_path(wx, wy, offsets, 60, 0) == -1
    assert ex.nearest_path(np.zeros(0), np.zeros(0), np.array([0]), 0, 0) == -1
    assert ex.screen_size(frame) == (2560, 1440)
    assert ex.screen_size(None) == (1920, 1080)


class _StubFountain:
    """Answers every query with the same frame, from the worker thread like the real client."""

    url = "stub://fountain"

    def __init__(self, frame: Frame):
        self._frame = frame
        self.calls: list[dict] = []

    def frame(self, **kw) -> Frame:
        self.calls.append(kw)
        return self._frame


def _wait(cond, seconds: float = 10.0) -> None:
    t0 = time.time()
    while not cond() and time.time() - t0 < seconds:
        QtTest.QTest.qWait(20)
    assert cond()


def _ink_pixels(widget: QtWidgets.QWidget) -> int:
    img = widget.grab().toImage()
    base = widget.palette().color(widget.backgroundRole()).rgb()
    return sum(1 for yy in range(0, img.height(), 4) for xx in range(0, img.width(), 4) if img.pixel(xx, yy) != base)


def test_window_offscreen(app, frame):
    stub = _StubFountain(frame)
    w = ex.Window(stub, limit=10)
    w.resize(1400, 900)
    w.show()
    w.start()
    _wait(lambda: w.frame is not None and w.baseline is not None)
    assert len(w.frame) == len(frame) and w.population == frame.total
    assert any(c.get("resample") == 2 for c in stub.calls)  # the population sample
    assert w.panel.rows["entropy_x"].hist.domain is not None
    assert w.panel.app.count() == len(frame.dicts["app"]) + 1
    assert "match" in w.count_label.text()

    # overlay: something is drawn, the first point of path 0 hits path 0, the status line describes it
    c = w.canvas
    c._render()
    assert _ink_pixels(c) > 0
    wx, wy = c._wxy
    pos = QtCore.QPoint(int(round(wx[0])), int(round(wy[0])))
    assert c._hit(pos) == 0
    w._hovered(0)
    assert w.statusBar().currentMessage().startswith("#0 ·")
    w._selected(0)
    assert "rec_0" in w.detail.text.toPlainText()
    c.zoom_to(0)
    assert c.zoom > 1.0
    c.fit()
    assert c.zoom == 1.0 and (c.cx, c.cy) == (0.5, 0.5)

    # every colour mode paints and describes itself
    for i in range(w.color_mode.count()):
        w.color_mode.setCurrentIndex(i)
        assert w.legend.spec["kind"] in ("none", "categorical", "sequential")
    w.color_mode.setCurrentIndex(0)

    # grid: the canvas grows to hold every tile and paints
    w.view_mode.setCurrentIndex(1)
    QtTest.QTest.qWait(50)
    assert c.minimumHeight() >= c.cell * (len(frame) // c._cols())
    assert _ink_pixels(c) > 0
    assert c._tile_at(QtCore.QPoint(c.GRID_MARGIN + 5, c.GRID_MARGIN + 5)) == 0
    w.view_mode.setCurrentIndex(0)

    # the panel feeds the query: a histogram drag, a box from the canvas, paging
    row = w.panel.rows["distance"]
    row.hist.rangeChanged.emit(0.2, None)
    assert row.value() == (0.2, None)
    assert w.panel.state().filters()["distance_min"] == 0.2
    assert "distance_min=0.2" in w.panel.snippet.toPlainText()
    w.panel.rows["n_points"].hist.rangeChanged.emit(9.6, 20.2)
    assert w.panel.rows["n_points"].value() == (9, 21)
    w.panel.set_bbox((0.1, 0.2, 0.3, 0.4))
    assert w.panel.state().bbox == (0.1, 0.2, 0.3, 0.4)
    w.panel.set_bbox(None)
    assert w.panel.state().bbox is None
    w.panel.page(+1)
    assert w.panel.state().offset == 10
    w.panel.set_filter("recording", "rec_3")
    assert w.panel.state().recording == ["rec_3"] and w.panel.state().offset == 0
    w.panel.reset()
    assert w.panel.state().filters() == {"sort": "random", "seed": w.panel.seed.value()}

    # an explicit run goes through the worker and lands
    before = len(stub.calls)
    w.run_query()
    _wait(lambda: len(stub.calls) > before and w.statusBar().currentMessage() != "querying…")
    assert "paths" in w.statusBar().currentMessage()
    w.timer.stop()
    w.pool.waitForDone(5000)
    w.close()
