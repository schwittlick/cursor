from cursor import loader
from cursor import renderer
from cursor import path

import os

def composition52(n):
    print(F"Creating Composition #52 with n={n}")
    p = os.path.abspath('../data/recordings/')
    l = loader.Loader(directory=p)
    rec = l.single(0)

    r = renderer.CursorGCodeRenderer()
    jpeg_renderer = renderer.JpegRenderer()

    coll = path.PathCollection(rec.resolution)

    xoffset = 64.22 * 8
    yoffset = 69.11 * 2

    single_path = rec[n]
    for i in range(int(1070 / 4)): #1042
        xfrom = 3.0 * i + xoffset
        yfrom = 0 + yoffset
        xto = 3.0 * i + xoffset
        yto = 727.5 * 2 + yoffset
        morphed = single_path.morph((xfrom, yfrom), (xto, yto))
        coll.add(morphed, rec.resolution)

    #bb = coll.bb()

    #coll.add(path.Path([path.TimedPosition(bb[0], bb[1]), path.TimedPosition(bb[2], bb[1])]), rec.resolution)
    #coll.add(path.Path([path.TimedPosition(bb[2], bb[1]), path.TimedPosition(bb[2], bb[3])]), rec.resolution)
    #coll.add(path.Path([path.TimedPosition(bb[2], bb[3]), path.TimedPosition(bb[0], bb[3])]), rec.resolution)
    #coll.add(path.Path([path.TimedPosition(bb[0], bb[3]), path.TimedPosition(bb[0], bb[1])]), rec.resolution)

    r.render([coll], 'composition52_double_' + str(n))
    jpeg_renderer.render([coll], rec.resolution, 'composition52_double_' + str(n))

if __name__ == '__main__':
    composition52(19)