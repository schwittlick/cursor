from __future__ import annotations

import json

import pyautogui

from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property


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
