from cursor.bb import BoundingBox
from cursor.data import DataDirHandler
from cursor.loader import JsonCompressor, Loader


def save(m):
    save_path = DataDirHandler().recordings_legacy_simplified()
    save_path.mkdir(parents=True, exist_ok=True)

    recs = {"mouse": m, "keys": []}

    fname_compressed = save_path / "0legacy_simplified_0.001.json"

    with open(fname_compressed.as_posix(), "w") as fp:
        dump = JsonCompressor().json_zip(recs)
        fp.write(str(dump))


if __name__ == "__main__":
    dir = DataDirHandler().recordings_legacy()
    ll = Loader(directory=dir, limit_files=None)

    keep_aspect_ratio = False
    c = ll.all_paths()
    bb = BoundingBox(0, 0, 1, 1)

    for p in c:
        p.fit(bb, 1.0, keep_aspect_ratio)

    c.simplify(0.001)
    save(c)
