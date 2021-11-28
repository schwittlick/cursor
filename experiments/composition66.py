from cursor.path import Path, PathCollection
<<<<<<< HEAD
from cursor.renderer import RealtimeRenderer
from cursor import device

import math


def plain_spiral(thetamax, yoffset, yadd, xextra):
    pp = Path(layer="round1")
    theta = 0
    ypos = 0
    xpos = 0
    r = 30
    while theta < thetamax: #* 20:
        y = r * math.cos(theta) + xpos
        x = r * math.sin(theta) + ypos
        pp.add(x, y + yoffset, 0)
        theta += 0.08
        ypos += yadd
        xpos += xextra

    return pp


if __name__ == "__main__":
    coll = PathCollection()

    xplus = 0.25
    yplus = 0.25

    p1 = plain_spiral(255, 0, xplus, 0)
    p2 = plain_spiral(255, 400, xplus, 0)
    p3 = plain_spiral(155, 0, 0, yplus)
    p4 = plain_spiral(155, 0, xplus, yplus)

    num = 'ad_strauss'

    # reversed_path = pp.reversed()
    # reversed_path.layer = "round2"

    coll.add(p1)
    coll.add(p2)
    coll.add(p3)
    coll.add(p4)
    # coll.add(reversed_path)

    #r = RealtimeRenderer()
    #r.render(coll)

    device.SimpleExportWrapper().ex(
        coll,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        50,
        "composition66",
        num,
    )
=======
from cursor import device
import matplotlib

matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt

plt.style.use("ggplot")

import math
from scipy.spatial import distance
import sys
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation


def map(value, inputMin, inputMax, outputMin, outputMax, clamp):
    outVal = (value - inputMin) / (inputMax - inputMin) * (
        outputMax - outputMin
    ) + outputMin

    if clamp:
        if outputMax < outputMin:
            if outVal < outputMax:
                outVal = outputMax
            elif outVal > outputMin:
                outVal = outputMin
    else:
        if outVal > outputMax:
            outVal = outputMax
        elif outVal < outputMin:
            outVal = outputMin
    return outVal


class SpiralFactory:
    def __init__(self):
        self.xx = 0.1
        self.yy = 0.25

    def plain_spiral(self, th, x_add, y_add, target, layer):
        pp = Path(layer=layer)
        theta = math.pi * 2
        xoffset = 0
        yoffset = 0
        r = 35
        center = [0, 0]
        while distance.euclidean(center, target) > 0.01:
            x = r * math.sin(theta) + xoffset
            y = r * math.cos(theta) + yoffset
            pp.add(x, y, 0)
            theta += th
            xoffset += x_add
            yoffset += y_add
            # print(distance.euclidean(center, target))
            center[0] += x_add
            center[1] += y_add

        return pp

    def other_spiral(self):
        t = 0
        pa = Path(layer="round1")
        for t in range(0, int(2 * math.pi * 10), 1):
            x = t / 10.0 * math.cos(t)
            y = t / 10.0 * math.sin(t)
            pa.add(x, y)
        return pa


if __name__ == "__main__":
    num = "ad_strauss"

    sf = SpiralFactory()
    _x = []
    _y = []
    fig = plt.figure()
    (line,) = plt.plot(_x, _y, "-")

    x = 0
    y = 0

    def mouse_move(event):
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
        sf.xx = map(x, 40, 2400, -2, 2, True)
        sf.yy = map(y, 80, 1640, 0.1, 2, True)

    plt.connect("motion_notify_event", mouse_move)

    def update(frame):
        # print(sf.xx, sf.yy)
        coll = PathCollection()
        tstep = 0.1
        xstep = 0.005
        ystep = 0.005
        p2 = sf.plain_spiral(tstep, xstep, 0.0, [100, 0], "1")  # horizon
        p3 = sf.plain_spiral(tstep, 0.0, ystep, [0, 100], "2")  # vertical
        p4 = sf.plain_spiral(tstep, 0.0, ystep, [0, 200], "3")  # vertical
        p5 = sf.plain_spiral(tstep, xstep, -ystep, [100, -100], "4")  # diagonal
        p6 = sf.plain_spiral(tstep, xstep, 0, [200, 0], "5")  # horizontal
        p7 = sf.plain_spiral(tstep, xstep, 0.0, [100, 0], "6")  # horizon
        p8 = sf.plain_spiral(tstep, 0.0, ystep, [0, 100], "7")  # vertical
        p9 = sf.plain_spiral(tstep, 0.0, ystep, [0, 200], "8")  # vertical
        p10 = sf.plain_spiral(tstep, xstep, 0.0, [100, 0], "9")  # horizon

        p3.translate(0, 100)
        p4.translate(100, 0)
        p5.translate(0, 200)
        p6.translate(100, 200)
        p7.translate(100, 100)
        p8.translate(200, 0)
        p9.translate(300, 0)
        p10.translate(200, 0)
        # coll.add(p1)
        coll.add(p2)
        coll.add(p3)
        coll.add(p4)
        coll.add(p5)
        coll.add(p6)
        coll.add(p7)
        coll.add(p8)
        coll.add(p9)
        coll.add(p10)

        coll.fit(
            (800, 600),
            padding_mm=50,
            cutoff_mm=0,
        )

        device.SimpleExportWrapper().ex(
            coll,
            device.PlotterType.ROLAND_DPX3300,
            device.PaperSize.LANDSCAPE_A1,
            50,
            "composition66",
            num,
        )
        sys.exit(0)

        coll.translate(0, 0)

        _x = []
        _y = []
        for pa in coll:
            for poi in pa:
                _x.append(poi.x)
                _y.append(poi.y)
        line.set_data(_x, _y)
        fig.gca().relim()
        fig.gca().autoscale_view()
        return (line,)

    animation = FuncAnimation(fig, update, interval=20)

    pyplot.show()

    # fig.savefig("c66.jpg")
    # plt.show()

    # device.SimpleExportWrapper().ex(
    #    coll,
    #    device.PlotterType.ROLAND_DPX3300,
    #    device.PaperSize.LANDSCAPE_A1,
    #    50,
    #    "composition66",
    #    num,
    # )
>>>>>>> 679d9204f4692f549e957e8a9b229537258b2053
