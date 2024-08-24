import random

from cursor.algorithm.h5 import (
    save_collection_to_h5,
    load_collection_from_h5,
)
from cursor.collection import Collection
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


def test_collection_save_load():
    collection = generate_test_collection(20, 20)

    # Save the collection to an HDF5 file
    save_collection_to_h5(collection, "test_collection.h5")

    # Load the collection from the HDF5 file
    loaded_collection = load_collection_from_h5("test_collection.h5")

    # Verify the loaded collection
    assert loaded_collection.name == collection.name
    assert len(loaded_collection.paths) == len(collection.paths)
    assert loaded_collection.properties == collection.properties

    print("Collection successfully saved and loaded!")
