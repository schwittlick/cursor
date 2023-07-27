from cursor.collection import Collection
from cursor.grbl.parser import GCODEParser


def test_gcode_parser():
    parser = GCODEParser()

    gcode = []
    gcode.append("G01 Z0.0 F1000")
    gcode.append("G01 X0.00 Y0.00 F2000")
    gcode.append("G01 X0.00 Y0.00 F2000")
    gcode.append("G01 X0.00 Y-0.00 F2000")
    gcode.append("G01 Z4.5 F1000")
    gcode.append("G01 X0.00 Y-0.00 F2000")
    gcode.append("G01 X10.00 Y-0.00 F2000")
    gcode.append("G01 X10.00 Y-10.00 F2000")
    gcode.append("G01 X0.00 Y-10.00 F2000")
    gcode.append("G01 X0.00 Y-0.00 F2000")
    gcode.append("G01 Z0.0 F1000")
    gcode.append("G01 X0.00 Y0.00 F2000")

    c = parser.parse(gcode)

    expected = Collection.from_tuples(
        [[(0.0, -0.0), (10.0, -0.0),
          (10.0, -10.0), (0.0, -10.0), (0.0, -0.0)]])

    assert c == expected
