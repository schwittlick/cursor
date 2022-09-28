import csv
import pathlib

import cursor.position
from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.loader import JsonCompressor
from cursor.path import Path


def get_res(path):
    with open(path, "r") as file:
        lines = []
        for line in file.readlines():
            lines.append(line)

        w = lines[1][(len(lines[1]) - 5) :]
        h = lines[2][(len(lines[2]) - 4) :]

        return int(w), int(h)


def save(m, name):
    save_path = DataDirHandler().recordings_legacy()
    save_path.mkdir(parents=True, exist_ok=True)

    recs = {"mouse": m, "keys": []}

    fname_compressed = save_path / f"{name}.json"

    with open(fname_compressed.as_posix(), "w") as fp:
        dump = JsonCompressor().json_zip(recs)
        fp.write(str(dump))


def parse_and_save_v1():
    base_folder = "Z:\\Dropbox\\CODE\\intellij_workspace\\MouseStudio\\data\\v1\\"
    base = pathlib.Path(base_folder)
    for folder in base.iterdir():
        if folder.is_dir():
            c = Collection()

            fn_only = folder.stem
            print(fn_only)

            pa = pathlib.Path(folder)
            res = 1920, 1080

            for fn in pa.iterdir():
                newpath = Path()
                with open(fn.as_posix(), "r") as file:
                    reader = csv.reader(file)
                    rows = []
                    for row in reader:
                        rows.append(row)

                    for row in rows[1:]:
                        pos = cursor.position.Position(
                            int(row[2]) / res[0], int(row[3]) / res[1], int(row[1])
                        )
                        newpath.add_position(pos)

                c.add(newpath)
                # print(f"added {newpath}")

            save(c, f"v1_{fn_only}")


def parse_and_save_v2():
    base_folder = "Z:\\Dropbox\\CODE\\intellij_workspace\\MouseStudio\\data\\v2\\"
    base = pathlib.Path(base_folder)

    for folder in base.iterdir():
        if folder.is_dir():
            c = Collection()

            fn_only = folder.stem
            print(fn_only)

            path = folder / "mouse"
            nfo = folder / "meta.nfo"
            pa = pathlib.Path(path)
            res = get_res(nfo)

            for fn in pa.iterdir():
                newpath = Path()
                with open(fn.as_posix(), "r") as file:
                    reader = csv.reader(file)
                    rows = []
                    for row in reader:
                        rows.append(row)

                    for row in rows[1:]:
                        pos = cursor.position.Position(
                            int(row[2]) / res[0], int(row[3]) / res[1], int(row[1])
                        )
                        newpath.add_position(pos)

                c.add(newpath)

            save(c, f"v2_{fn_only}")


if __name__ == "__main__":

    parse_and_save_v1()
    parse_and_save_v2()
