import logging
import pathlib
import sys
import tkinter as tk
from tkinter import filedialog

import numpy as np
from PIL import Image

from bitmap_lib import do_bitmap_approximation
from cursor import Position
from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.device import PlotterType
from cursor.export import ExportWrapper
from cursor.renderer.jpg import JpegRenderer


def main_approximation():
    path = select_file()

    loaded = Image.open(path.as_posix())

    # Rotate only if the image is in portrait orientation
    if loaded.height < loaded.width:
        loaded = loaded.rotate(90, expand=True)

    loaded = loaded.convert("RGB")
    data = np.asarray(loaded)
    data = data / np.array(255)

    collection = do_bitmap_approximation(data)
    export_jpg_preview(data, collection, path)

    create_separate_layers_per_pen = False
    if create_separate_layers_per_pen:
        # use pen select as hack to use it as the layer
        for pa in collection:
            pa.layer = (int(pa.layer) * 8) + pa.pen_select - 1
            pa.pen_select = 1

    # a4 = 252x168px
    # a3 = 504x336px
    # a1 = 672x512 (a bit tighter would be 788x600
    wrapper = ExportWrapper(
        collection,
        PlotterType.HP_7550A_A3,  # PlotterType.HP_7550A_A4,HP_DM_RX_PLUS_A1
        15,  # 25mm - 11mm # for postcards in a4, set padding to 0 and add legende on all four sides, use 25 for a1
        "color_interpolation",
        f"bitmap_approximator_{path.name}",
        keep_aspect_ratio=True,
        optimize=True,
    )
    wrapper.fit()
    wrapper.ex()


def select_file() -> pathlib.Path:
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()

    if not file_path:
        logging.warning("Not selected any file. Aborting")
        sys.exit(0)

    return pathlib.Path(file_path)


def export_jpg_preview(data: np.ndarray, collection: Collection, path: pathlib.Path) -> None:
    dir = DataDirHandler().jpg("color_interpolation")
    r = JpegRenderer(dir, w=data.shape[0], h=data.shape[1])
    for pa in collection:
        pos = Position(pa[0].x, pa[0].y)
        col = pa.color
        pos.color = col
        pos.radius = 1
        r.add(pos.copy())
    # r.add(collection)
    r.render()
    r.save(f"bitmap_approx_{path.name}")
