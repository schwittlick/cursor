from __future__ import annotations

import base64
import json
import logging
import time
import zlib

import orjson

from cursor.load.decode import MyJsonDecoder, decode_recording
from cursor.load.encode import MyJsonEncoder


class JsonCompressor:
    ZIPJSON_KEY = "base64(zip(o))"

    def json_zip(self, j: dict) -> dict:
        dumped = json.dumps(j, cls=MyJsonEncoder)
        dumped_encoded = dumped.encode("utf-8")
        compressed = zlib.compress(dumped_encoded)
        encoded = {self.ZIPJSON_KEY: base64.b64encode(compressed).decode("ascii")}

        return encoded

    def json_unzip(self, j: dict, insist: bool = True) -> dict:
        try:
            assert j[self.ZIPJSON_KEY]
            assert set(j.keys()) == {self.ZIPJSON_KEY}
        except AssertionError:
            if insist:
                raise RuntimeError("JSON not in the expected format {" + str(self.ZIPJSON_KEY) + ": zipstring}")
            else:
                return j

        try:
            t0 = time.perf_counter()
            b64_bytes = base64.b64decode(j[self.ZIPJSON_KEY])
            raw_bytes = zlib.decompress(b64_bytes)
            t1 = time.perf_counter()
        except zlib.error:
            raise RuntimeError("Could not decode/unzip the contents")

        try:
            t2 = time.perf_counter()
            parsed = orjson.loads(raw_bytes)
            t3 = time.perf_counter()
            result = decode_recording(parsed)
            t4 = time.perf_counter()
        except (TypeError, orjson.JSONDecodeError):
            raise RuntimeError("Could interpret the unzipped contents")

        n_paths = len(result["mouse"])
        n_points = sum(len(p) for p in result["mouse"])
        logging.info(
            f"  {len(raw_bytes) // 1024}KB uncompressed | "
            f"zlib={int((t1 - t0) * 1000)}ms "
            f"orjson={int((t3 - t2) * 1000)}ms "
            f"obj_build={int((t4 - t3) * 1000)}ms | "
            f"{n_paths} paths {n_points} points"
        )

        return result
