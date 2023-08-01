import math

import arcade

from cursor import misc
from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.path import Path
from cursor.position import Position
from cursor.renderer import RealtimeRenderer, GCodeRenderer

if __name__ == "__main__":
    """
    we use path for x, y
    properties will be z values and ampere values
    """
    path = Path()

    frequency = 2  # the times the sine cycles while going start -> end
    amplitude = 5
    resolution = 100
    start = (0, 500)
    end = (1000, 500)

    values = []
    for i in range(resolution):
        v = misc.map(i, 0, resolution - 1, 0, math.pi * frequency)
        v = math.sin(v) + 1.0
        v = v * amplitude / 2
        values.append(v)

        x = misc.map(i, 0, resolution - 1, start[0], end[0])
        y = misc.map(i, 0, resolution - 1, start[1], end[1])

        pos = Position(x, y)
        pos.properties["z"] = v
        pos.properties["amp"] = 0.1
        pos.properties["volt"] = 3.3
        path.add_position(pos)

    path.properties["laser"] = True

    collection = Collection()
    collection.add(path)
    gcode_dir = DataDirHandler().gcode("multi-dim")
    gcode_renderer = GCodeRenderer(gcode_dir)
    gcode_renderer.render(collection)
    instructions = gcode_renderer.generate_instructions()
    rr = RealtimeRenderer(1000, 1000, "multi-dim")
    rr.add_path(path, line_width=1, color=arcade.color.BLACK)
    rr.run()
    print(values)
