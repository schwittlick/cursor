from cursor import loader
from cursor import renderer
from cursor import path
from cursor import filter
from cursor import data

import pyautogui

def pen_sample(pa, id):
    padding = 0.25

    jpeg_renderer = renderer.JpegRenderer()
    svg_renderer = renderer.CursorSVGRenderer()
    res = pyautogui.Size(110, 110)
    coll = path.PathCollection(res)

    for i in range(46*8):
        morphed = pa.morph((10.0 + float(i) * padding, 10.0), (10.0 + float(i) * padding, 100.0))
        coll.add(morphed, res)

        morphed2 = pa.morph((10.0, 10.0 + float(i) * padding), (100.0, 10.0 + float(i) * padding))
        coll.add(morphed2, res)

    print(coll.bb())
    bb = path.BoundingBox(0, 0, res.width, res.height)
    if bb.inside(coll):
        fname = F"pen_sample_test_{id}"
        jpeg_renderer.render([coll], fname, 5.0)
        svg_renderer.render([coll], fname)
    else:
        print(F"Not Saving {id}")


if __name__ == '__main__':
    p = data.DataHandler().data_path()
    l = loader.Loader(directory=p)
    rec = l.single(0)
    all_paths = l.all_paths()

    entropy_filter = filter.EntropyFilter(0.6, 0.6)
    all_paths.filter(entropy_filter)

    print(len(all_paths))

    point_count_filter = filter.MinPointCountFilter(0)
    all_paths.filter(point_count_filter)

    print(len(all_paths))

    point_count_filter = filter.MaxPointCountFilter(99999)
    all_paths.filter(point_count_filter)

    for i in range(45, 46):
        pa = all_paths[i]
        pen_sample(pa, i)