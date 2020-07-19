from cursor import renderer
from cursor import path
from cursor import data
from cursor import device

import random
import math

if __name__ == "__main__":
    gcode_folder = data.DataDirHandler().gcode("composition59")
    folder = data.DataDirHandler().jpg("composition59")
    gcode_renderer = renderer.GCodeRenderer(gcode_folder, z_down=4.5)
    jpeg_renderer = renderer.JpegRenderer(folder)

    coll = path.PathCollection()

    path = path.Path(layer="round1")
    theta = 0
    yextra = 0
    r = 1
    while theta < math.pi * 80:  # 80
        r += 0.05
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        path.add(x, y, 0)
        theta += 0.02  # math.pi / random.randint(1, 800)
        yextra += 0.15

    reversed_path = path.reversed()
    reversed_path.layer = "round2"

    coll.add(path)
    # coll.add(reversed_path)

    coll.fit(device.DrawingMachine.Paper.custom_70_70(), 95)

    num = "upward_spiral"
    #num = coll.hash()
    fname = f"composition59_{num}"

    print(coll.bb())

    jpeg_renderer.render(coll)
    jpeg_renderer.save(f"{fname}")
    gcode_renderer.render(coll)
    gcode_renderer.save(f"{fname}")

    exit(0)

    separate_layers = coll.get_layers()
    for layer, pc in separate_layers.items():
        pc.fit(device.DrawingMachine.Paper.custom_70_100_landscape(), 100)

        jpeg_renderer.render(pc)
        jpeg_renderer.save(f"{fname}_{layer}")
        gcode_renderer.render(pc)
        gcode_renderer.save(f"{fname}_{layer}")
