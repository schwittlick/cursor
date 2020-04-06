from cursor import loader
from cursor import renderer
from cursor.path import TimedPosition as TP
from cursor.path import PathCollection
from cursor.path import Path
from cursor import data
from cursor import device


def main():
    gcode_renderer = renderer.GCodeRenderer("square_test", z_down=3.0)
    jpeg_renderer = renderer.JpegRenderer("square_test")

    coll = PathCollection()

    p = Path()
    p.add(0, 0)
    p.add(1, 1)

    coll.fit(device.DrawingMachine.Paper.a1_landscape(), 50)

    gcode_renderer.render(coll)
    jpeg_renderer.render(coll)

    gcode_renderer.save(f"straight_lines_{coll.hash()}")
    jpeg_renderer.save(f"straight_lines_{coll.hash()}")


if __name__ == "__main__":
    main()
