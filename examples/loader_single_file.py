from cursor.bb import BoundingBox
from cursor.data import DataDirHandler
from cursor.load.loader import Loader
from renderer.realtime import RealtimeRenderer

if __name__ == "__main__":
    ll = Loader()
    ll.load_file(DataDirHandler().recordings() / "1664174605.599717_colors.json")
    c = ll.all_paths()

    res = BoundingBox(0, 0, 1920, 1080)

    c.fit(res)

    rr = RealtimeRenderer(res.w, res.h, "single recording example")
    rr.add_collection(c, 2, (255, 255, 255))

    rr.run()
