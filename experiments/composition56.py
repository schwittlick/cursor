from cursor import loader
from cursor import renderer
from cursor import path
from cursor import filter
from cursor import data

def composition56(nr, pathlist):
    gcode_renderer = renderer.CursorGCodeRenderer('composition56', z_down=3.0)
    jpeg_renderer = renderer.JpegRenderer('composition56')
    xoffset = 142.5
    yoffset = 147

    xmaxsize = 2111.85
    ymaxsize = 1452

    xspacing = 2
    coll = path.PathCollection(rec.resolution)


    for p in pathlist:
        for i in range(150):
            xfrom = xspacing * i + xoffset
            yfrom = yoffset
            xto = xspacing * i + xoffset
            yto = 1452 + yoffset
            morphed = p.morph((xfrom, yfrom), (xto, yto))
            coll.add(morphed, rec.resolution)

        xoffset += 420

    #print()
    #bb = path.BoundingBox(0, 0, xmaxsize + 142.5, ymaxsize + 147)
    #print(bb)
    #if bb.inside(coll):
    print(F"rendering {nr}, {coll.bb()}")
    gcode_renderer.render(coll, F"composition56_{nr}")
    jpeg_renderer.render(coll, F"composition56_{nr}")

if __name__ == '__main__':
    p = data.DataHandler().recordings()
    l = loader.Loader(directory=p, limit_files=None)
    rec = l.single(0)
    all_paths = l.all_paths()

    entropy_filter = filter.EntropyFilter(1.2, 1.2)
    all_paths.filter(entropy_filter)

    distance_filter = filter.DistanceFilter(100, rec.resolution)
    all_paths.filter(distance_filter)

    for i in range(50):
        r1 = all_paths.random()
        r2 = all_paths.random()
        r3 = all_paths.random()
        r4 = all_paths.random()
        r5 = all_paths.random()

        composition56(i, [r1, r2, r3, r4, r5])