from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import renderer


def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0, thickness=3)
    jpeg_renderer.save(fname)


if __name__ == "__main__":
    recs = data.DataDirHandler().recordings()
    loader = loader.Loader(directory=recs, limit_files=1)
    all_paths = loader.all_paths()

    # filter1 = filter.DirectionChangeEntropyFilter(2.0, 3.0)
    # all_paths.filter(filter1)

    pc = path.PathCollection()

    sc = 1
    for x in range(4):
        p1 = all_paths.random()
        p1.morph((x * sc, 0), (x * sc, sc))

        p2 = all_paths.random()
        p2.morph((x * sc, 0), ((x + 1) * sc, sc))

        p3 = all_paths.random()
        p3.morph((x * sc, sc), ((x + 1) * sc, sc))

        pc.add(p1)
        pc.add(p2)
        pc.add(p3)

    pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=40)
    save_wrapper(pc, "genuary", "6_triangle_subdivision")
