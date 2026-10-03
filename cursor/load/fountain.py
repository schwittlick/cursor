"""Client for the mouse_logger data fountain: recorded paths over HTTP, as a Collection.

    from cursor.load.fountain import Fountain
    pc = Fountain().paths(min_points=50, max_points=100, entropy_min=(3.5, 3.5), limit=200)

Needs a running `mouse-logger fountain serve` (see ~/dev/mouse_logger). The URL
is the `url` argument, else $CURSOR_FOUNTAIN_URL, else `fountain_url` under
[cursor] in config_local.ini, else http://127.0.0.1:7777.

Filter keywords mirror the Filter classes: entropy_min=(3.5, 3.5) means
EntropyMinFilter(3.5, 3.5), entropy_dc=(5, 10) means
DirectionChangeEntropyFilter(5, 10), min_points=50 means MinPointCountFilter(50).
The server filters on the same formulas Path computes, so the Collection that
comes back passes those filters again.
"""

from __future__ import annotations

import configparser
import json
import os
import pathlib
from typing import Any, Iterator

import httpx
import msgpack
import numpy as np

from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property

DEFAULT_URL = "http://127.0.0.1:7777"
DTYPES = {"offsets": "<u4", "x": "<f4", "y": "<f4", "t": "<i4", "rgb": "u1", "id": "<i8", "t0_ns": "<i8",
          "screen_w": "<u2", "screen_h": "<u2", "has_color": "u1", "open": "u1", "source": "u1",
          "machine": "<u2", "app": "<u2", "recording": "<u2", "n_points": "<u4"}


class FountainError(RuntimeError):
    pass


def _config_url() -> str | None:
    ini = pathlib.Path(__file__).resolve().parent.parent.parent / "config_local.ini"
    if not ini.exists():
        return None
    cfg = configparser.ConfigParser()
    cfg.read(ini)
    return cfg.get("cursor", "fountain_url", fallback=None) or None


def _pair(v) -> tuple:
    if v is None:
        return None, None
    if isinstance(v, (int, float)):
        return v, None
    lo, hi = v
    return lo, hi


class Fountain:
    def __init__(self, url: str | None = None, timeout: float = 60.0):
        self.url = (url or os.environ.get("CURSOR_FOUNTAIN_URL") or _config_url() or DEFAULT_URL).rstrip("/")
        self._client = httpx.Client(base_url=self.url, timeout=timeout)

    # ---- plumbing
    def _get(self, path: str, params: dict | None = None, binary: bool = False) -> Any | None:
        """The decoded body, or None on 204."""
        accept = "application/msgpack" if binary else "application/json"
        try:
            r = self._client.get(path, params=params, headers={"Accept": accept})
        except httpx.HTTPError as e:
            raise FountainError(f"no fountain at {self.url}: {e}") from None
        if r.status_code == 503:
            raise FountainError(f"the fountain is still starting: {r.text}")
        if r.status_code == 204:
            return None
        if r.status_code >= 400:
            raise FountainError(f"{r.status_code} from {path}: {r.text}")
        return msgpack.unpackb(r.content, raw=False) if binary else r.json()

    def _require(self, path: str, params: dict | None = None, binary: bool = False) -> Any:
        """Like _get, but an empty response is an error."""
        d = self._get(path, params, binary)
        if d is None:
            raise FountainError(f"empty response from {path}")
        return d

    @staticmethod
    def _params(*, min_points=None, max_points=None, entropy_min=None, entropy_max=None, entropy_dc=None,
                distance_min=None, distance_max=None, aspect=None, variation_x=None, variation_y=None,
                duration=None, bbox=None, bbox_mode=None, since=None, until=None, source=None, machine=None,
                app=None, recording=None, has_color=None, ids=None, include_open=False, sort=None,
                order="asc", seed=None, limit=200, offset=0, resample=None) -> dict:
        p: dict = {}
        if min_points is not None:
            p["min_points"] = int(min_points)
        if max_points is not None:
            p["max_points"] = int(max_points)
        if entropy_min is not None:
            p["entropy_x_min"], p["entropy_y_min"] = entropy_min
        if entropy_max is not None:
            p["entropy_x_max"], p["entropy_y_max"] = entropy_max
        for name, val in (("entropy_dc", entropy_dc), ("aspect", aspect), ("variation_x", variation_x),
                          ("variation_y", variation_y), ("duration", duration)):
            lo, hi = _pair(val)
            if lo is not None:
                p[f"{name}_min"] = lo
            if hi is not None:
                p[f"{name}_max"] = hi
        if distance_min is not None:
            p["distance_min"] = distance_min
        if distance_max is not None:
            p["distance_max"] = distance_max
        if bbox is not None:
            b = (bbox.x, bbox.y, bbox.x2, bbox.y2) if isinstance(bbox, BoundingBox) else tuple(bbox)
            p["bbox"] = ",".join(str(float(v)) for v in b)
        if bbox_mode:
            p["bbox_mode"] = bbox_mode
        if since is not None:
            p["since"] = since
        if until is not None:
            p["until"] = until
        for name, val in (("source", source), ("machine", machine), ("app", app), ("recording", recording)):
            if val:
                p[name] = val if isinstance(val, str) else ",".join(val)
        if has_color is not None:
            p["has_color"] = int(bool(has_color))
        if ids is not None:
            p["ids"] = ",".join(str(int(i)) for i in ids)
        if include_open:
            p["include_open"] = 1
        if sort:
            p["sort"] = sort
        if order != "asc":
            p["order"] = order
        if seed is not None:
            p["seed"] = int(seed)
        p["limit"] = int(limit)
        if offset:
            p["offset"] = int(offset)
        if resample:
            p["resample"] = int(resample)
        return p

    # ---- queries
    def health(self) -> dict:
        return self._require("/health")

    def stats(self) -> dict:
        return self._require("/stats")

    def sources(self) -> list[dict]:
        return self._require("/sources")

    def recordings(self) -> list[str]:
        """Names usable as recording=...: legacy file stems and machine/day for the recorder."""
        return sorted({s["recording"] for s in self.sources() if s.get("recording")})

    def position(self) -> dict | None:
        """The live cursor: x, y (normalised), px, py, t_ns, age_ms, app; None if nothing was seen."""
        return self._get("/live/position")

    def count(self, **filters) -> int:
        params = self._params(**filters)
        params.pop("limit", None)
        return int(self._require("/paths/count", params)["total"])

    def paths(self, *, timestamps: bool = True, colors: bool = False, meta: bool = True, **filters) -> Collection:
        """Matching paths as a Collection. Each Path keeps the server's metadata in properties["fountain"]."""
        params = self._params(**filters)
        params["fields"] = "xytc" if colors else ("xyt" if timestamps else "xy")
        params["meta"] = 1 if meta else 0
        d = self._require("/paths", params, binary=True)
        return decode_collection(d, name="fountain " + " ".join(f"{k}={v}" for k, v in params.items()))

    def path(self, path_id: int, **kw) -> Path:
        pc = self.paths(ids=[path_id], include_open=True, limit=1, **kw)
        if len(pc) == 0:
            raise FountainError(f"no path with id {path_id}")
        return pc.paths[0]

    def live(self, hz: float = 60, events=("motion",), timeout: float | None = None) -> Iterator[dict]:
        """Live events from the recorder, e.g. {"e": "motion", "t": ns, "x": .., "y": .., "px": .., "py": ..}."""
        try:
            from websockets.sync.client import connect
        except ImportError:
            raise FountainError("pip install websockets for the live stream") from None
        ws_url = ("ws" + self.url[4:]) + f"/live?hz={hz}&events={','.join(events)}&format=msgpack"
        with connect(ws_url) as ws:
            while True:
                msg = ws.recv(timeout=timeout)
                yield msgpack.unpackb(msg, raw=False) if isinstance(msg, bytes) else json.loads(msg)


def decode_collection(d: dict, name: str = "fountain") -> Collection:
    """Turn a /paths response (msgpack document) into a Collection of Paths."""
    n = int(d["n"])

    def arr(v, dtype: str) -> np.ndarray:
        return np.frombuffer(v, dtype) if isinstance(v, (bytes, bytearray)) else np.asarray(v)

    def opt(key: str) -> np.ndarray | None:
        """A column the server may leave out (t, rgb)."""
        v = d.get(key)
        return None if v is None else arr(v, DTYPES[key])

    def col(key: str) -> np.ndarray:
        """A column the server always sends."""
        v = opt(key)
        if v is None:
            raise FountainError(f"/paths response has no {key!r} column")
        return v

    off = col("offsets").astype(np.int64)
    x, y = col("x"), col("y")
    t = opt("t")
    rgb = opt("rgb")
    ids, t0 = col("id"), col("t0_ns")
    has_color, is_open = col("has_color"), col("open")
    codes = {k: col(k) for k in ("source", "machine", "app", "recording")}
    dicts = d.get("dict", {})
    metrics = {k: arr(v, "<u4" if k == "n_points" else "<f8") for k, v in d.get("metrics", {}).items()}
    screen_w, screen_h = col("screen_w"), col("screen_h")

    xl, yl = x.tolist(), y.tolist()
    tl = None
    if t is not None and n:
        pid = np.repeat(np.arange(n), np.diff(off))
        tl = (t0[pid] / 1e9 + t / 1000.0).tolist()
    rgbl = rgb.reshape(-1, 3).tolist() if rgb is not None else None

    pc = Collection(name=name)
    for k in range(n):
        s, e = int(off[k]), int(off[k + 1])
        if tl is not None:
            verts = [Position(a, b, c) for a, b, c in zip(xl[s:e], yl[s:e], tl[s:e])]
        else:
            verts = [Position(a, b) for a, b in zip(xl[s:e], yl[s:e])]
        if rgbl is not None and has_color[k]:
            for v, c in zip(verts, rgbl[s:e]):
                v.properties[Property.COLOR] = tuple(c)
        info = {
            "id": int(ids[k]), "t0_ns": int(t0[k]), "open": bool(is_open[k]), "has_color": bool(has_color[k]),
            "screen_w": int(screen_w[k]), "screen_h": int(screen_h[k]),
            **{key: dicts.get(key, [None] * 65536)[int(codes[key][k])] for key in codes},
            **{mk: (int(mv[k]) if mk == "n_points" else float(mv[k])) for mk, mv in metrics.items()},
        }
        p = Path(verts)
        p.properties["fountain"] = info
        pc.add(p)
    return pc
