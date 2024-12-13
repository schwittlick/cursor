from bitmap_lib import select_files, generate_preview, export_collection, process_collection, \
    do_bitmap_approximation
from cursor.collection import Collection
from device import MinmaxMapping

from PIL import Image
import numpy as np


def process_image(path):
    loaded = Image.open(path).rotate(90, expand=True).convert('RGB')
    data = np.asarray(loaded) / 255
    collection = do_bitmap_approximation(data)

    # hardcoded styling for copic pen nib sizes
    # this means that each pixel is drawn about 1mm apart from each other (1mm==40 hpgl units)
    collection.scale(40, 40)
    return collection


def create_grid(plotter):
    fridge_collection = Collection()
    fridge_bb = MinmaxMapping.maps[plotter]
    collections = []

    file_paths = select_files()
    if not file_paths or len(file_paths) != 4:
        print("Please select exactly 4 files.")
        return

    for path in file_paths:
        collection = process_image(path)
        collections.append(collection)

    grid_width = 2
    grid_height = 2
    cell_width = fridge_bb.w / grid_width
    cell_height = fridge_bb.h / grid_height

    for i, collection in enumerate(collections):
        row = i // grid_width
        col = i % grid_width

        # Scale the collection to fit within the cell
        scale_factor = min(cell_width / collection.bb().w, cell_height / collection.bb().h)
        collection.scale(scale_factor, scale_factor)

        # Calculate the position to center the collection within its cell
        x_offset = col * cell_width + (cell_width - collection.bb().w) / 2
        y_offset = row * cell_height + (cell_height - collection.bb().h) / 2

        collection.translate(x_offset, y_offset)
        fridge_collection.add(collection)

        process_collection(collection, i, fridge_collection)
        export_collection(collection, plotter, i)

    generate_preview(fridge_collection, fridge_bb, [])

    print(f"Successfully placed {len(collections)} images in a 2x2 grid")
