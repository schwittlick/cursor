import logging
import pathlib
import sys

import tkinter as tk
from tkinter import filedialog

import numpy as np
from PIL import Image
from tqdm import tqdm

from collection import Collection
from algorithm.color.copic import Copic
from data import DataDirHandler
from device import PlotterType
from export import ExportWrapper
from renderer.jpg import JpegRenderer
from algorithm.color.lib import convert_color_coordinates_to_collection


def select_file() -> pathlib.Path:
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()

    if not file_path:
        logging.warning("Not selected any file. Aborting")
        sys.exit(0)

    return pathlib.Path(file_path)


def do_bitmap_approximation(data: np.ndarray) -> Collection:
    color_coordinates = {}

    with tqdm(total=data.shape[0] * data.shape[1]) as pbar:
        for y in range(0, data.shape[0], 1):
            for x in range(0, data.shape[1], 1):
                color_value = data[y][x]
                if (color_value == (1.0, 1.0, 1.0)).all():
                    pbar.update(1)
                    continue
                closest_color = Copic().most_similar_rgb_kdtree(color_value)

                if closest_color.code not in color_coordinates.keys():
                    color_coordinates[closest_color.code] = [(y, x)]
                else:
                    color_coordinates[closest_color.code].append((y, x))

                pbar.update(1)

    collection = convert_color_coordinates_to_collection(color_coordinates, True, True)
    return collection


def export_jpg_preview(data: np.ndarray, collection: Collection, path: pathlib.Path) -> None:
    dir = DataDirHandler().jpg("color_interpolation")
    r = JpegRenderer(dir, w=data.shape[0], h=data.shape[1])
    r.add(collection)
    r.render()
    r.save(f"bitmap_approx_{path.name}")


def main_approximation():
    path = select_file()

    loaded = Image.open(path.as_posix())

    # only resize to make sure its landscape
    loaded = loaded.rotate(90, expand=True)
    loaded = loaded.convert('RGB')
    data = np.asarray(loaded)
    data = data / np.array(255)

    collection = do_bitmap_approximation(data)
    export_jpg_preview(data, collection, path)

    create_separate_layers_per_pen = False
    if create_separate_layers_per_pen:
        # use pen select as hack to use it as the layer
        for pa in collection:
            pa.layer = pa.pen_select - 1
            pa.pen_select = 1

    # the final resolution we want to export is 1 dot per ~40 units. Maybe 35-40 units is the sweet spot.

    # for postcards, just remove the padding at the A4 export

    # a4 = 252x168px
    # a3 = 504x336px
    wrapper = ExportWrapper(
        collection,
        PlotterType.HP_7550A_A4,  # PlotterType.HP_7550A_A4,HP_DM_RX_PLUS_A1
        14,  # 25mm - 11mm
        "color_interpolation",
        f"bitmap_approximator_{path.name}",
        keep_aspect_ratio=True,
        optimize=True)
    wrapper.fit()
    wrapper.ex()


if __name__ == '__main__':
    main_approximation()
    # create_fridge()
