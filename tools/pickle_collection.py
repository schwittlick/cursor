from cursor.filter import SortParameter, Sorter
from cursor.loader import Loader
from cursor.data import DataDirHandler

from cursor.bb import BoundingBox
from cursor.collection import Collection

from cursor.misc import Timer


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
    timer = Timer()
    c.simplify(0.1)
    timer.print_elapsed("simplifying took")
    c.save_pickle("frechet_all_simplified.pickle")


def save_entropy_crossed() -> None:
    dir = DataDirHandler().recordings()
    ll = Loader(directory=dir, limit_files=None)

    keep_aspect_ratio = False
    c = ll.all_paths()
    bb = BoundingBox(0, 0, 1, 1)

    for p in c:
        p.fit(bb, 1.0, keep_aspect_ratio)

    c.simplify(0.01)

    sorter = Sorter(param=SortParameter.ENTROPY_X, reverse=True)
    paths_sorted = c.sorted(sorter)

    sorter = Sorter(param=SortParameter.FRECHET_DISTANCE, reverse=False)
    paths_sorted = c.sorted(sorter, paths_sorted[6])

    c = Collection()
    c.add(paths_sorted)
    name = "frechet_squiggle_all_norm_simplified_0.01.pickle"
    c.save_pickle(name)

    sorter = Sorter(param=SortParameter.FRECHET_DISTANCE, reverse=False)
    paths_sorted = c.sorted(sorter, c.random())

    c = Collection()
    c.add(paths_sorted)
    name = "frechet1_all_norm_simplified_0.01.pickle"
    c.save_pickle(name)

    sorter = Sorter(param=SortParameter.FRECHET_DISTANCE, reverse=False)
    paths_sorted = c.sorted(sorter, c.random())

    c = Collection()
    c.add(paths_sorted)
    name = "frechet2_all_norm_simplified_0.01.pickle"
    c.save_pickle(name)

    sorter = Sorter(param=SortParameter.FRECHET_DISTANCE, reverse=False)
    paths_sorted = c.sorted(sorter, c.random())

    c = Collection()
    c.add(paths_sorted)
    name = "frechet3_all_norm_simplified_0.01.pickle"
    c.save_pickle(name)

    sorter = Sorter(param=SortParameter.VARIATION_X, reverse=True)
    paths_sorted = c.sorted(sorter)

    c = Collection()
    c.add(paths_sorted)
    name = "variation_x_all_norm_simplified_0.01.pickle"
    c.save_pickle(name)

    sorter = Sorter(param=SortParameter.VARIATION_Y, reverse=True)
    paths_sorted = c.sorted(sorter)

    c = Collection()
    c.add(paths_sorted)
    name = "variation_y_all_norm_simplified_0.01.pickle"
    c.save_pickle(name)

    sorter = Sorter(param=SortParameter.ENTROPY_Y, reverse=True)
    paths_sorted = c.sorted(sorter)

    c = Collection()
    c.add(paths_sorted)
    name = "entropy_y_all_norm_simplified_0.01.pickle"
    c.save_pickle(name)

    sorter = Sorter(param=SortParameter.ENTROPY_CROSS, reverse=True)
    paths_sorted = c.sorted(sorter)

    c = Collection()
    c.add(paths_sorted)
    name = "entropy_cross_all_norm_presimplified_0.01.pickle"
    c.save_pickle(name)

    sorter = Sorter(param=SortParameter.ENTROPY_Y, reverse=True)
    paths_sorted = c.sorted(sorter)

    c = Collection()
    c.add(paths_sorted)
    name = "entropy_y_all_norm_presimplified_0.01.pickle"
    c.save_pickle(name)

    sorter = Sorter(param=SortParameter.ENTROPY_X, reverse=True)
    paths_sorted = c.sorted(sorter)

    c = Collection()
    c.add(paths_sorted)
    name = "entropy_x_all_norm_presimplified_0.01.pickle"
    c.save_pickle(name)

    sorter = Sorter(param=SortParameter.DISTANCE, reverse=True)
    paths_sorted = c.sorted(sorter)

    c = Collection()
    c.add(paths_sorted)
    name = "distance_all_norm_presimplified_0.01.pickle"
    c.save_pickle(name)

    sorter = Sorter(param=SortParameter.POINT_COUNT, reverse=True)
    paths_sorted = c.sorted(sorter)

    c = Collection()
    c.add(paths_sorted)
    name = "pointcount_all_norm_presimplified_0.01.pickle"
    c.save_pickle(name)


if __name__ == "__main__":
    # save_frechet()
    save_entropy_crossed()
