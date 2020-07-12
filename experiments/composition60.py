from cursor import loader
from cursor import renderer
from cursor import filter
from cursor import path
from cursor import data
from cursor import device

import random

if __name__ == "__main__":
    """
    c60
    1. take 2 lines, make a square of them, parallel sides the same line
    2. make a grid of them
    3. offset the grid elements a little here and there
    4. render 80% black and 20% with other colours
    5. this means 3 diff gcode files
    """
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=30)
    all_paths = ll.all_paths()

    entropy_filter_min = filter.EntropyMinFilter(0.1, 0.1)
    all_paths.filter(entropy_filter_min)

    entropy_filter_max = filter.EntropyMaxFilter(1.5, 1.5)
    all_paths.filter(entropy_filter_max)

    point_filter = filter.MaxPointCountFilter(100)
    all_paths.filter(point_filter)

    point_filter2 = filter.MinPointCountFilter(6)
    all_paths.filter(point_filter2)

    for i in range(10):
        gcode_folder = data.DataDirHandler().gcode("composition60")
        folder = data.DataDirHandler().jpg("composition60")
        gcode_renderer = renderer.GCodeRenderer(gcode_folder, z_down=3.5)
        jpeg_renderer = renderer.JpegRenderer(folder)

        p1 = all_paths.random()
        p2 = all_paths.random()

        print(i)
        print(p1)
        print(p2)

        xsize = 50
        ysize = 50

        coll = path.PathCollection()

        for y in range(7):
            for x in range(10):
                p1 = all_paths.random()
                print(p1)

                posx = x * xsize + (x*20) + random.uniform(-50, 50)
                posy = y * ysize + (y*20) + random.uniform(-50, 50)
                _p1 = p1.morph((posx, posy), (posx + xsize, posy)) # top
                _p2 = p1.morph((posx, posy + ysize), (posx + xsize, posy + ysize)) # bottom
                _p3 = p1.morph((posx, posy), (posx, posy + ysize)) # left
                _p4 = p1.morph((posx + xsize, posy), (posx + xsize, posy + ysize)) # right

                coll.add(_p1)
                coll.add(_p2)
                coll.add(_p3)
                coll.add(_p4)

                if random.randint(0, 10) < 2:
                    counter = 0
                    for p in _p1:
                        bottom_connection = _p2[counter]
                        counter += 1

                        newpath = _p3.morph(p, bottom_connection)

                        coll.add(newpath)

        coll.fit(device.DrawingMachine.Paper.custom_42_56_landscape(), 40)
        jpeg_renderer.render(coll)
        jpeg_renderer.save(f"composition60_{i}")
        gcode_renderer.render(coll)
        gcode_renderer.save(f"composition60_{i}")