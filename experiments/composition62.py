from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import filter


if __name__ == "__main__":
    p = data.DataDirHandler().recordings()
    files = ["1644923397.358839_compressed"]
    ll = loader.Loader(directory=p, limit_files=files)
    colls = ll.all_paths()

    colls.limit()
    c = path.PathCollection()

    #layer = 0
    #for p in colls:
    #    add = True
    #    for pos in p:
    #        if pos.x > 1.1:
    #            add = False
    #    # p.layer = str(layer)
    #    if add:
    #        c.add(p)
    # layer += 1

    # c.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=20)

    # bb = path.BoundingBox(500, 400, 1400, 900)
    # f = filter.BoundingBoxFilter(bb)
    # c.filter(f)


    # misc.save_wrapper_jpeg(c, "composition62", "composition62_together", 4.0, 1.0)

    device.SimpleExportWrapper().ex(
        colls,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        20,
        "composition62",
        c.hash(),
    )
