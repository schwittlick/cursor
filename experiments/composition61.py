from cursor import loader
from cursor import renderer
from cursor import data
from cursor import device
from cursor import filter

from cursor.filter import Sorter
from cursor.path import PathCollection

if __name__ == "__main__":
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=10)
    pcol = ll.all_paths()
    #pcol.clean()

    entropy_filter = filter.EntropyMaxFilter(3.5, 3.5)
    #pcol.filter(entropy_filter)

    mincount_filter = filter.MinPointCountFilter(40)
    pcol.filter(mincount_filter)

    maxtraveldistance_filter = filter.DistanceFilter(0.06)
    pcol.filter(maxtraveldistance_filter)

    sorter = Sorter(param=Sorter.SHANNON_DIRECTION_CHANGES, reverse=False)
    pcol.sort(sorter)

    coll = PathCollection()

    for i in range(len(pcol)):
        p = pcol[i]

        pnew = p.morph((i, 0), (i, 100))
        coll.add(pnew)

    folder = data.DataDirHandler().jpg("composition61")
    jpeg_renderer = renderer.JpegRenderer(folder)

    fname = f"composition61_test_rev2"

    coll.fit(device.DrawingMachine.Paper.custom_42_56_landscape(), 40)
    jpeg_renderer.render(coll)
    jpeg_renderer.save(f"{fname}")

    coll.fit(
        device.RolandDPX3300.Paper.custom_30_30(),
        machine=device.RolandDPX3300(),
        padding_mm=50,
        center_point=(-880, 600),
    )

    hpgl_folder = data.DataDirHandler().hpgl("composition61")
    hpgl_renderer = renderer.HPGLRenderer(hpgl_folder)
    separate_layers = coll.get_layers()
    for layer, pc in separate_layers.items():
        hpgl_renderer.render(pc)
        hpgl_renderer.save(f"{fname}_{layer}")

    exit(0)
    coll.fit(device.DrawingMachine.Paper.custom_42_56_landscape(), 40)

    gcode_folder = data.DataDirHandler().gcode("composition61")
    folder = data.DataDirHandler().jpg("composition61")
    gcode_renderer = renderer.GCodeRenderer(gcode_folder, z_down=4.5)
    jpeg_renderer = renderer.JpegRenderer(folder)




    gcode_renderer.render(coll)
    gcode_renderer.save(f"{fname}")
