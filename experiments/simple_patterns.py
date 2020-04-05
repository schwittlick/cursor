from cursor import loader
from cursor import renderer
from cursor.path import TimedPosition as TP
from cursor.path import PathCollection
from cursor.path import Path
from cursor import data
from cursor import device


def simple_pattern1():
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=1)

    r = renderer.GCodeRenderer("straight_lines", z_down=3.0)
    jpeg_renderer = renderer.JpegRenderer("straight_lines")

    coll = PathCollection()

    xoffset = 200
    yoffset = 100

    for i in range(50):
        print(i)
        xfrom = 1.5 * i + xoffset
        yfrom = 5 + yoffset
        xto = 1.5 * i + xoffset
        yto = 200 + yoffset

        pth = Path()
        pth.add(xfrom, yfrom, 0)
        pth.add(xto, yto, 0)

        coll.add(pth)

    bb = coll.bb()

    coll.add(Path([TP(bb.x, bb.y), TP(bb.x + bb.w, bb.y)]))
    coll.add(Path([TP(bb.x + bb.w, bb.y), TP(bb.x + bb.w, bb.y + bb.h),]))
    coll.add(Path([TP(bb.x + bb.w, bb.y + bb.h), TP(bb.x, bb.y + bb.h),]))
    coll.add(Path([TP(bb.x, bb.y + bb.h), TP(bb.x, bb.y)]))

    coll.fit(device.DrawingMachine.Paper.a1_landscape(), 50)

    r.render(coll, f"straight_lines_{coll.hash()}")
    jpeg_renderer.render(coll, f"straight_lines_{coll.hash()}")


if __name__ == "__main__":
    simple_pattern1()
