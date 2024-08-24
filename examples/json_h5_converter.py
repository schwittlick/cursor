import pathlib

from cursor.algorithm.h5 import save_collection_to_h5
from cursor.data import DataDirHandler
from cursor.load.loader import Loader
from cursor.collection import Collection

# Import the save_collection_to_h5 function we created earlier


def convert_json_to_h5(
    input_directory: str, output_file: str, limit_files: int | list[str] | None = None
):
    # Create a Loader instance
    loader = Loader(
        directory=pathlib.Path(input_directory),
        limit_files=limit_files,
        load_keys=True,  # Set to True if you want to load keyboard data as well
    )

    # Get all collections
    all_collections = loader.all_collections()

    # Combine all collections into one
    combined_collection = Collection(name="Combined Collection")
    for collection in all_collections:
        combined_collection.extend(collection)

    # Add keyboard data to the collection properties if loaded
    if loader.keys():
        combined_collection.properties["keyboard_data"] = [
            (k.key, k.timestamp, k.is_down) for k in loader.keys()
        ]

    # Save the combined collection to an HDF5 file
    save_collection_to_h5(combined_collection, output_file)

    print(f"Converted {len(all_collections)} collections to HDF5 file: {output_file}")
    print(f"Total paths: {len(combined_collection)}")
    print(f"Total keyboard events: {len(loader.keys())}")


if __name__ == "__main__":
    recs_dir = DataDirHandler().recordings()
    output_file = "1724238962.5259_belly_pain.h5"

    # Optional: limit the number of files to process
    # limit_files = 10  # Process only the first 10 files
    limit_files = ["1724238962.5259_belly_pain"]  # Process specific files

    convert_json_to_h5(recs_dir.as_posix(), output_file, limit_files=limit_files)

    # If you want to limit the files:
    # convert_json_to_h5(input_dir, output_file, limit_files=limit_files)
