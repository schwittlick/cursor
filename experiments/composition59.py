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


def full_spiral(pp, rounds=800):
    theta = 0
    yextra = 0
    r = 50
    while theta < rounds:
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


def fat_spiral(pp):
    theta = 0
    yextra = 0
    r = 50
    while theta < 600:
        x = r * math.cos(theta) * 2
        y = r * math.sin(theta) + yextra
        pp.add(x, y, 0)
        theta += 0.005
        yextra += 0.01

    return "fat_spiral"


if __name__ == "__main__":
    coll = path.PathCollection()

    pp = path.Path(layer="round1")

    # num = plain_spiral(pp)
    # num = circleball_spiral(pp)
    # num = upward_spiral(pp)
    num = full_spiral(pp, 1600 * 5)
    # num = heart_spiral(pp)
    # num = fat_spiral(pp)

    reversed_path = pp.reversed()
    reversed_path.layer = "round2"

    coll.add(pp)
    coll.add(reversed_path)

    axidraw = False
    dpx3300 = True
    if axidraw:
        coll.fit(
            size=device.AxiDraw.Paper.custom_36_48_landscape(),
            machine=device.AxiDraw(),
            padding_mm=64,
        )
        fname = f"composition59_axidraw_{num}_a1"
    elif dpx3300:
        coll.fit(
            device.RolandDPX3300.Paper.a1_landscape(),
            machine=device.RolandDPX3300(),
            padding_mm=90,
            center_point=(-880, 600),
        )
        fname = f"composition59_dpx3300_{num}_a1"

        hpgl_folder = data.DataDirHandler().hpgl("composition59")
        hpgl_renderer = renderer.HPGLRenderer(hpgl_folder)
        separate_layers = coll.get_layers()
        for layer, pc in separate_layers.items():
            hpgl_renderer.render(pc)
            hpgl_renderer.save(f"{fname}_{layer}")
        exit(0)
    else:
        coll.fit(device.DrawingMachine.Paper.a1_landscape(), padding_mm=90)
        fname = f"composition59_{num}_a1"

    separate_layers = coll.get_layers()
    for layer, pc in separate_layers.items():
        gcode_folder = data.DataDirHandler().gcode("composition59")
        folder = data.DataDirHandler().jpg("composition59")
        svg_dir = data.DataDirHandler().svg("composition59")
        gcode_renderer = renderer.GCodeRenderer(gcode_folder, z_down=4.5)
        jpeg_renderer = renderer.JpegRenderer(folder)
        svg_renderer = renderer.SvgRenderer(svg_dir)

        # pc.fit(device.DrawingMachine.Paper.a1_landscape(), 90)

        jpeg_renderer.render(pc)
        jpeg_renderer.save(f"{fname}_{layer}")
        gcode_renderer.render(pc)
        gcode_renderer.save(f"{fname}_{layer}")
        svg_renderer.render(pc)
        svg_renderer.save(f"{fname}_{layer}")
