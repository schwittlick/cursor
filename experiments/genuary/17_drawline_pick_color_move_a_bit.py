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

    ff = filter.DirectionChangeEntropyFilter(4.0, 4.5) # 2.0
    all_paths.filter(ff)



    for times in range(10):
        pc = path.PathCollection()
        x = 0
        for i in range(6):
            p = all_paths.random()
            for lines in range(40):
                pm = p.morph((x, 0), (x, 100))
                pm.layer = i
                x+= 5
                pc.add(pm)



        device.SimpleExportWrapper().ex(
            pc,
            device.PlotterType.HP_7595A,
            device.PaperSize.LANDSCAPE_A0,
            50,
            "genuary",
            f"17_drawline_pick_colormove_another_{times}",
        )
        pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=40)
        save_wrapper(pc, "genuary", f"17_drawline_pick_colormove_another_{times}")