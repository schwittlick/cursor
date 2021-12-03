from cursor.path import Path, PathCollection
from cursor import device

import math


class Spiral:
    def __init__(self):
        pass



    def get_plain(self):
        theta = 0
        theta_incr = 0.02
        max_theta = 255
        r = 50
        xextra = 0
        xextra_incr = 0.15
        maxx =

        pp = Path()

        while theta < max_theta:
            y = r * math.cos(theta) * 2
            x = r * math.sin(theta) + xextra
            pp.add(x, y, 0)
            theta += theta_incr
            xextra += xextra_incr

        return pp

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


if __name__ == "__main__":
    coll = PathCollection()

    for i in range(16):
        x = i % 4
        y = (i - x) / 4

        pp = Path(layer=f"{i}")
        num = plain_spiral(pp)
        pp.translate(x * 2250, y * 250)
        coll.add(pp)

    name = "pptx"
    device.SimpleExportWrapper().ex(
        coll,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        20,
        "composition59_pptx_layer2",
        name,
    )
