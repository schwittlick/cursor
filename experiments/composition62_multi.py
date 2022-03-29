from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import filter


def load(fn) -> path.PathCollection:
    ll = loader.Loader(directory=data.DataDirHandler().recordings(), limit_files=[fn])
    return ll.all_paths()


if __name__ == "__main__":
    files = [
        "1642172638.032577_compressed",
        "1642172275.779894_compressed",
        "1634846539.565324_compressed",
        "1585761724.491215_compressed",
        "1587806590.579923_compressed",
        "1594372891.160352_compressed",
        "1606479425.800735_compressed",
    ]
    colls = path.PathCollection()
    count = 1
    for f in files:
        c = load(f)
        c.limit()
        for p in c:
            p1 = p
            p1.pen_select = count
            colls.add(p1)
        count += 1


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
        "composition62_multi",
        colls.hash(),
    )
