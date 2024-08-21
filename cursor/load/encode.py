from __future__ import annotations

import json

from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property


class MyJsonEncoder(json.JSONEncoder):
    def default(self, o: Position | Path | Collection) -> dict | list[Position]:
        match o:
            case Collection():
                return {
                    "paths": o.get_all(),
                    "timestamp": o.timestamp(),
                }
            case Path():
                return o.vertices
            case Position():
                d = {
                    "x": round(o.x, 4),
                    "y": round(o.y, 4)
                }

                if o.timestamp:
                    d["ts"] = round(o.timestamp, 2)

                if Property.COLOR in o.properties.keys():
                    color = o.properties[Property.COLOR]
                    if color:
                        d["c"] = color
                return d
