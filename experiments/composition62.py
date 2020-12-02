from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import renderer


def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0)
    jpeg_renderer.save(fname)


if __name__ == "__main__":
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=None)
    colls = ll.all_collections()

    c = path.PathCollection()

    layer = 0
    for coll in colls:
        for p in coll:
            p.layer = str(layer)
            c.add(p)
        layer += 1

    c.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=90)
    save_wrapper(c, "composition62", "composition62_together")

    device.SimpleExportWrapper().ex(
        c,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        90,
        "composition62",
        c.hash(),
    )
