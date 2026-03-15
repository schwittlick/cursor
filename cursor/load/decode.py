from __future__ import annotations

import json
import re
from typing import Any, Dict, Union

import orjson

from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property

# Precompute common objects
EMPTY_DICT = {}
COLOR_PROPERTY = Property.COLOR


def parse_position(obj: Dict[str, Any]) -> Position:
    pos = Position(obj["x"], obj["y"], obj["ts"])

    if "c" in obj:
        pos.properties[Property.COLOR] = obj["c"]

    return pos


def parse_size(obj: Dict[str, Any]) -> tuple[int, int]:
    return obj["w"], obj["h"]


def parse_collection(obj: Dict[str, Any]) -> Collection:
    ts = obj["timestamp"]
    pc = Collection(ts)
    for p in obj["paths"]:
        path = Path()
        for _pos in p:
            path.add_position(parse_position(_pos))
        pc.add(path)
    return pc


def custom_decoder(
    obj: Dict[str, Any],
) -> Union[Dict, Position, tuple[int, int], Collection]:
    if isinstance(obj, dict):
        if "x" in obj and "y" in obj:
            return parse_position(obj)
        elif "w" in obj and "h" in obj:
            return parse_size(obj)
        elif "paths" in obj and "timestamp" in obj:
            return parse_collection(obj)
    return obj


class CustomJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=custom_decoder, *args, **kwargs)


def preprocess_json(s: str) -> str:
    # This regex finds single-quoted strings and replaces them with double-quoted strings
    # It handles escaped single quotes within the strings
    return re.sub(
        r"'((?:[^'\\]|\\.)*)'",
        lambda m: json.dumps(json.loads(m.group(0).replace("'", '"'))),
        s,
    )


def load_json(json_string: str) -> Any:
    # First, parse the JSON without any custom decoding
    try:
        processed_content = preprocess_json(json_string)
        # First, try to parse with orjson for speed
        parsed_data = orjson.loads(processed_content)
        # Apply our custom decoding to the parsed data
        return custom_decode(parsed_data)
    except orjson.JSONDecodeError:
        # If orjson fails, fall back to the standard json library with our custom decoder
        return json.loads(json_string, cls=CustomJSONDecoder)


def custom_decode(data: Any) -> Any:
    if isinstance(data, dict):
        return custom_decoder(data)
    elif isinstance(data, list):
        return [custom_decode(item) for item in data]
    else:
        return data


def decode_recording(data: dict) -> dict:
    """Decode raw orjson output into a recording dict.

    Replaces data["mouse"] with a Collection built directly from the raw dicts,
    avoiding the per-object Python callback overhead of json.loads + object_hook.
    Keys and other fields are left as-is (plain lists).
    """
    mouse_raw = data["mouse"]
    ts = mouse_raw["timestamp"]
    pc = Collection(ts)
    for path_raw in mouse_raw.get("paths", []):
        path = Path()
        for pos_raw in path_raw:
            pos = Position(pos_raw["x"], pos_raw["y"], pos_raw["ts"])
            c = pos_raw.get("c")
            if c is not None:
                pos.properties[COLOR_PROPERTY] = tuple(c)
            path.add_position(pos)
        pc.add(path)
    data["mouse"] = pc
    return data


class MyJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct: dict) -> dict | Position | Collection:
        if "x" in dct:
            if "c" in dct:
                if dct["c"] is not None:
                    c = tuple(dct["c"])
                else:
                    c = None
            else:
                c = None

            pos = Position(dct["x"], dct["y"], dct["ts"])
            if c is not None:
                pos.properties[Property.COLOR] = c
            return pos
        if "w" in dct and "h" in dct:
            s = dct["w"], dct["h"]
            return s
        if "paths" in dct and "timestamp" in dct:
            ts = dct["timestamp"]
            pc = Collection(ts)
            for _p in dct["paths"]:
                pc.add(Path(_p))
            return pc
        return dct
