import json
import random

import h5py

from cursor.collection import Collection
from cursor.path import Path
import numpy as np

from cursor.position import Position
from cursor.properties import Property
from cursor.tools.decorator_helpers import timing

filename = "test_path.h5"
filename_collection = "test_collection.h5"


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
    path.properties = {Property.COLOR: (0.1, 0.2, 0.3), Property.LASER_AMP: 3.0}
    return path


def generate_test_collection(length_collection: int, length_paths: int) -> Collection:
    return Collection.from_path_list(
        [generate_test_path(length_paths) for _ in range(length_collection)]
    )


def dataset_from_collection(collection: Collection):
    ds_arr = np.recarray(
        len(collection),
        dtype=[
            ("paths", (float, 2), len(collection[0])),
            ("timestamp", int),
            ("name", "S50"),
            ("properties", "S75"),
        ],
    )
    ds_arr["paths"] = collection.as_array()
    # ds_arr["timestamp"] = collection.timestamp()
    # ds_arr["name"] = collection.name
    # ds_arr["properties"] = json.dumps(collection.properties)
    return ds_arr


def dataset_from_path(path):
    ds_arr = np.recarray(
        len(path),
        dtype=[
            ("positions", float, 2),
            ("timestamp", int),
            ("properties", "S75"),  # S50 means string apparently?
        ],
    )

    ds_arr["positions"] = path.as_array()
    ds_arr["timestamp"] = np.asarray([p.timestamp for p in path.vertices])
    ds_arr["properties"] = np.asarray([json.dumps(p.properties) for p in path.vertices])
    return ds_arr


def path_from_dataset(dataset_positions, dataset_properties) -> Path:
    asarray = np.array(dataset_positions)
    parsed = from_array(asarray)
    parsed.properties = dict(json.loads(dataset_properties[0][0]))
    return parsed


def collection_from_dataset(dataset_positions, dataset_properties) -> Collection:
    asarray = np.array(dataset_positions)
    parsed_collection = collection_from_array(asarray)
    parsed_collection.properties = dict(json.loads(dataset_properties[0][0]))
    return parsed_collection


@timing
def save_test_file():
    """
    Main problem is saving up the properties/metadata per Path and per Position
    Maybe it's not necessary for this actually.. The recorder doesnt save this up either,
    since there are no properties at this point except from default values

    And when one needs these properties, one can just pickle the objects
    """

    path = generate_test_path(100)

    ds_arr_prop = np.recarray(1, dtype=[("properties", "S80")])
    json_string = json.dumps(path.properties)

    ds_arr_prop["properties"] = np.asarray(json_string)
    # property is a value saved for each position
    with h5py.File(filename, "w") as h5f:
        h5f.create_dataset(
            "positions", data=dataset_from_path(path)
        )  # positions & position-properties
        h5f.create_dataset("properties", data=ds_arr_prop)  # path-global properties

    return path


def from_array(arr: np.array) -> Path:
    return Path.from_list([Position(a[0][0], a[0][1], a[1], a[2]) for a in arr])


def collection_from_array(arr: np.array) -> Collection:
    # collection = Collection()
    # for a in arr:
    #    pa = Path.from_list([Position.from_array(pos_ar) for pos_ar in a[0]])
    #    collection.add(pa)
    # return collection
    return Collection.from_path_list(
        [Path.from_list([Position.from_array(pos_ar) for pos_ar in a[0]]) for a in arr]
    )


@timing
def load_test_file():
    f = h5py.File(filename, "r")
    parsed_path = path_from_dataset(f["positions"], f["properties"])
    return parsed_path


@timing
def load_test_collection_file() -> Collection:
    f = h5py.File(filename_collection, "r")
    parsed_collection = collection_from_dataset(f["positions"], f["properties"])
    return parsed_collection


@timing
def save_test_collection():
    collection = generate_test_collection(200, 300)

    ds_arr_prop = np.recarray(1, dtype=[("properties", "S80")])
    json_string = json.dumps(collection.properties)

    ds_arr_prop["properties"] = np.asarray(json_string)
    # property is a value saved for each position
    with h5py.File(filename_collection, "w") as h5f:
        h5f.create_dataset("positions", data=dataset_from_collection(collection))
        h5f.create_dataset("properties", data=ds_arr_prop)  # path-global properties

    return collection


if __name__ == "__main__":
    saved_path = save_test_file()
    loaded_path = load_test_file()
    assert saved_path == loaded_path

    saved_collection = save_test_collection()
    loaded_collection = load_test_collection_file()

    # print(saved_collection)
    # print(loaded_collection)

    assert saved_collection == loaded_collection
