from __future__ import annotations

import json
import logging
import pathlib
import time
from functools import reduce

import pyarrow as pa
import pyarrow.feather as feather

from cursor.collection import Collection
from cursor.load import KeyPress
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property
from cursor.timer import Timer

# Arrow schema for mouse recording data.
# Each row is one position point. Path membership is encoded by path_id.
MOUSE_SCHEMA = pa.schema(
    [
        pa.field("path_id", pa.int32()),
        pa.field("x", pa.float64()),
        pa.field("y", pa.float64()),
        pa.field("ts", pa.float64()),
        pa.field("r", pa.uint8()),
        pa.field("g", pa.uint8()),
        pa.field("b", pa.uint8()),
        pa.field("has_color", pa.bool_()),
    ],
    metadata={
        "recording_ts": "",  # filled per recording
        "keys": "",  # JSON-serialised list of [key, ts, is_down] triples
    },
)


def collection_to_table(collection: Collection, keys: list[KeyPress]) -> pa.Table:
    path_ids: list[int] = []
    xs: list[float] = []
    ys: list[float] = []
    tss: list[float] = []
    rs: list[int] = []
    gs: list[int] = []
    bs: list[int] = []
    has_colors: list[bool] = []

    for path_id, path in enumerate(collection.get_all()):
        for pos in path.vertices:
            path_ids.append(path_id)
            xs.append(pos.x)
            ys.append(pos.y)
            tss.append(pos.timestamp)
            color = pos.properties.get(Property.COLOR)
            if color is not None:
                rs.append(int(color[0]))
                gs.append(int(color[1]))
                bs.append(int(color[2]))
                has_colors.append(True)
            else:
                rs.append(0)
                gs.append(0)
                bs.append(0)
                has_colors.append(False)

    keys_serialized = json.dumps(
        [[k.key, k.timestamp, k.is_down] for k in keys]
    )
    metadata = {
        "recording_ts": str(collection._timestamp),
        "keys": keys_serialized,
    }

    return pa.table(
        {
            "path_id": pa.array(path_ids, type=pa.int32()),
            "x": pa.array(xs, type=pa.float64()),
            "y": pa.array(ys, type=pa.float64()),
            "ts": pa.array(tss, type=pa.float64()),
            "r": pa.array(rs, type=pa.uint8()),
            "g": pa.array(gs, type=pa.uint8()),
            "b": pa.array(bs, type=pa.uint8()),
            "has_color": pa.array(has_colors, type=pa.bool_()),
        },
        schema=MOUSE_SCHEMA.with_metadata(metadata),
    )


def table_to_collection(table: pa.Table) -> tuple[Collection, list[KeyPress]]:
    meta = table.schema.metadata or {}
    recording_ts = float(meta.get(b"recording_ts", b"0").decode())
    keys_raw = json.loads(meta.get(b"keys", b"[]").decode())

    keys = [KeyPress(k[0], k[1], bool(k[2])) for k in keys_raw]

    collection = Collection(recording_ts)
    current_path_id = None
    current_path = None

    path_ids = table.column("path_id").to_pylist()
    xs = table.column("x").to_pylist()
    ys = table.column("y").to_pylist()
    tss = table.column("ts").to_pylist()
    rs = table.column("r").to_pylist()
    gs = table.column("g").to_pylist()
    bs = table.column("b").to_pylist()
    has_colors = table.column("has_color").to_pylist()

    for i in range(len(path_ids)):
        pid = path_ids[i]
        if pid != current_path_id:
            if current_path is not None:
                collection.add(current_path)
            current_path = Path()
            current_path_id = pid

        pos = Position(xs[i], ys[i], tss[i])
        if has_colors[i]:
            pos.properties[Property.COLOR] = (rs[i], gs[i], bs[i])
        current_path.add_position(pos)

    if current_path is not None:
        collection.add(current_path)

    return collection, keys


def write_recording(
    collection: Collection,
    keys: list[KeyPress],
    output_path: pathlib.Path,
) -> None:
    table = collection_to_table(collection, keys)
    feather.write_feather(table, output_path, compression="lz4")


def read_recording(path: pathlib.Path) -> tuple[Collection, list[KeyPress]]:
    table = feather.read_table(path)
    return table_to_collection(table)


class ArrowLoader:
    def __init__(
        self,
        directory: pathlib.Path | None = None,
        limit_files: int | list[str] | None = None,
        load_keys: bool = True,
    ):
        self._recordings: list[Collection] = []
        self._keyboard_recordings: list[KeyPress] = []

        if directory is not None:
            self.load_all(directory, limit_files=limit_files, load_keys=load_keys)

    def load_all(
        self,
        directory: pathlib.Path,
        limit_files: int | list[str] | None = None,
        load_keys: bool = True,
    ) -> None:
        t = Timer()
        t.start()
        all_files = [f for f in directory.glob("*.feather") if f.is_file()]

        if limit_files and type(limit_files) is int:
            all_files = all_files[:limit_files]
        elif limit_files and type(limit_files) is list:
            all_files = [f for f in all_files if f.stem in limit_files]

        logging.info(f"Loading {len(all_files)} feather files...")

        for f in all_files:
            t0 = time.perf_counter()
            collection, keys = read_recording(f)
            t1 = time.perf_counter()
            logging.info(
                f"  {f.stem}: {len(collection)} paths in {int((t1 - t0) * 1000)}ms"
            )
            collection.clean()
            self._recordings.append(collection)
            if load_keys:
                self._keyboard_recordings.extend(keys)

        total_paths = sum(len(c) for c in self._recordings)
        logging.info(
            f"Loaded {total_paths} paths from {len(self._recordings)} recordings "
            f"in {round(t.elapsed() * 1000)}ms"
        )

    def load_file(self, path: pathlib.Path, load_keys: bool = True) -> None:
        collection, keys = read_recording(path)
        collection.clean()
        self._recordings.append(collection)
        if load_keys:
            self._keyboard_recordings.extend(keys)

    def all_collections(self) -> list[Collection]:
        return list(self._recordings)

    def all_paths(self) -> Collection:
        return reduce(lambda a, b: a + b, self._recordings)

    def single(self, index: int) -> Collection:
        if index > len(self._recordings) - 1:
            raise IndexError("Specified index too high. (> " + str(len(self._recordings) - 1) + ")")
        return self._recordings[index]

    def keys(self) -> list[KeyPress]:
        return self._keyboard_recordings

    def __len__(self) -> int:
        return len(self._recordings)
