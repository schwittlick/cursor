import numpy as np

from cursor.collection import Collection
from cursor.device import PlotterType
from cursor.export import ExportWrapper
from cursor.hpgl.parser import HPGLParser
from cursor.path import Path
from cursor.tools.realtime_boilerplate import RealtimeDropin


def generate_rose_curve(n, d, resolution=1000):
    """
    Generates a rose curve with the given parameters.

    Parameters:
    - n: The numerator in the n/d parameter of the rose curve equation.
    - d: The denominator in the n/d parameter of the rose curve equation.
    - resolution: The number of points to generate for the curve.

    Returns:
    - A list of points (tuples) that make up the rose curve.
    """
    theta = np.linspace(0, 2 * np.pi * d, resolution)
    r = np.cos(n / d * theta)
    x = r * np.cos(theta)
    y = r * np.sin(theta)

    return list(zip(x, y))


if __name__ == "__main__":
    points = generate_rose_curve(3, 2, 100)
    velocities = [1, 2, 4, 8, 16, 32, 64, 128]
    pen_force = [1, 2, 3, 4, 5, 6, 7, 8]
    line_types = [(2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8)]

    collection = Collection()

    for x in range(8):
        # letter_collection = HPGLParser().parse(f"SP1;LB{velocities[x]}{chr(3)}")
        letter_collection = HPGLParser().parse(f"SP1;LB{line_types[x]}{chr(3)}")
        letter_collection.pen_select = 1
        letter_collection.scale(0.001, 0.001)
        letter_collection.translate(x * 2.2 - 0.5, -2.5)
        collection.add(letter_collection)

    for y in range(8):
        letter_collection = HPGLParser().parse(f"SP1;LB{pen_force[y]}{chr(3)}")
        letter_collection.pen_select = 1
        letter_collection.scale(0.001, 0.001)
        letter_collection.translate(-2.5, y * 2.2 - 0.5)
        collection.add(letter_collection)

    for y in range(8):
        for x in range(8):
            rose_curve = Path.from_tuple_list(points.copy())
            rose_curve.translate(x * 2.1, y * 2.1)

            rose_curve.pen_select = 1
            # rose_curve.velocity = velocities[x]
            rose_curve.line_type = line_types[x]
            rose_curve.pen_force = pen_force[y]
            collection.add(rose_curve)

    export = ExportWrapper(
        collection,
        PlotterType.HP_7550A_A3,
        0,
        "test_sheet",
        f"hp7550a_lt",
        keep_aspect_ratio=True)
    export.fit()
    export.ex()
