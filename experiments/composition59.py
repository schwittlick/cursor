from cursor import renderer
from cursor import path
from cursor import data
from cursor import device

import math


def plain_spiral(pp):
    theta = 0
    yextra = 0
    r = 50
    while theta < 255:
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp.add(x, y, 0)
        theta += 0.02
        yextra += 0.15

    return "spiral_plain"


def full_spiral(pp):
    theta = 0
    yextra = 0
    r = 50
    while theta < 800:
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp.add(x, y, 0)
        theta += 0.02
        yextra += 0.01

    return "full_plain"


def circleball_spiral(pp):
    theta = 0
    yextra = 0
    r = 1
    while theta < 255:
        r += 0.4
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp.add(x, y, 0)
        theta += 0.02
        yextra += 0.15

    return "circleball_spiral"


def upward_spiral(pp):
    theta = 0
    yextra = 0
    r = 1
    while theta < 940:
        r += 0.03
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp.add(x, y, 0)
        theta += 0.02
        yextra += 0.15

    return "upward_spiral"


def heart_spiral(pp):
    theta = 0
    yextra = 0
    while theta < 800:
        r = (math.sin(theta) * 500) + 500
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp.add(x, y, 0)
        theta += 0.02
        yextra += 0.06

    return "heart_spiral"


if __name__ == "__main__":
    coll = path.PathCollection()

    pp = path.Path(layer="round1")

    # num = plain_spiral(pp)
    # num = circleball_spiral(pp)
    # num = upward_spiral(pp)
    # num = full_spiral(pp)
    num = heart_spiral(pp)

    reversed_path = pp.reversed()
    reversed_path.layer = "round2"

    coll.add(pp)
    coll.add(reversed_path)

    coll.fit(device.DrawingMachine.Paper.a1_landscape(), padding_mm=90)

    fname = f"composition59_{num}_a1"

    separate_layers = coll.get_layers()
    for layer, pc in separate_layers.items():
        gcode_folder = data.DataDirHandler().gcode("composition59")
        folder = data.DataDirHandler().jpg("composition59")
        gcode_renderer = renderer.GCodeRenderer(gcode_folder, z_down=4.5)
        jpeg_renderer = renderer.JpegRenderer(folder)

        # pc.fit(device.DrawingMachine.Paper.a1_landscape(), 90)

        jpeg_renderer.render(pc)
        jpeg_renderer.save(f"{fname}_{layer}")
        gcode_renderer.render(pc)
        gcode_renderer.save(f"{fname}_{layer}")
