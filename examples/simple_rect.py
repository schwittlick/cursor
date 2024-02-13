from cursor.collection import Collection
from cursor.device import PlotterType
from cursor.export import ExportWrapper
from cursor.path import Path

if __name__ == "__main__":
    c = Collection()

    p = Path.from_tuple_list([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
    p.pen_select = 1
    p.velocity = 50

    c.add(p)

    wrapper = ExportWrapper(
        c,
        PlotterType.MUTOH_XP500_500x297mm,
        0,
        "simple_rect_example",
        "test")
    wrapper.fit()
    wrapper.ex()
