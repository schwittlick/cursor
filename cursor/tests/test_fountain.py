"""The fountain client: decoding, and parity with the file loader when a fountain is running."""

import os
import pathlib

import msgpack
import numpy as np
import pytest

from cursor.filter import (DirectionChangeEntropyFilter, EntropyMaxFilter, EntropyMinFilter, MaxPointCountFilter,
                           MinPointCountFilter)
from cursor.load.fountain import Fountain, FountainError, decode_collection
from cursor.properties import Property


def canned_document():
    """What the server sends for two paths, built the way wire.document does it."""
    x = np.array([0.1, 0.2, 0.3, 0.5, 0.5, 0.6], dtype="<f4")
    y = np.array([0.1, 0.1, 0.2, 0.5, 0.6, 0.6], dtype="<f4")
    return {
        "v": 1, "coord": "norm", "took_ms": 0.1, "total": 2, "n": 2, "m": 6,
        "offsets": np.array([0, 3, 6], dtype="<u4").tobytes(), "x": x.tobytes(), "y": y.tobytes(),
        "t": np.array([0, 10, 20, 0, 1000, 2000], dtype="<i4").tobytes(),
        "rgb": np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype="u1").tobytes(),
        "id": np.array([7 << 32 | 0, 7 << 32 | 1], dtype="<i8").tobytes(),
        "t0_ns": np.array([1_700_000_000 * 10**9, 1_700_000_100 * 10**9], dtype="<i8").tobytes(),
        "screen_w": np.array([2560, 0], dtype="<u2").tobytes(), "screen_h": np.array([1440, 0], dtype="<u2").tobytes(),
        "has_color": np.array([1, 0], dtype="u1").tobytes(), "open": np.array([0, 0], dtype="u1").tobytes(),
        "source": np.array([1, 0], dtype="u1").tobytes(), "machine": np.array([1, 0], dtype="<u2").tobytes(),
        "app": np.array([2, 0], dtype="<u2").tobytes(), "recording": np.array([0, 1], dtype="<u2").tobytes(),
        "dict": {"source": ["legacy", "mouse_logger"], "machine": ["", "lush"], "app": ["", "kitty", "firefox"],
                 "recording": ["lush/2026-01-01", "1700000100.0_old"]},
        "metrics": {"n_points": np.array([3, 3], dtype="<u4").tobytes(),
                    "distance": np.array([0.2414, 0.2], dtype="<f8").tobytes()},
    }


def test_decode_collection():
    pc = decode_collection(msgpack.unpackb(msgpack.packb(canned_document(), use_bin_type=True), raw=False))
    assert len(pc) == 2 and [len(p) for p in pc] == [3, 3]
    p0, p1 = pc[0], pc[1]
    assert (p0[0].x, p0[0].y) == (pytest.approx(0.1), pytest.approx(0.1))
    assert p0[1].timestamp == pytest.approx(1_700_000_000.01) and p1[2].timestamp == pytest.approx(1_700_000_102.0)
    assert p0[1].properties[Property.COLOR] == (4, 5, 6) and Property.COLOR not in p1[0].properties
    f0, f1 = p0.properties["fountain"], p1.properties["fountain"]
    assert f0["id"] == 7 << 32 and f0["source"] == "mouse_logger" and f0["machine"] == "lush" and f0["app"] == "firefox"
    assert f0["recording"] == "lush/2026-01-01" and f1["recording"] == "1700000100.0_old" and f1["source"] == "legacy"
    assert f0["screen_w"] == 2560 and f1["screen_w"] == 0 and f0["n_points"] == 3 and f0["distance"] == 0.2414
    assert p0.distance == pytest.approx(0.2414, abs=1e-4)


def test_params_mirror_filters():
    p = Fountain._params(min_points=50, max_points=100, entropy_min=(3.5, 4.0), entropy_dc=(5, 10), aspect=0.5,
                         bbox=(0, 0, 1, 1), app=["kitty", "code"], sort="distance", order="desc", seed=3, limit=0)
    assert p == {"min_points": 50, "max_points": 100, "entropy_x_min": 3.5, "entropy_y_min": 4.0,
                 "entropy_dc_min": 5, "entropy_dc_max": 10, "aspect_min": 0.5, "bbox": "0.0,0.0,1.0,1.0",
                 "app": "kitty,code", "sort": "distance", "order": "desc", "seed": 3, "limit": 0}


def _fountain_or_skip() -> Fountain:
    f = Fountain()
    try:
        if not f.health().get("ready"):
            pytest.skip("fountain not ready")
    except FountainError as e:
        pytest.skip(str(e))
    return f


def _recordings_dir() -> pathlib.Path:
    d = pathlib.Path(os.environ.get("CURSOR_RECORDINGS", "~/dev/cursor/data/cursor-recordings")).expanduser()
    if not d.is_dir():
        pytest.skip(f"no recordings at {d}")
    return d


def test_parity_with_file_loader():
    """The fountain's paths and metrics equal what Loader + Path compute on the same recording."""
    from cursor.load.loader import Loader

    f = _fountain_or_skip()
    recs = _recordings_dir()
    legacy = [s for s in f.sources() if s["kind"] == "legacy" and 100 < s["paths"] < 3000 and not s.get("error")]
    if not legacy:
        pytest.skip("no small legacy recording served")
    stem = sorted(legacy, key=lambda s: s["paths"])[0]["recording"]
    if not (recs / f"{stem}.json").exists():
        pytest.skip(f"{stem}.json not in {recs}")

    loader = Loader(directory=recs, limit_files=[stem])
    mine = loader.all_paths()
    theirs = f.paths(recording=stem, limit=0)
    assert len(mine) == len(theirs)

    # per-path: same points, and cursor's own metrics on the delivered paths equal the server's
    max_dc_diff = 0.0
    for a, b in zip(mine, theirs):
        assert len(a) == len(b)
        assert a[0].x == pytest.approx(b[0].x, abs=1e-6) and a[-1].y == pytest.approx(b[-1].y, abs=1e-6)
        m = b.properties["fountain"]
        assert b.distance == pytest.approx(m["distance"], abs=1e-9)
        assert b.entropy_x == pytest.approx(m["entropy_x"], abs=1e-9)
        assert b.entropy_y == pytest.approx(m["entropy_y"], abs=1e-9)
        assert b.entropy_direction_changes == pytest.approx(m["entropy_dc"], abs=1e-9)
        assert b.variation_x == pytest.approx(m["variation_x"], abs=1e-9)
        assert b.aspect_ratio() == pytest.approx(m["aspect"], abs=1e-9) or (abs(m["aspect"]) == float("inf"))
        # against the original float64 decode: identical except rare float32 collisions
        assert a.entropy_x == pytest.approx(m["entropy_x"], abs=1e-6)
        max_dc_diff = max(max_dc_diff, abs(a.entropy_direction_changes - m["entropy_dc"]))
    assert max_dc_diff < 0.05

    # the composition filter chains agree with server-side counts
    chains = [
        ([MinPointCountFilter(50), MaxPointCountFilter(100), EntropyMinFilter(3.5, 3.5)],
         dict(min_points=50, max_points=100, entropy_min=(3.5, 3.5))),
        ([EntropyMaxFilter(2.0, 2.0)], dict(entropy_max=(2.0, 2.0))),
        ([DirectionChangeEntropyFilter(5, 10)], dict(entropy_dc=(5, 10))),
    ]
    for filters, kw in chains:
        pc = theirs
        for flt in filters:
            pc = pc.filtered(flt)
        n_server = f.count(recording=stem, **kw)
        assert len(pc) == n_server, (kw, len(pc), n_server)
