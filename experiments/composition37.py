from cursor import loader
from cursor import renderer
from cursor import path

import os


def composition37(p0, p1, offset):
    r = renderer.CursorGCodeRenderer(z_down=3.0)
    jpeg_renderer = renderer.JpegRenderer()

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

    for i in range(len(toppath)):
        st = toppath[i]
        en = bottompath[i]
        newpath = p1.morph(en.pos(), st.pos())
        coll.add(newpath, rec.resolution)

    print(coll.bb())

    #r.render([coll], F"composition37_{offset}")
    jpeg_renderer.render([coll], coll.bb(), F"composition37_{offset}")


if __name__ == '__main__':

    p = os.path.abspath('../cursor/data/recordings/')
    l = loader.Loader(directory=p)
    rec = l.single(0)
    all_paths = l.all_paths()

    print(len(all_paths))
    for i in range(50):
        print(F"Creating Composition #37 with offset={i}")
        p0 = all_paths[i]
        p1 = all_paths[i + 1]
        composition37(p0, p1, i)
    #composition37(23)