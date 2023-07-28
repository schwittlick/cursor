from cursor import misc
from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.path import Path
from cursor.device import PaperSize, Paper
from cursor.renderer import HPGLRenderer, GCodeRenderer

if __name__ == "__main__":
    c = Collection()
    out_bb = Paper.sizes[PaperSize.PHOTO_PAPER_240_178_LANDSCAPE]
    p = Path.from_tuple_list([(0, 0), (out_bb[0], 0), (out_bb[0], out_bb[1]), (0, out_bb[1]), (0, 0)])
    # c.add(p)

    y_elements = 6
    x_elements = 8

    for y in range(y_elements):
        for x in range(x_elements):
            _x = misc.map(x, 0, x_elements, 0, out_bb[0])
            _y = misc.map(y, 0, y_elements, 0, out_bb[1])
            # _x += (out_bb[0] / x_elements) * 0.5
            # _y += (out_bb[1] / y_elements) * 0.5
            path = Path.from_tuple_list([(_x, _y), (_x, _y)])
            path.laser_pwm = 100
            path.laser_amp = misc.map(x, 0, x_elements - 1, 0.01, 0.06)  # between 3 and 5 v
            path.laser_delay = misc.map(y, 0, y_elements - 1, 0.4, 2.0)  # between 0.2 and 1.0s of exposure
            c.add(path)

    p.velocity = 100

    gcode_folder = DataDirHandler().gcode("laser_benchmark")
    gcode_renderer = GCodeRenderer(gcode_folder)

    c.transform(BoundingBox(10, 10, out_bb[0] - 10, out_bb[1] - 10))
    c.scale(2.85714, 2.90572)

    gcode_renderer.render(c)
    gcode_renderer.save("rect_diy")
