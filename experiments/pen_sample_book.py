from cursor import loader
from cursor import renderer
from cursor import path
from cursor import filter
from cursor import data

import pyautogui


def add_bb(bb, coll, res):
    coll.add(path.Path([path.TimedPosition(bb.x, bb.y), path.TimedPosition(bb.x + bb.w, bb.y)]), res)
    coll.add(path.Path([path.TimedPosition(bb.x + bb.w, bb.y), path.TimedPosition(bb.x + bb.w, bb.y + bb.h)]), res)
    coll.add(path.Path([path.TimedPosition(bb.x + bb.w, bb.y + bb.h), path.TimedPosition(bb.x, bb.y + bb.h)]), res)
    coll.add(path.Path([path.TimedPosition(bb.x, bb.y + bb.h), path.TimedPosition(bb.x, bb.y)]), res)


def pen_sample(pa, id):
    padding = 0.25

    jpeg_renderer = renderer.JpegRenderer('pen_sample_book')
    svg_renderer = renderer.CursorSVGRenderer('pen_sample_book')
    res = pyautogui.Size(140, 340)
    coll = path.PathCollection(res)

    xstart = 50
    ystart = 100
    yend = 200

    lines = 10  # 46 * 8

    for i in range(lines):
        x1 = xstart + float(i) * padding
        y1 = ystart

        y2 = yend
        morphed = pa.morph((x1, y1), (x1, y2))
        coll.add(morphed, res)

        # morphed2 = pa.morph((10.0, 10.0 + float(i) * padding), (100.0, 10.0 + float(i) * padding))
        # coll.add(morphed2, res)

    print(coll.bb())
    bb = path.BoundingBox(0, 0, res.width, res.height)
    if bb.inside(coll):
        fname = F"pen_sample_test_{id}"
        # coll2 = path.PathCollection(res)
        # add_bb(coll.bb(), coll2, res)

        jpeg_renderer.render([coll], fname, 5.0)
        svg_renderer.render([coll], fname)
    else:
        print(F"Not Saving {id}")


if __name__ == '__main__':
    p = data.DataHandler().recordings()
    ll = loader.Loader(directory=p)
    rec = ll.single(0)
    all_paths = ll.all_paths()

    print(len(all_paths))

    entropy_filter = filter.EntropyFilter(0.9, 0.9)
    all_paths.filter(entropy_filter)

    print(len(all_paths))

    for i in range(45, 46):
        pa = all_paths[i]
        pen_sample(pa, i)
