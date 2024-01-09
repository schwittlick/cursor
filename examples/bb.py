from cursor.collection import Collection
from cursor.device import PlotterType, PaperSize
from cursor.export import ExportWrapper
from cursor.path import Path

if __name__ == "__main__":
    pc = Collection()
    p = Path.from_tuple_list([(0, 0), (-1, 0), (1, 1), (0, 1), (0, 0)])
    pc.add(p)

    wrapper = ExportWrapper(
        pc,
        PlotterType.ROLAND_DPX3300_A3,
        PaperSize.LANDSCAPE_A3,
        10,
        "bb_example",
        "bb",
    )
    wrapper.fit()
    wrapper.ex()
