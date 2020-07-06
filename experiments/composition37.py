from cursor import loader
from cursor import renderer
from cursor import filter
from cursor import path
from cursor import data
from cursor import device


def composition37(p0, p1, offset):
    gcode_folder = data.DataDirHandler().gcode("composition37")
    folder = data.DataDirHandler().jpg("composition37")
    gcode_renderer = renderer.GCodeRenderer(gcode_folder, z_down=3.0)
    jpeg_renderer = renderer.JpegRenderer(folder)

    coll = path.PathCollection()

    start = (100, 100)
    end = (100, 700)

    startbottom = (400, 100)
    endbottom = (400, 700)

    toppath = p0.morph(start, end)
    bottompath = p0.morph(endbottom, startbottom)

    bottompath.reverse()

    coll.add(toppath)
    coll.add(bottompath)

    p1_morphed = p1.morph(toppath[0].pos(), bottompath[0].pos())
    coll.add(p1_morphed)

    for i in range(len(toppath)):
        st = toppath[i]
        en = bottompath[i]
        newpath = p1.morph(en.pos(), st.pos())
        coll.add(newpath)

    print(coll.bb())

    coll.fit(device.DrawingMachine.Paper.a1_landscape(), 100)

    print(coll.bb())

    fname = f"composition37_broken_{offset}"
    gcode_renderer.render(coll)
    gcode_renderer.save(fname)
    jpeg_renderer.render(coll)
    jpeg_renderer.save(fname)


if __name__ == "__main__":
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=15)
    all_paths = ll.all_paths()

    entropy_filter = filter.EntropyFilter(2.5, 2.5)
    all_paths.filter(entropy_filter)

    mincount_filter = filter.MinPointCountFilter(20)
    all_paths.filter(mincount_filter)

    maxcount_filter = filter.MaxPointCountFilter(100)
    all_paths.filter(maxcount_filter)

    for i in range(100):
        import random
        r = random.randint(0, len(all_paths) - 1)
        print(f"Creating Composition #37 with offset={r}")
        p0 = all_paths[r]
        p1 = all_paths[r + 1]
        composition37(p0, p1, i)
