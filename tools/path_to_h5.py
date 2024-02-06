import h5py

from cursor.path import Path
import numpy as np

from cursor.position import Position

filename = "test_path.h5"


def save_test_file():
    """
    Main problem is saving up the properties/metadata per Path and per Position
    Maybe it's not necessary for this actually.. The recorder doesnt save this up either,
    since there are no properties at this point except from default values

    And when one needs these properties, one can just pickle the objects
    """
    path = Path.from_tuple_list([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])
    ds_dtype = [
        ("positions", float, 2),
        ("properties", "S50"),  # S50 means string apparently?
    ]

    ds_arr = np.recarray(len(path), dtype=ds_dtype)
    ds_arr["positions"] = path.as_array()
    ds_arr["properties"] = np.asarray("ok")
    # property is a value saved for each position
    with h5py.File(filename, "w") as h5f:
        dset = h5f.create_dataset("positions", data=ds_arr, maxshape=(None))


def from_array(arr: np.array) -> Path:
    return Path.from_list([Position.from_array(a[0]) for a in arr])


def load_test_file():
    f = h5py.File(filename, "r")
    dset = f["positions"]
    asarray = np.array(dset)
    for a in asarray:
        print(a)
    parsed = from_array(asarray)

    print(parsed)


if __name__ == "__main__":
    save_test_file()
    load_test_file()
