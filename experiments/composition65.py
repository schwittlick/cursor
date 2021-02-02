from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import filter
from cursor import renderer

def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0, thickness=3)
    jpeg_renderer.save(fname)


if __name__ == "__main__":
    recs = data.DataDirHandler().recordings()
    loader = loader.Loader(directory=recs, limit_files=10)
    all_paths = loader.all_paths()

    sorter1 = filter.DistanceFilter(0.05)
    all_paths.filter(sorter1)

    #sorter2 = filter.MaxPointCountFilter(50)
    #all_paths.filter(sorter2)

    pc = path.PathCollection()

    counter = 0
    for p in all_paths:
        #p.layer = counter
        pc.add(p)

        counter += 1

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.DIY_PLOTTER,
        device.PaperSize.LANDSCAPE_A1,
        60,
        "composition65",
        f"c65{pc.hash()}",
    )