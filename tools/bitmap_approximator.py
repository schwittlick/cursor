import logging
import math
import pathlib
import sys

import tkinter as tk
from tkinter import filedialog

import numpy as np
from PIL import Image
from tqdm import tqdm

from cursor.collection import Collection
from cursor.algorithm.color.copic import Copic
from cursor.data import DataDirHandler
from cursor.device import PlotterType, MinmaxMapping
from cursor.export import ExportWrapper
from cursor.renderer.jpg import JpegRenderer
from cursor.algorithm.color.lib import convert_color_coordinates_to_collection
from timer import Timer


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


import random
from cursor.bb import BoundingBox
from cursor.position import Position


def create_fridge():
    fridge_collection: Collection = Collection()
    fridge_bb = MinmaxMapping.maps[PlotterType.HP_DM_RX_PLUS_A1]
    collections = []
    placed_bbs = []
    preview_positions = []
    for _ in range(16):
        path = select_file()

        loaded = Image.open(path.as_posix())
        loaded = loaded.rotate(90, expand=True)
        loaded = loaded.convert('RGB')
        data = np.asarray(loaded)
        data = data / np.array(255)

        collection = do_bitmap_approximation(data)
        collection.scale(85 / 2, 85 / 2)

        rotation_angle = random.uniform(0, 360)
        collection.rot(rotation_angle * (math.pi / 180))

        max_attempts = 100
        for _ in range(max_attempts):
            padding = 200
            max_x = fridge_bb.x2 - collection.bb().w - padding
            max_y = fridge_bb.y2 - collection.bb().h - padding
            random_x = random.uniform(fridge_bb.x + padding, max_x)
            random_y = random.uniform(fridge_bb.y + padding, max_y)

            temp_collection = collection.copy()
            temp_collection.move_to_origin()
            temp_collection.translate(random_x, random_y)
            temp_bb = temp_collection.bb()

            if all(not temp_bb.intersects(placed_bb) for placed_bb in placed_bbs):
                collection = temp_collection
                placed_bbs.append(temp_bb)
                collections.append(collection)
                break
        else:
            print(f"Warning: Could not place collection without overlap after {max_attempts} attempts.")

    for idx, coll in enumerate(collections):
        create_separate_layers_per_pen = True
        if create_separate_layers_per_pen:
            # use pen select as hack to use it as the layer
            for pa in coll:
                _pa = pa.copy()
                _pa.pen_select = _pa.pen_select + idx * 2
                _pa.color = "black"
                _pa.width = 250
                fridge_collection.add(_pa)

                pa.layer = pa.pen_select - 1
                pa.pen_select = 1

        wrapper = ExportWrapper(
            coll,
            PlotterType.HP_DM_RX_PLUS_A1,
            14,
            "color_interpolation",
            f"bitmap_approximator_double_{idx}",
            keep_aspect_ratio=True,
            optimize=True,
            export_jpg_preview=True)
        wrapper.ex()

    jpeg_folder = DataDirHandler().jpg("color_interpolation")
    fridge_collection.transform(BoundingBox(0, 0, fridge_bb.w, fridge_bb.h))
    for pa in fridge_collection:
        pos = Position(pa[0].x, pa[0].y)
        pos.color = "black"
        pos.radius = 10
        preview_positions.append(pos)
    jpeg_renderer = JpegRenderer(jpeg_folder, w=int(fridge_bb.w), h=int(fridge_bb.h))
    jpeg_renderer.background((255, 255, 255))
    jpeg_renderer.add(preview_positions)
    jpeg_renderer.render()
    jpeg_renderer.save(f"bitmap_approximator_preview_{Timer.timestamp()}")


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
        PlotterType.HP_7550A_A4,
        14,  # 25mm - 11mm
        "color_interpolation",
        f"bitmap_approximator_{path.name}",
        keep_aspect_ratio=True,
        optimize=True)
    wrapper.fit()
    wrapper.ex()


if __name__ == '__main__':
    # main_approximation()
    create_fridge()
