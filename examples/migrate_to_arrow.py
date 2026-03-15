"""Migrate compressed JSON recording files to Arrow/Feather format.

Usage:
    python examples/migrate_to_arrow.py [--output-dir OUTPUT_DIR]

By default, feather files are written next to the source JSON files
in the same directory. Pass --output-dir to write them elsewhere.
"""

from __future__ import annotations

import argparse
import logging
import pathlib
import sys
import time

from tqdm import tqdm

from cursor.data import DataDirHandler
from cursor.load.arrow_loader import write_recording
from cursor.load.loader import _load_file_worker

logging.basicConfig(level=logging.WARNING, format="%(message)s")


def migrate(source_dir: pathlib.Path, output_dir: pathlib.Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_files = sorted(f for f in source_dir.glob("*.json") if f.is_file())
    if not json_files:
        print(f"No .json files found in {source_dir}")
        return

    already_done = {f.stem for f in output_dir.glob("*.feather") if f.is_file()}
    pending = [f for f in json_files if f.stem not in already_done]

    print(f"Found {len(json_files)} recording(s). {len(already_done)} already converted, {len(pending)} remaining.")

    if not pending:
        print("Nothing to do.")
        return

    errors: list[tuple[pathlib.Path, Exception]] = []
    t_total = time.perf_counter()

    with tqdm(total=len(pending), unit="file") as pbar:
        for json_path in pending:
            pbar.set_description(json_path.stem[:30])
            try:
                collection, keys = _load_file_worker(json_path, load_keys=True, verbose=False)
                collection.clean()
                out_path = output_dir / (json_path.stem + ".feather")
                write_recording(collection, keys, out_path)
            except Exception as exc:
                errors.append((json_path, exc))
                tqdm.write(f"  ERROR {json_path.name}: {exc}")
            finally:
                pbar.update(1)

    elapsed = time.perf_counter() - t_total
    converted = len(pending) - len(errors)
    print(f"\nConverted {converted}/{len(pending)} files in {elapsed:.1f}s.")
    if errors:
        print(f"{len(errors)} file(s) failed:")
        for path, exc in errors:
            print(f"  {path.name}: {exc}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        default=None,
        help="Directory to write .feather files (default: same as source)",
    )
    args = parser.parse_args()

    source_dir = DataDirHandler().recordings()
    output_dir = args.output_dir if args.output_dir else source_dir

    print(f"Source : {source_dir}")
    print(f"Output : {output_dir}")
    migrate(source_dir, output_dir)


if __name__ == "__main__":
    main()
