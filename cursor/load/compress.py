from __future__ import annotations

import base64
import json
import zlib

from cursor.timer import timing
from cursor.load.decode import MyJsonDecoder
from cursor.load.encode import MyJsonEncoder


class JsonCompressor:
    ZIPJSON_KEY = "base64(zip(o))"

    def json_zip(self, j: dict) -> dict:
        dumped = json.dumps(j, cls=MyJsonEncoder)
        dumped_encoded = dumped.encode("utf-8")
        compressed = zlib.compress(dumped_encoded)
        encoded = {self.ZIPJSON_KEY: base64.b64encode(compressed).decode("ascii")}

        return encoded

    @timing
    def json_unzip(self, j: dict, insist: bool = True) -> dict:
        try:
            assert j[self.ZIPJSON_KEY]
            assert set(j.keys()) == {self.ZIPJSON_KEY}
        except AssertionError:
            if insist:
                raise RuntimeError(
                    "JSON not in the expected format {"
                    + str(self.ZIPJSON_KEY)
                    + ": zipstring}"
                )
            else:
                return j

        try:
            decoded = base64.b64decode(j[self.ZIPJSON_KEY])
            decompressed = zlib.decompress(decoded)
        except zlib.error:
            raise RuntimeError("Could not decode/unzip the contents")

        try:
            print(decompressed)
            decompressed = json.loads(decompressed, cls=MyJsonDecoder)

        except TypeError and json.JSONDecodeError:
            raise RuntimeError("Could interpret the unzipped contents")

        return decompressed

