from cursor import loader
from cursor import renderer
from cursor import path

import os

def composition52(n):
    print(F"Creating Composition #52 with n={n}")
    p = os.path.abspath('../data/recordings/')
    l = loader.Loader(directory=p)
    rec = l.single(0)

    r = renderer.CursorGCodeRenderer(z_down=3.0)
    jpeg_renderer = renderer.JpegRenderer()

    coll = path.PathCollection(rec.resolution)

    xoffset = 135.38
    yoffset = 132.3

    xspacing = 2.5
    manual_less_x = 20

    single_path = rec[n]
    for i in range(int(2138 / xspacing) - manual_less_x): #1042
        xfrom = xspacing * i + xoffset
        yfrom = yoffset
        xto = xspacing * i + xoffset
        yto = 1470 + yoffset
        morphed = single_path.morph((xfrom, yfrom), (xto, yto))
        coll.add(morphed, rec.resolution)

    print(coll.bb())

    #coll.add(path.Path([path.TimedPosition(bb[0], bb[1]), path.TimedPosition(bb[2], bb[1])]), rec.resolution)
    #coll.add(path.Path([path.TimedPosition(bb[2], bb[1]), path.TimedPosition(bb[2], bb[3])]), rec.resolution)
    #coll.add(path.Path([path.TimedPosition(bb[2], bb[3]), path.TimedPosition(bb[0], bb[3])]), rec.resolution)
    #coll.add(path.Path([path.TimedPosition(bb[0], bb[3]), path.TimedPosition(bb[0], bb[1])]), rec.resolution)

    r.render([coll], 'composition52_double_final_sp2.5_3.0_' + str(n))
    jpeg_renderer.render([coll], rec.resolution, 'composition52_double_final_sp2.5_down_3.0_' + str(n))

if __name__ == '__main__':
    composition52(19)