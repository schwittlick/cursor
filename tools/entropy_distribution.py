import logging

import numpy as np
import matplotlib.pyplot as plt

from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.loader import Loader
from cursor.timer import Timer


def load_all():
    timer = Timer()
    c = Collection.from_pickle("2023.pckl")
    timer.print_elapsed("Loading 2023.pckl took ")
    logging.info(len(c))


def save(c, fn):
    save_dir = DataDirHandler().pickles() / f"{fn}.pckl"
    c.save_pickle(save_dir)


if __name__ == "__main__":
    # load_all()

    recordings = DataDirHandler().recordings()
    loader = Loader(directory=recordings, limit_files=None)
    paths = loader.all_paths()

    # save_dir = DataDirHandler().pickles() / "2023.pckl"
    # paths.save_pickle(save_dir)

    cleaned_paths = Collection()

    logging.info(f"Len before: {len(paths)}")
    for path in paths.paths:
        if len(path) < 3:  # <= 600:
            continue
        if path.is_1_dimensional():
            continue
        cleaned_paths.add(path)
    logging.info(f"Len after: {len(cleaned_paths)}")

    variation_x = Collection()
    not_welcome_data = Collection()

    for path in cleaned_paths:
        # if math.isclose(path.differential_entropy_x, -math.inf):
        # if len(path) > 600:
        # if path.variation_y > -1 and not math.isclose(path.variation_y, math.inf) and path.variation_y < 3:
        if path.duration < 30:
            variation_x.add(path)
            # logging.info(f"{path.differential_entropy_y}")
            # logging.info(f"{path}")
            # logging.info(f"{path.is_1_dimensional()}")
        else:
            not_welcome_data.add(path)

    # s = Sorter(param=SortParameter.POINT_COUNT, reverse=True)
    # cleaned_paths.sort(s)

    logging.info(f"Not welcome: {len(not_welcome_data)}")

    save(not_welcome_data, "duration_more_than_30s")

    entropies_differential = np.array([path.duration for path in variation_x])

    logging.info(f"Total {len(entropies_differential)} paths")

    plt.hist(entropies_differential, bins=100)
    plt.gca().xaxis.set_major_locator(plt.MultipleLocator(1))
    plt.show()
