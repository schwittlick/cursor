from cursor.filter import SortParameter, Sorter
from cursor.loader import Loader
from cursor.data import DataDirHandler

from cursor.bb import BoundingBox
from cursor.collection import Collection


def save_frechet():
    dir = DataDirHandler().recordings()
    ll = Loader(directory=dir, limit_files=None)

    keep_aspect_ratio = False
    c = ll.all_paths()
    bb = BoundingBox(0, 0, 1, 1)

    p1 = c.random()

    for p in c:
        p.fit(bb, 0.8, keep_aspect_ratio)

    sorter = Sorter(param=SortParameter.FRECHET_DISTANCE, reverse=False)

    paths_sorted = c.sorted(sorter, p1.copy())

    c = Collection()
    c.add(paths_sorted)
    c.to_pickle("frechet_all.pickle")


def save_entropy_crossed() -> None:
    name = "entropy_direction_changes_40_norm.pickle"
    dir = DataDirHandler().recordings()
    ll = Loader(directory=dir, limit_files=40)

    keep_aspect_ratio = False
    c = ll.all_paths()
    bb = BoundingBox(0, 0, 1, 1)

    for p in c:
        p.fit(bb, 1.0, keep_aspect_ratio)

    sorter = Sorter(param=SortParameter.ENTROPY_DIRECTION_CHANGES, reverse=True)

    paths_sorted = c.sorted(sorter)

    c = Collection()
    c.add(paths_sorted)
    c.to_pickle(name)


if __name__ == "__main__":
    # save_frechet()
    save_entropy_crossed()
