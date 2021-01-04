from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import renderer
from cursor import filter

import numpy

def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0, thickness=3)
    jpeg_renderer.save(fname)

def gen3(id):
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=1)
    colls = ll.all_paths()
    #fil = filter.EntropyMaxFilter(2.0, 2.0)
    #colls.filter(fil)

    p1 = colls.random()
    p2 = colls.random()

    pc = path.PathCollection()

    for i in numpy.arange(0, 1, 0.01):
        p3 = p1.interp(p2, i)
        p4 = p3.morph((i * 10, 0), (i * 10, 100))
        pc.add(p4)

    pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=40)
    save_wrapper(pc, "genuary", f"3_small_areas_of_symmetry{id}")

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.HP_7475A_A3,
        device.PaperSize.LANDSCAPE_A3,
        30,
        "genuary",
        "3_small_areas" + pc.hash()
    )

if __name__ == "__main__":
    for i in range(10):
        gen3(i)