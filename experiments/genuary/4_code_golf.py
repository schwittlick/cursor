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
    loader = loader.Loader(directory=recs, limit_files=None)
    all_paths = loader.all_paths()

    sorter = filter.Sorter(param=filter.Sorter.SHANNON_DIRECTION_CHANGES, reverse=True)
    all_paths.sort(sorter)

    pc = path.PathCollection()

    counter = 0
    for p in all_paths[60:70]:
        p.layer = counter
        pc.add(p)

        counter += 1

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.DIY_PLOTTER,
        device.PaperSize.LANDSCAPE_A1,
        100,
        "genuary",
        f"4_code_golf_ALL_{pc.hash()}",
    )
