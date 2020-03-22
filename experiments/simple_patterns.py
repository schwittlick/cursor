from cursor import loader
from cursor import renderer
from cursor import path
from cursor import data


def simple_pattern1():
    p = data.DataHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=1)
    rec = ll.single(0)

    r = renderer.GCodeRenderer("straight_lines", z_down=3.0)
    jpeg_renderer = renderer.JpegRenderer("straight_lines")

    coll = path.PathCollection(rec.resolution)

    xoffset = 200
    yoffset = 100

    for i in range(50):
        print(i)
        xfrom = 1.5 * i + xoffset
        yfrom = 5 + yoffset
        xto = 1.5 * i + xoffset
        yto = 200 + yoffset

        pth = path.Path()
        pth.add(xfrom, yfrom, 0)
        pth.add(xto, yto, 0)

        coll.add(pth, rec.resolution)

    bb = coll.bb()

    coll.add(
        path.Path(
            [path.TimedPosition(bb.x, bb.y), path.TimedPosition(bb.x + bb.w, bb.y)]
        ),
        rec.resolution,
    )
    coll.add(
        path.Path(
            [
                path.TimedPosition(bb.x + bb.w, bb.y),
                path.TimedPosition(bb.x + bb.w, bb.y + bb.h),
            ]
        ),
        rec.resolution,
    )
    coll.add(
        path.Path(
            [
                path.TimedPosition(bb.x + bb.w, bb.y + bb.h),
                path.TimedPosition(bb.x, bb.y + bb.h),
            ]
        ),
        rec.resolution,
    )
    coll.add(
        path.Path(
            [path.TimedPosition(bb.x, bb.y + bb.h), path.TimedPosition(bb.x, bb.y)]
        ),
        rec.resolution,
    )

    coll.fit(path.Paper.a1_landscape(), 50)

    r.render(coll, f"straight_lines_{coll.hash()}")
    jpeg_renderer.render(coll, f"straight_lines_{coll.hash()}")


if __name__ == "__main__":
    simple_pattern1()
