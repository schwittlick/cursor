from cursor import loader
from cursor import renderer
from cursor import filter
from cursor import path
from cursor import data
from cursor import device

import random
import math

if __name__ == "__main__":
    gcode_folder = data.DataDirHandler().gcode("composition59")
    folder = data.DataDirHandler().jpg("composition59")
    gcode_renderer = renderer.GCodeRenderer(gcode_folder, z_down=3.0)
    jpeg_renderer = renderer.JpegRenderer(folder)

    coll = path.PathCollection()

    path = path.Path()
    theta = 0
    yextra = 0
    while theta < math.pi * 20:
        h = 150
        k = 150
        r = 50
        y = h + r * math.cos(theta) * 2
        x = k - r * math.sin(theta) + yextra
        path.add(x, y, 0)
        theta += math.pi / random.randint(1, 800)
        yextra += 0.15

    coll.add(path)

    coll.fit(device.DrawingMachine.Paper.custom_36_48_landscape(), 0)

    fname = f"composition59_{coll.hash()}"
    print(fname)
    #fname = f"composition59"
    gcode_renderer.render(coll)
    gcode_renderer.save(fname)
    jpeg_renderer.render(coll)
    jpeg_renderer.save(fname)