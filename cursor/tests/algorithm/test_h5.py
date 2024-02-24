import random

from cursor.algorithm.h5 import (
    save_test_file,
    load_test_file,
    save_test_collection,
    load_test_collection_file,
)
from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.loader import Loader
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property


def generate_test_path(length: int) -> Path:
    path = Path.from_list(
        [
            Position(
                random.uniform(-10, 10),
                random.uniform(-10, 10),
                random.randint(0, 10),
                {
                    Property.COLOR: (
                        random.uniform(0, 255),
                        random.uniform(0, 255),
                        random.uniform(0, 255),
                    )
                },
            )
            for _ in range(length)
        ]
    )
    path.color = (0.1, 0.2, 0.3)
    path.laser_amp = 3.0
    return path


def generate_test_collection(length_collection: int, length_paths: int) -> Collection:
    return Collection.from_path_list(
        [generate_test_path(length_paths) for _ in range(length_collection)]
    )


def DISABLED_test_saved_loaded_path():
    path = generate_test_path(100)
    temp_file = DataDirHandler().test_data_file("test_path.h5")
    saved_path = save_test_file(temp_file, path)
    loaded_path = load_test_file(temp_file)
    assert saved_path == loaded_path


def DISABLED_test_saved_loaded_collection():
    collection = generate_test_collection(200, 300)
    temp_file = DataDirHandler().test_data_file("test_collection.h5")
    saved_collection = save_test_collection(temp_file, collection)
    loaded_collection = load_test_collection_file(temp_file)
    assert saved_collection == loaded_collection


def DISABLED_test_save_load_collection_benchmark():
    """
    my h5 code can't handle collections of paths with varying lengths yet, it seems.

    """
    recordings = DataDirHandler().recordings()
    _loader = Loader(
        directory=recordings,
        limit_files=["1700043253.391094_just_another_day"],
    )
    collection = _loader.all_paths()
    temp_file = DataDirHandler().test_data_file("test_collection.h5")
    saved_collection = save_test_collection(temp_file, collection)
    loaded_collection = load_test_collection_file(temp_file)
    assert saved_collection == loaded_collection
