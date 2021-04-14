from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import filter
from cursor import renderer

import sys
import random


def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0, thickness=3)
    jpeg_renderer.save(fname)


if __name__ == "__main__":

    with open("genuary12_api_test.hpgl", "w") as f:
        f.write("SP1;\n")
        ips = []
        ips.append("1.1.229.100")
        ips.append("1.179.185.50")
        ips.append("1.186.248.30")
        ips.append("101.32.116.55")
        mm = device.MinmaxMapping.maps[device.PlotterType.HP_7475A_A3]
        f2 = open("all_blocked.txt", "r")
        f.write("DT~,1;\n")
        counter = 0
        for ip in f2:
            mx = mm.minx
            mx2 = mm.maxx
            x = random.randint(-200, mx2)
            y = random.randint(-200, mm.maxy)

            f.write(f"PU{x},{y};\n")
            # f.write("PD;\n")
            f.write(f"LB{ip.rstrip()}~;\n")

            counter += 1
            if counter >= 1000:

                f.write("SP0;\n")
                sys.exit(0)
