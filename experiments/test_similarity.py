from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import renderer
from cursor import filter

import random


def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0, thickness=6)
    jpeg_renderer.save(fname)


if __name__ == "__main__":
    p1 = path.Path()
    p1.add(0, 0)
    p1.add(0, 1)
    p1.add(0, 2)
    p1.add(0, 3)
    p1.add(0, 4)

    p2 = path.Path()
    p2.add(0, 0)
    p2.add(0, 1)
    p2.add(0, 2)
    p2.add(0, 3)
    p2.add(0, 4)

    sim = p1.similarity(p2)
    print(sim)

    p3 = path.Path()
    p3.add(0, 0)
    p3.add(0, 1)
    p3.add(0, 2)
    p3.add(0, 3)

    sim2 = p1.similarity(p3)
    print(sim2)

    recs = data.DataDirHandler().recordings()
    loader = loader.Loader(directory=recs, limit_files=1)
    all_paths = loader.all_paths()

    pc = path.PathCollection()

    p1 = all_paths.random()
    for i in range(100):

        p2 = all_paths.random()
        _sim = p1.similarity(p2)
        if _sim > 0.999:
            pc.add(p2)
        print(_sim)

    pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=10)
    save_wrapper(pc, "similarity", f"similarity_test")
