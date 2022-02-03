from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import filter
from cursor import misc

if __name__ == "__main__":
    p = data.DataDirHandler().recordings()
    files = ["1640346795.269127_compressed"]
    ll = loader.Loader(directory=p, limit_files=files)
    colls = ll.all_collections()

    c = path.PathCollection()

    layer = 0
    for coll in colls:
        for p in coll:
            p.layer = str(layer)
            c.add(p)
        layer += 1

    c.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=20)

    #bb = path.BoundingBox(500, 400, 1400, 900)
    #f = filter.BoundingBoxFilter(bb)
    #c.filter(f)

    #misc.save_wrapper_jpeg(c, "composition62", "composition62_together", 4.0, 1.0)

    device.SimpleExportWrapper().ex(
        c,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        20,
        "composition62",
        c.hash(),
    )
