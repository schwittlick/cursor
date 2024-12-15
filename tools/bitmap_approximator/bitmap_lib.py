import tkinter as tk
from tkinter import filedialog

import numpy as np
from tqdm import tqdm

from algorithm.color.copic import Copic
from algorithm.color.lib import convert_color_coordinates_to_collection

from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.export import ExportWrapper
from cursor.position import Position
from cursor.renderer.jpg import JpegRenderer
from cursor.timer import Timer


def select_files():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames()
    if not file_paths:
        print("No files selected. Exiting.")
    else:
        print(f"Number of files selected: {len(file_paths)}")
    return file_paths


def process_collection(coll, idx, fridge_collection):
    for pa in coll:
        _pa = pa.copy()
        _pa.pen_select = _pa.pen_select + idx * 2
        _pa.color = "black"
        _pa.width = 250
        fridge_collection.add(_pa)

        pa.layer = pa.pen_select - 1
        pa.pen_select = 1


def export_collection(coll, plotter, idx):
    wrapper = ExportWrapper(
        coll,
        plotter,
        14,
        "color_interpolation",
        f"bitmap_approximator_double_{idx}",
        keep_aspect_ratio=True,
        optimize=True,
        export_jpg_preview=True)
    wrapper.ex()


def generate_preview(fridge_collection, fridge_bb, preview_positions):
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
