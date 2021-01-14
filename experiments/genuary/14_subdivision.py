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
    recs = data.DataDirHandler().recordings()
    loader = loader.Loader(directory=recs, limit_files=1)
    all_paths = loader.all_paths()

    main = all_paths.random()
    main = main.morph((0, 0), (100, 0))

    ff = filter.DirectionChangeEntropyFilter(0.0, 2.5) # 2.0
    all_paths.filter(ff)

    for i in range(10):
        pc = path.PathCollection()

        counter = 0
        for point in main:
            if counter % 2 == 0:
                pa = all_paths.random().morph((point.x, point.y), (point.x, -50))
                pc.add(pa)
            else:
                pa = all_paths.random().morph((point.x, point.y), (point.x, 50))
                pc.add(pa)

            counter += 1

        pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=40)
        save_wrapper(pc, "genuary", f"14_subdivision_3_{i}")