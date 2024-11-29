import logging
import pathlib
import sys

import tkinter as tk
from tkinter import filedialog

import numpy as np
from PIL import Image
from tqdm import tqdm

from cursor.collection import Collection
from cursor.path import Path
from cursor.algorithm.color.copic import Copic
from cursor.data import DataDirHandler
from cursor.device import PlotterType
from cursor.export import ExportWrapper
from cursor.renderer.jpg import JpegRenderer
from cursor.algorithm.color.lib import convert_color_coordinates_to_collection


def add_legende(collection: Collection):
    p1 = Path()
    p1.pen_select = 1
    p1.add(0, 0)


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()

    if not file_path:
        logging.warning("Not selected any file. Aborting")
        sys.exit(0)

    path = pathlib.Path(file_path)

    loaded = Image.open(path.as_posix())

    loaded = loaded.rotate(90, expand=True)

    do_resize = False

    if do_resize:
        width = 126
        wpercent = (width / float(loaded.size[0]))
        height = int((float(loaded.size[1]) * float(wpercent)))
        loaded = loaded.resize((width, height))
        logging.info(f"Resized to {width}x{height}")
    loaded = loaded.convert('RGB')
    data = np.asarray(loaded)
    data = data / np.array(255)

    color_coordinates = {}

    with tqdm(total=data.shape[0] * data.shape[1]) as pbar:
        for y in range(0, data.shape[0], 1):
            for x in range(0, data.shape[1], 1):
                color_value = data[y][x]
                if (color_value == (1.0, 1.0, 1.0)).all():
                    continue
                closest_color = Copic().most_similar_rgb_kdtree(color_value)

                if closest_color.code not in color_coordinates.keys():
                    color_coordinates[closest_color.code] = [(y, x)]
                else:
                    color_coordinates[closest_color.code].append((y, x))

                pbar.update(1)

    collection = convert_color_coordinates_to_collection(color_coordinates, True)

    add_legende(collection)

    dir = DataDirHandler().jpg("color_interpolation")
    r = JpegRenderer(dir, w=data.shape[0], h=data.shape[1])
    r.add(collection)
    r.render()
    r.save(f"bitmap_approximator_{path.name}")

    wrapper = ExportWrapper(
        collection,
        PlotterType.HP_7550A_A4,
        25,
        "color_interpolation",
        f"bitmap_approximator_{path.name}",
        keep_aspect_ratio=True,
        optimize=True)
    wrapper.fit()
    wrapper.ex()
