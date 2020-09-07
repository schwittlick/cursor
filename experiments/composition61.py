from cursor import loader
from cursor import renderer
from cursor import data
from cursor import device

from cursor.filter import Sorter
from cursor.path import PathCollection

if __name__ == "__main__":
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=1)
    pcol = ll.all_paths()

    sorter = Sorter(param=Sorter.SHANNON_DIRECTION_CHANGES, reverse=False)
    pcol.sort(sorter)

    pres = PathCollection()

    for i in range(len(pcol)):
        p = pcol[i]

        pnew = p.morph((i, 0), (i, 100))
        pres.add(pnew)

    pres.fit(device.DrawingMachine.Paper.custom_42_56_landscape(), 40)

    gcode_folder = data.DataDirHandler().gcode("composition61")
    folder = data.DataDirHandler().jpg("composition61")
    gcode_renderer = renderer.GCodeRenderer(gcode_folder, z_down=4.5)
    jpeg_renderer = renderer.JpegRenderer(folder)

    fname = f"composition61_test_rev"

    jpeg_renderer.render(pres)
    jpeg_renderer.save(f"{fname}")
    gcode_renderer.render(pres)
    gcode_renderer.save(f"{fname}")
