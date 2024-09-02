import json

import numpy as np
import h5py

from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position

"""
These functions save/load path/collection data from/to H5 files
It should be faster for loading, but it's binary. Not sure if it's a good trade off
for the current files saved as json. we need a benchmark
"""


def save_collection_to_h5(collection: Collection, filename: str) -> None:
    with h5py.File(filename, "w") as f:
        # Save collection attributes
        f.attrs["name"] = collection.name
        f.attrs["timestamp"] = collection._timestamp

        # Create a group for properties
        props_group = f.create_group("properties")
        save_dict_compressed(props_group, collection.properties)

        # Create a group for paths
        paths_group = f.create_group("paths")

        # Prepare data for all paths
        all_x = []
        all_y = []
        all_timestamps = []
        path_lengths = []
        path_properties = []
        vertex_properties = []

        for path in collection.paths:
            path_lengths.append(len(path.vertices))
            x_data = [v.x for v in path.vertices]
            y_data = [v.y for v in path.vertices]
            timestamp_data = [v.timestamp for v in path.vertices]
            all_x.extend(x_data)
            all_y.extend(y_data)
            all_timestamps.extend(timestamp_data)
            path_properties.append(json.dumps(path.properties))
            vertex_properties.extend([json.dumps(v.properties) for v in path.vertices])

        # Save all path data in compressed datasets
        paths_group.create_dataset(
            "x", data=np.array(all_x), compression="gzip", compression_opts=9
        )
        paths_group.create_dataset(
            "y", data=np.array(all_y), compression="gzip", compression_opts=9
        )
        paths_group.create_dataset(
            "timestamp",
            data=np.array(all_timestamps),
            compression="gzip",
            compression_opts=9,
        )
        paths_group.create_dataset(
            "path_lengths",
            data=np.array(path_lengths),
            compression="gzip",
            compression_opts=9,
        )
        save_string_list(paths_group, "path_properties", path_properties)
        save_string_list(paths_group, "vertex_properties", vertex_properties)


def save_dict_compressed(group, dictionary):
    for key, value in dictionary.items():
        if isinstance(value, (int, float, bool, np.number)):
            group.attrs[key] = value
        elif isinstance(value, str) and len(value) < 1000:
            group.attrs[key] = value
        else:
            # For complex objects or long strings, serialize to JSON
            json_value = json.dumps(value, default=lambda o: o.__dict__)
            save_long_string(group, key, json_value)


def save_long_string(group, key, string_value):
    chunk_size = 1000000  # 1MB chunks
    num_chunks = (len(string_value) - 1) // chunk_size + 1
    chunks = [
        string_value[i * chunk_size : (i + 1) * chunk_size] for i in range(num_chunks)
    ]

    chunk_group = group.create_group(key)
    chunk_group.attrs["num_chunks"] = num_chunks
    for i, chunk in enumerate(chunks):
        chunk_group.create_dataset(
            f"chunk_{i}", data=chunk, dtype=h5py.special_dtype(vlen=str)
        )


def save_string_list(group, key, string_list):
    chunk_size = 1000  # Number of strings per chunk
    num_chunks = (len(string_list) - 1) // chunk_size + 1
    chunks = [
        string_list[i * chunk_size : (i + 1) * chunk_size] for i in range(num_chunks)
    ]

    list_group = group.create_group(key)
    list_group.attrs["num_chunks"] = num_chunks
    for i, chunk in enumerate(chunks):
        list_group.create_dataset(
            f"chunk_{i}",
            data=np.array(chunk, dtype=h5py.special_dtype(vlen=str)),
            compression="gzip",
            compression_opts=9,
        )


def load_collection_from_h5(filename: str) -> Collection:
    with h5py.File(filename, "r") as f:
        collection = Collection(name=f.attrs["name"], timestamp=f.attrs["timestamp"])

        # Load collection properties
        if "properties" in f:
            collection.properties = load_dict_compressed(f["properties"])

        # Load paths
        paths_group = f["paths"]
        x_data = paths_group["x"][()]
        y_data = paths_group["y"][()]
        timestamp_data = paths_group["timestamp"][()]
        path_lengths = paths_group["path_lengths"][()]
        path_properties = load_string_list(paths_group, "path_properties")
        vertex_properties = load_string_list(paths_group, "vertex_properties")

        vertex_index = 0
        for i, length in enumerate(path_lengths):
            path = Path()
            path.properties = json.loads(path_properties[i])

            for j in range(length):
                position = Position(
                    x_data[vertex_index],
                    y_data[vertex_index],
                    timestamp_data[vertex_index],
                )
                position.properties = json.loads(vertex_properties[vertex_index])
                path.add_position(position)
                vertex_index += 1

            collection.add(path)

    return collection


def load_dict_compressed(group):
    result = {}
    for key in group.attrs:
        result[key] = group.attrs[key]
    for key in group:
        if isinstance(group[key], h5py.Group):
            result[key] = json.loads(load_long_string(group[key]))
    return result


def load_long_string(string_group):
    num_chunks = string_group.attrs["num_chunks"]
    chunks = [string_group[f"chunk_{i}"][()] for i in range(num_chunks)]
    # Decode bytes to string if necessary
    decoded_chunks = [
        chunk.decode("utf-8") if isinstance(chunk, bytes) else chunk for chunk in chunks
    ]
    return "".join(decoded_chunks)


def load_string_list(group, key):
    list_group = group[key]
    num_chunks = list_group.attrs["num_chunks"]
    chunks = [list_group[f"chunk_{i}"][()] for i in range(num_chunks)]
    # Decode bytes to string if necessary
    decoded_chunks = [
        [item.decode("utf-8") if isinstance(item, bytes) else item for item in chunk]
        for chunk in chunks
    ]
    return [item for sublist in decoded_chunks for item in sublist]
