import math
import random

import numpy as np
from PIL import Image

from bitmap_lib import select_files, process_collection, export_collection, generate_preview, do_bitmap_approximation
from collection import Collection
from device import MinmaxMapping


def create_fridge(plotter):
    fridge_collection = Collection()
    fridge_bb = MinmaxMapping.maps[plotter]
    collections = []
    placed_bbs = []
    preview_positions = []

    file_paths = select_files()
    if not file_paths:
        return

    for path in file_paths:
        collection = process_image(path)
        place_collection(collection, fridge_bb, placed_bbs, collections)

    print(f"Successfully placed {len(collections)} out of {len(file_paths)} images")

    for idx, coll in enumerate(collections):
        process_collection(coll, idx, fridge_collection)
        export_collection(coll, plotter, idx)

    generate_preview(fridge_collection, fridge_bb, preview_positions)


def process_image(path):
    loaded = Image.open(path).rotate(90, expand=True).convert("RGB")
    data = np.asarray(loaded) / 255
    collection = do_bitmap_approximation(data)
    # hardcoded styling for copic pen nib sizes
    # this means that each pixel is drawn about 1mm apart from each other (1mm==40 hpgl units)
    collection.scale(40, 40)
    rotation_angle = random.uniform(0, 360)
    collection.rot(rotation_angle * (math.pi / 180))
    return collection


def place_collection(collection, fridge_bb, placed_bbs, collections):
    max_attempts = 200
    for _ in range(max_attempts):
        if try_place_collection(collection, fridge_bb, placed_bbs):
            collections.append(collection)
            return
    print(f"Warning: Could not place collection without overlap after {max_attempts} attempts.")


def try_place_collection(collection, fridge_bb, placed_bbs):
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
        collection.move_to_origin()
        collection.translate(random_x, random_y)
        placed_bbs.append(temp_bb)
        return True
    return False
