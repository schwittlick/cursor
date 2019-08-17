from cursor import loader
from cursor import renderer
from cursor import path

import os


def composition55(p0, p1, offset):
    r = renderer.CursorGCodeRenderer(z_down=3.0)
    jpeg_renderer = renderer.JpegRenderer()

    coll = path.PathCollection(rec.resolution)

    xoffset = 142.5
    yoffset = 147

    xmaxsize = 2111.85
    ymaxsize = 1452

    start = (xoffset, yoffset)
    end = (xmaxsize, yoffset)

    startbottom = (xoffset, ymaxsize + yoffset)
    endbottom = (xmaxsize, ymaxsize + yoffset)


    xspacing = 2.5

    lines = 1500
    #while coll.bb()[2] < 2138:
    for i in range(lines):
        perc = (1.0 / lines) * i
        interped = p0.interp(p1, perc)
        currstartx = path.Path.mix(start[0], end[0], perc)
        print(currstartx)
        currstarty = path.Path.mix(start[1], end[1], perc)
        currendx = path.Path.mix(startbottom[0], endbottom[0], perc)
        currendy = path.Path.mix(startbottom[1], endbottom[1], perc)

        curr_start = (currstartx, currstarty)
        curr_end = (currendx, currendy)
        morphed = interped.morph(curr_start, curr_end)
        coll.add(morphed, rec.resolution)

    print(coll.bb())

    r.render([coll], F"composition55_{offset}")
    try:
        jpeg_renderer.render([coll], F"composition55_{offset}_high2", 5.0)
    except MemoryError as me:
        print("Memory error ignored..")
        return


if __name__ == '__main__':

    p = os.path.abspath('../cursor/data/recordings/')
    l = loader.Loader(directory=p)
    rec = l.single(0)
    all_paths = l.all_paths()

    print(len(all_paths))
    for i in range(1, 2):
        print(F"Creating Composition #55 with offset={i}")
        p0 = all_paths[i]
        p1 = all_paths[i + 1]
        composition55(p0, p1, i)
