import logging
import tkinter as tk
import pathlib
from tkinter import filedialog

from PIL import Image

from cursor.algorithm.braille import BrailleTranslator


def main():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()
    path = pathlib.Path(file_path)

    logging.info(f"Loaded {path.as_posix()}")

    loaded = Image.open(path.as_posix())
    loaded = loaded.convert('1')  # invert
    out = BrailleTranslator().to_braille(loaded, "ascii")

    out_filepath = f"{path.as_posix()}.vim"
    logging.info(f"Saved {out_filepath}")
    with open(out_filepath, "w") as out_file:
        for line in out:
            out_file.write(f"{line}\n")


if __name__ == "__main__":
    """
    This loads an image file and converts it to braille
    """
    main()
