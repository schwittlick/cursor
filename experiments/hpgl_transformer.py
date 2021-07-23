from cursor import data
from cursor import device
from cursor import path
from cursor import renderer

import sys


def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=2.0, thickness=3)
    jpeg_renderer.save(fname)


if __name__ == "__main__":
    commands = []
    with open(sys.argv[1], "r") as filestream:
        for line in filestream:
            currentline = line.split(";")
            for c in currentline:
                if c:
                    commands.append(c)

    pc = path.PathCollection()

    counter = 0

    prev = ""

    for c in commands:
        if c.startswith("PU"):
            p = c[2:].split(",")
            prev = c

        elif c.startswith("PD"):
            counter += 1
            p = c[2:].split(",")
            _path = path.Path()
            # if len(p) == 2:
            psplit = prev[2:].split(",")
            _path.add(float(psplit[0]), float(psplit[1]))
            for step in range(0, len(p), 2):
                _path.add(float(p[step]), float(p[step + 1]))
                # print(step)
            pc.add(_path)
        else:
            print(c)

    print(counter)
    pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=20)
    save_wrapper(pc, "calendar", f"calendar1")

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        20,
        "calendar",
        pc.hash(),
    )
