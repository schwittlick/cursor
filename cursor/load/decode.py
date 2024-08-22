from __future__ import annotations

import json
import orjson
import re
from typing import Any, Dict, Union

import pyautogui

from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property

# Precompute common objects
EMPTY_DICT = {}
COLOR_PROPERTY = Property.COLOR


def parse_position(obj: Dict[str, Any]) -> Position:
    return Position(
        obj["x"],
        obj["y"],
        obj["ts"],
        {COLOR_PROPERTY: tuple(obj["c"])} if "c" in obj else EMPTY_DICT,
    )


def parse_size(obj: Dict[str, Any]) -> pyautogui.Size:
    return pyautogui.Size(obj["w"], obj["h"])


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
        obj: Dict[str, Any]
) -> Union[Dict, Position, pyautogui.Size, Collection]:
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
            return Position(dct["x"], dct["y"], dct["ts"], {Property.COLOR: c})
        if "w" in dct and "h" in dct:
            s = pyautogui.Size(dct["w"], dct["h"])
            return s
        if "paths" in dct and "timestamp" in dct:
            ts = dct["timestamp"]
            pc = Collection(ts)
            for _p in dct["paths"]:
                pc.add(Path(_p))
            return pc
        return dct
