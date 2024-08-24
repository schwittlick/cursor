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


@timing
def save_collection_to_h5(collection: Collection, filename: str) -> None:
    with h5py.File(filename, "w") as f:
        # Save collection attributes
        f.attrs["name"] = collection.name
        f.attrs["timestamp"] = collection._timestamp

        # Create a group for properties
        props_group = f.create_group("properties")
        for key, value in collection.properties.items():
            props_group.attrs[key] = value

        # Create a group for paths
        paths_group = f.create_group("paths")

        for i, path in enumerate(collection.paths):
            path_group = paths_group.create_group(f"path_{i}")

            # Save path properties
            path_props = path_group.create_group("properties")
            for key, value in path.properties.items():
                if isinstance(value, (list, tuple)):
                    path_props.create_dataset(key, data=np.array(value))
                else:
                    path_props.attrs[key] = value

            # Save vertices
            vertices = path_group.create_group("vertices")
            x_data = [v.x for v in path.vertices]
            y_data = [v.y for v in path.vertices]
            timestamp_data = [v.timestamp for v in path.vertices]

            vertices.create_dataset("x", data=np.array(x_data))
            vertices.create_dataset("y", data=np.array(y_data))
            vertices.create_dataset("timestamp", data=np.array(timestamp_data))

            # Save vertex properties
            vertex_props = vertices.create_group("properties")
            for j, vertex in enumerate(path.vertices):
                if vertex.properties:
                    v_prop = vertex_props.create_group(f"vertex_{j}")
                    for key, value in vertex.properties.items():
                        if isinstance(value, (list, tuple)):
                            v_prop.create_dataset(key, data=np.array(value))
                        else:
                            v_prop.attrs[key] = value


@timing
def load_collection_from_h5(filename: str) -> Collection:
    with h5py.File(filename, "r") as f:
        collection = Collection(name=f.attrs["name"], timestamp=f.attrs["timestamp"])

        # Load collection properties
        if "properties" in f:
            for key, value in f["properties"].attrs.items():
                collection.properties[key] = value

        # Load paths
        paths_group = f["paths"]
        for path_name in paths_group:
            path_group = paths_group[path_name]
            path = Path()

            # Load path properties
            if "properties" in path_group:
                for key, value in path_group["properties"].attrs.items():
                    path.properties[key] = value
                for key in path_group["properties"]:
                    if isinstance(path_group["properties"][key], h5py.Dataset):
                        path.properties[key] = path_group["properties"][key][()]

            # Load vertices
            vertices = path_group["vertices"]
            x_data = vertices["x"][()]
            y_data = vertices["y"][()]
            timestamp_data = vertices["timestamp"][()]

            for x, y, ts in zip(x_data, y_data, timestamp_data):
                position = Position(x, y, ts)
                path.add_position(position)

            # Load vertex properties
            if "properties" in vertices:
                vertex_props = vertices["properties"]
                for i, vertex in enumerate(path.vertices):
                    v_prop_name = f"vertex_{i}"
                    if v_prop_name in vertex_props:
                        v_prop = vertex_props[v_prop_name]
                        for key, value in v_prop.attrs.items():
                            vertex.properties[key] = value
                        for key in v_prop:
                            if isinstance(v_prop[key], h5py.Dataset):
                                vertex.properties[key] = v_prop[key][()]

            collection.add(path)

    return collection
