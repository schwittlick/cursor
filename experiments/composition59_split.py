from cursor import renderer
from cursor import path
from cursor import data
from cursor import device

import math


def save_wrapper(pc, projname, fname):
    gcode_folder = data.DataDirHandler().gcode(projname)
    folder = data.DataDirHandler().jpg(projname)
    gcode_renderer = renderer.GCodeRenderer(gcode_folder, z_down=4.5)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc)
    jpeg_renderer.save(fname)
    gcode_renderer.render(pc)
    gcode_renderer.save(fname)


def two_split_spiral():
    pc = path.PathCollection()

    theta = 0
    yextra = 0
    r = 50
    perc = 0.35

    p1 = path.Path(layer="top")
    p2 = path.Path(layer="bottom")

    while theta < 800:
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra

        theta += 0.02
        yextra += 0.01

        if theta < 800 * perc:
            p1.add(x, y)
        elif theta > 800 - 800 * perc:
            p2.add(x, y)

    pc.add(p1)
    pc.add(p2)

    return "two_split_spiral", pc


def middle_split_spiral():
    pc = path.PathCollection()

    theta = 0
    yextra = 0
    r = 50
    perc1 = 0.10
    perc2 = 0.5

    p1 = path.Path(layer="top")
    p2 = path.Path(layer="middle")
    p3 = path.Path(layer="bottom")

    while theta < 800:
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra

        theta += 0.02
        yextra += 0.01

        if theta < 800 * perc1:
            p1.add(x, y)
        elif 800 * perc1 < theta < 800 * perc2:
            p2.add(x, y)
        else:
            p3.add(x, y)

    pc.add(p1)
    pc.add(p2)
    pc.add(p3)

    return "middle_split_spiral", pc


def three_split_spiral():
    pc = path.PathCollection()

    theta = 0
    yextra = 0
    r = 50
    perc = 0.2

    p1 = path.Path(layer="top")
    p2 = path.Path(layer="middle")
    p3 = path.Path(layer="bottom")

    while theta < 800:
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra

        theta += 0.02
        yextra += 0.015

        if theta < 800 * perc:
            p1.add(x, y)
        elif 800 / 2 - 800 * perc / 2 < theta < 800 / 2 + 800 * perc / 2:
            p2.add(x, y)
        elif theta > 800 - 800 * perc:
            p3.add(x, y)

    pc.add(p1)
    pc.add(p2)
    pc.add(p3)

    return "three_split_spiral", pc


if __name__ == "__main__":
    coll = path.PathCollection()

    # num, pc = two_split_spiral()
    # num, pc = three_split_spiral()
    num, pc = middle_split_spiral()

    pc.fit(device.DrawingMachine.Paper.a1_landscape(), padding_mm=90)
    save_wrapper(pc, "composition59_split", f"c59_{num}_together")

    for p in pc:
        p_rev = p.reversed()
        p_rev.layer = p_rev.layer + "_rev"

        coll.add(p)
        coll.add(p_rev)

    coll.fit(device.DrawingMachine.Paper.a1_landscape(), padding_mm=90)

    fname = f"c59_{num}_a1"

    separate_layers = coll.get_layers()
    for layer, pc in separate_layers.items():
        gcode_folder = data.DataDirHandler().gcode("composition59_split")
        folder = data.DataDirHandler().jpg("composition59_split")
        gcode_renderer = renderer.GCodeRenderer(gcode_folder, z_down=4.5)
        jpeg_renderer = renderer.JpegRenderer(folder)

        # pc.fit(device.DrawingMachine.Paper.a1_landscape(), 90)

        jpeg_renderer.render(pc)
        jpeg_renderer.save(f"{fname}_{layer}")
        gcode_renderer.render(pc)
        gcode_renderer.save(f"{fname}_{layer}")
