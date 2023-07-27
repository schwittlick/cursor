from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.path import Path
from cursor.renderer import GCodeRenderer

if __name__ == "__main__":
    c = Collection()

    p = Path.from_tuple_list([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
    p.scale(10, 10)

    p.velocity = 100

    c.add(p)
    gcode_folder = DataDirHandler().gcode("simple_rect_gcode")
    gcode_renderer = GCodeRenderer(gcode_folder, z_down=4.5)
    gcode_renderer.render(c)
    gcode_renderer.save("simple")
