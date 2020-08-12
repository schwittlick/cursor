from cursor import renderer
from cursor import path
from cursor import data
from cursor import device

import random
import math


def full_spiral(pp):
    theta = 0
    yextra = 0
    # r = 1
    r = 50
    while theta < math.pi * 3 * 80:  # 80
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp.add(x, y, 0)
        theta += 0.02  # math.pi / random.randint(1, 800)
        yextra += 0.01

    return "full_plain"


if __name__ == "__main__":
    coll = path.PathCollection()
    pp = path.Path(layer="round1")

    num = full_spiral(pp)

    reversed_path = pp.reversed()
    reversed_path.layer = "round2"

    coll.add(pp)
    coll.add(reversed_path)

    coll.fit(device.DrawingMachine.Paper.a1_landscape(), 90)

    fname = f"composition59_{num}_a1"

    #jpeg_renderer.render(coll)
    #jpeg_renderer.save(f"{fname}")
    #gcode_renderer.render(coll)
    #gcode_renderer.save(f"{fname}")

    #exit(0)

    separate_layers = coll.get_layers()
    for layer, pc in separate_layers.items():
        gcode_folder = data.DataDirHandler().gcode("testing_layers")
        folder = data.DataDirHandler().jpg("testing_layers")
        gcode_renderer = renderer.GCodeRenderer(gcode_folder, z_down=4.5)
        jpeg_renderer = renderer.JpegRenderer(folder)

        pc.fit(device.DrawingMachine.Paper.a1_landscape(), 90)

        jpeg_renderer.render(pc)
        jpeg_renderer.save(f"{fname}_{layer}")
        gcode_renderer.render(pc)
        gcode_renderer.save(f"{fname}_{layer}")
