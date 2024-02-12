import json
import pathlib
import numpy as np
import h5py

from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position
from cursor.timer import timing

"""
These functions save/load path/collection data from/to H5 files
It should be faster for loading, but it's binary. Not sure if it's a good trade off
for the current files saved as json. we need a benchmark
"""


def dataset_from_collection(collection: Collection):
    ds_arr = np.recarray(
        len(collection),
        dtype=[
            ("paths", (float, 3), len(collection[0])),
            ("timestamp", int),
            ("name", "S50"),
            ("properties", "S75"),
        ],
    )
    all_collection_data = np.array(
        [
            np.array([np.array([p2.x, p2.y, p2.timestamp]) for p2 in p.vertices])
            for p in collection.paths
        ],
        dtype=object,
    )
    ds_arr["paths"] = all_collection_data
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
def save_test_file(file: pathlib.Path, path: Path):
    """
    Main problem is saving up the properties/metadata per Path and per Position
    Maybe it's not necessary for this actually.. The recorder doesnt save this up either,
    since there are no properties at this point except from default values

    And when one needs these properties, one can just pickle the objects
    """

    ds_arr_prop = np.recarray(1, dtype=[("properties", "S80")])
    json_string = json.dumps(path.properties)

    ds_arr_prop["properties"] = np.asarray(json_string)
    # property is a value saved for each position
    with h5py.File(file.as_posix(), "w") as h5f:
        h5f.create_dataset(
            "positions", data=dataset_from_path(path)
        )  # positions & position-properties
        h5f.create_dataset("properties", data=ds_arr_prop)  # path-global properties

    return path


def from_array(arr: np.array) -> Path:
    return Path.from_list([Position(a[0][0], a[0][1], a[1], a[2]) for a in arr])


def collection_from_array(arr: np.array) -> Collection:
    return Collection.from_path_list(
        [
            Path.from_list(
                [Position(pos_ar[0], pos_ar[1], pos_ar[2]) for pos_ar in a[0]]
            )
            for a in arr
        ]
    )


@timing
def load_test_file(file: pathlib.Path):
    f = h5py.File(file.as_posix(), "r")
    parsed_path = path_from_dataset(f["positions"], f["properties"])
    return parsed_path


@timing
def load_test_collection_file(file: pathlib.Path) -> Collection:
    f = h5py.File(file.as_posix(), "r")
    parsed_collection = collection_from_dataset(f["positions"], f["properties"])
    return parsed_collection


@timing
def save_test_collection(file: pathlib.Path, collection: Collection):
    ds_arr_prop = np.recarray(1, dtype=[("properties", "S80")])
    json_string = json.dumps(collection.properties)

    ds_arr_prop["properties"] = np.asarray(json_string)
    # property is a value saved for each position
    with h5py.File(file.as_posix(), "w") as h5f:
        h5f.create_dataset("positions", data=dataset_from_collection(collection))
        h5f.create_dataset("properties", data=ds_arr_prop)  # path-global properties

    return collection
