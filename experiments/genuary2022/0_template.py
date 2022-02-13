from cursor import device
from cursor import path

# from cursor import data
# from cursor import loader
# from cursor import misc
# from cursor import filter

# import math
# import numpy as np

if __name__ == "__main__":
    # recordings = data.DataDirHandler().recordings()
    # _loader = loader.Loader(directory=recordings, limit_files=1)
    # pc = _loader.all_paths()

    pc = path.PathCollection()

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.HP_7595A_A3,
        device.PaperSize.LANDSCAPE_A3,
        25,
        "folder",
        "suffix_name",
    )
