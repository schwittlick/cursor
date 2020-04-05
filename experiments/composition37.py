from cursor import loader
from cursor import renderer
from cursor import path
from cursor import data
from cursor import device


def composition37(p0, p1, offset):
    gcode_renderer = renderer.GCodeRenderer("composition37", z_down=3.0)
    jpeg_renderer = renderer.JpegRenderer("composition37")

    coll = path.PathCollection()

    start = (100, 100)
    end = (400, 100)

    startbottom = (100, 600)
    endbottom = (400, 600)

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

    coll.fit(device.DrawingMachine.Paper.a0_landscape(), 200)

    print(coll.bb())

    gcode_renderer.render(coll, f"composition37_{offset}")
    jpeg_renderer.render(coll, f"composition37_{offset}")


if __name__ == "__main__":
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=5)
    all_paths = ll.all_paths()

    for i in range(1):
        print(f"Creating Composition #37 with offset={i}")
        p0 = all_paths[i]
        p1 = all_paths[i + 1]
        composition37(p0, p1, i)
