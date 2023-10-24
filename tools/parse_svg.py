from cursor.data import DataDirHandler
from cursor.data import DateHandler
from cursor.device import PlotterType, PaperSize
from cursor.export import ExportWrapper
from cursor.renderer.realtime import RealtimeRenderer
from cursor.sorter import SortParameter, Sorter
from cursor.path import Path
from cursor.collection import Collection

import arcade
import random
import pymsgbox
import wasabi
import xml.etree.ElementTree as ET

log = wasabi.Printer()


def main():
    fi = "export_220606_115729"
    f = DataDirHandler().data_dir / "julien_svgs" / f"{fi}.svg"

    tree = ET.parse(f.as_posix())
    root = tree.getroot()

    c = Collection()
    for child in root.findall("line"):
        x1 = float(child.attrib["x1"])
        y1 = float(child.attrib["y1"])
        x2 = float(child.attrib["x2"])
        y2 = float(child.attrib["y2"])
        p = Path.from_tuple_list([(x1, y1), (x2, y2)])
        c.add(p)

    def sort_all(rr: RealtimeRenderer):
        sorter = Sorter(param=SortParameter.DISTANCE, reverse=True)
        c.sort(sorter)
        rr.clear_list()
        rr.add_collection(c, 1.5)

    def next_key(rr: RealtimeRenderer):
        for i in range(100):
            if r.index > len(c):
                return
            rr.add_path(c[r.index], 1.5, random.choice(rr.colors))
            r.index += 1

    def export(rr: RealtimeRenderer):
        ExportWrapper().ex(
            c,
            PlotterType.ROLAND_DPX3300,
            PaperSize.LANDSCAPE_A1,
            30,
            "svg2hpgl",
            f"{rr.title}",
        )

    def save_pickle(rr: RealtimeRenderer):
        c.save_pickle(f"{rr.title}.pickle")

    def screenshot(renderer: RealtimeRenderer):
        suffix = pymsgbox.prompt("suffix", default="")
        fn = (
                DataDirHandler().jpg("svg2hpgl")
                / f"{DateHandler().utc_timestamp()}_{suffix}.png"
        )
        arcade.get_image().save(fn, "PNG")
        log.info(f"saved {fn}")

    bb = c.bb()
    r = RealtimeRenderer(int(bb.w + bb.x * 2), int(bb.h + bb.y * 2), f"v3ga_{fi}")
    r.add_collection(c, 1)
    r.add_cb(arcade.key.N, next_key)
    r.add_cb(arcade.key.E, export)
    r.add_cb(arcade.key.P, save_pickle)
    r.add_cb(arcade.key.S, screenshot)
    r.add_cb(arcade.key.O, sort_all)
    r.index = 0
    RealtimeRenderer.run()


if __name__ == "__main__":
    main()
