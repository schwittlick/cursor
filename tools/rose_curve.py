import random

import numpy as np

from cursor.collection import Collection
from cursor.device import PlotterType
from cursor.export import ExportWrapper
from cursor.hpgl.parser import HPGLParser
from cursor.path import Path


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
    points = generate_rose_curve(2, 3, 100)
    velocities = [1, 2, 4, 8, 16, 32, 64, 128]
    pen_force = [1, 2, 3, 4, 5, 6, 7, 8]
    # line_types = [(1, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8)]
    line_type_x = [8, 7, 6, 5, 4, 3, 2, 1, -1, -2, -3, -4, -5, -6, -7, -8]
    line_type_y = [1, 2, 3, 4, 5, 6, 7, 8]
    line_types = [(random.randint(2, 8), random.randint(2, 8)) for _ in range(8)]

    collection = Collection()

    for x in range(15):
        # letter_collection = HPGLParser().parse(f"SP1;LB{velocities[x]}{chr(3)}")
        letter_collection = HPGLParser().parse(f"SP1;LBLT1={line_type_x[x]};")
        letter_collection.pen_select = 1
        letter_collection.scale(0.001, 0.001)
        letter_collection.translate(x * 2.2 - 0.5, -2.5)
        collection.add(letter_collection)

    for y in range(8):
        # letter_collection = HPGLParser().parse(f"SP1;LBVS{velocities[y]}")
        letter_collection = HPGLParser().parse(f"SP1;LBLT2={line_type_y[y]};")
        letter_collection.pen_select = 1
        letter_collection.scale(0.001, 0.001)
        letter_collection.translate(-2.5, y * 2.2 - 0.5)
        collection.add(letter_collection)

    for y in range(8):
        for x in range(15):
            points = generate_rose_curve(random.randint(1, 8), random.randint(1, 8), 200)
            rose_curve = Path.from_tuple_list(points.copy())
            rose_curve.resample(0.05)
            rose_curve.translate(x * 2.1, y * 2.1)

            lt = (line_type_x[x], line_type_y[y])

            rose_curve.pen_select = 1
            rose_curve.velocity = 5  # velocities[x]
            rose_curve.line_type = lt  # line_types[x]
            rose_curve.pen_force = 8  # pen_force[y]
            collection.add(rose_curve)

    export = ExportWrapper(
        collection,
        PlotterType.HP_7550A_A3,
        0,
        "test_sheet",
        "hp7550a_lt_all",
        keep_aspect_ratio=True)
    export.fit()
    export.ex()
