import time
import pathlib
from cursor.load.loader import Loader
from cursor.algorithm.h5 import load_collection_from_h5
from cursor.data import DataDirHandler


def load_json(json_path):
    loader = Loader(
        directory=pathlib.Path(json_path).parent,
        limit_files=[pathlib.Path(json_path).stem],
    )
    return loader.all_collections()[0]


def load_h5(h5_path):
    return load_collection_from_h5(h5_path)


def compare_load_times(json_path, h5_path, num_runs=5):
    json_times = []
    h5_times = []

    print(f"Comparing load times (average of {num_runs} runs):")

    for _ in range(num_runs):
        # Time JSON loading
        start_time = time.time()
        json_collection = load_json(json_path)
        json_time = time.time() - start_time
        json_times.append(json_time)

        # Time HDF5 loading
        start_time = time.time()
        h5_collection = load_h5(h5_path)
        h5_time = time.time() - start_time
        h5_times.append(h5_time)

    avg_json_time = sum(json_times) / num_runs
    avg_h5_time = sum(h5_times) / num_runs

    print(f"Average JSON load time: {avg_json_time:.4f} seconds")
    print(f"Average HDF5 load time: {avg_h5_time:.4f} seconds")

    speedup = avg_json_time / avg_h5_time if avg_h5_time > 0 else float("inf")
    print(f"HDF5 is {speedup:.2f}x faster than JSON")

    # Compare contents
    print("\nComparing contents:")
    print(f"JSON collection path count: {len(json_collection)}")
    print(f"HDF5 collection path count: {len(h5_collection)}")

    if len(json_collection) == len(h5_collection):
        print("Path counts match.")

        # Compare a few paths
        for i in range(min(3, len(json_collection))):
            json_path = json_collection[i]
            h5_path = h5_collection[i]
            if len(json_path) == len(h5_path):
                print(f"Path {i} lengths match: {len(json_path)} vertices")
            else:
                print(
                    f"Path {i} lengths do not match: JSON: {len(json_path)}, HDF5: {len(h5_path)}"
                )
    else:
        print("Warning: Path counts do not match!")

    # Compare properties
    if json_collection.properties == h5_collection.properties:
        print("Collection properties match.")
    else:
        print("Warning: Collection properties do not match!")


if __name__ == "__main__":
    json_path = DataDirHandler().recordings() / "1724238962.5259_belly_pain.json"
    h5_path = "1724238962.5259_belly_pain.h5"

    compare_load_times(json_path, h5_path)
