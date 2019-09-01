from cursor import loader
from cursor import renderer
from cursor import path
from cursor import data


def composition37(p0, p1, offset):
    r = renderer.CursorGCodeRenderer('composition37', z_down=3.0)
    jpeg_renderer = renderer.JpegRenderer('composition37')

    coll = path.PathCollection(rec.resolution)

    start = (100, 100)
    end = (400, 100)

    startbottom = (100, 600)
    endbottom = (400, 600)

    toppath = p0.morph(start, end)
    bottompath = p0.morph(endbottom, startbottom)

    bottompath.reverse()

    coll.add(toppath, rec.resolution)
    coll.add(bottompath, rec.resolution)

    p1_morphed = p1.morph(toppath[0].pos(), bottompath[0].pos())
    coll.add(p1_morphed, rec.resolution)

    for i in range(len(toppath)):
        st = toppath[i]
        en = bottompath[i]
        newpath = p1.morph(en.pos(), st.pos())
        coll.add(newpath, rec.resolution)

    print(coll.bb())

    #r.render(coll, F"composition37_{offset}")
    jpeg_renderer.render(coll, F"composition37_{offset}")


if __name__ == '__main__':
    p = data.DataHandler().recordings()
    l = loader.Loader(directory=p, limit_files=1)
    rec = l.single(0)
    all_paths = l.all_paths()

    #print(len(all_paths))
    for i in range(10):
        print(F"Creating Composition #37 with offset={i}")
        p0 = all_paths[i]
        p1 = all_paths[i + 1]
        composition37(p0, p1, i)