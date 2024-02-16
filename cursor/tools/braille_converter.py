import logging
import sys
import tkinter as tk
import pathlib
from tkinter import filedialog

from PIL import Image, ImageOps

from cursor.algorithm.braille import BrailleTranslator


def save(data: list[str], filename: str) -> None:
    with open(filename, "w") as out_file:
        for line in data:
            out_file.write(f"{line}\n")

    logging.info(f"Saved {filename}")


def main():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()

    if not file_path:
        logging.warning("Not selected any file. Aborting")
        sys.exit(0)

    path = pathlib.Path(file_path)

    logging.info(f"Loaded {path.as_posix()}")

    loaded = Image.open(path.as_posix())
    image = loaded.convert('1')  # binary
    inverted_image = ImageOps.invert(loaded).convert('1')

    braille_image = BrailleTranslator().to_braille(image, "ascii")
    braille_inverted = BrailleTranslator().to_braille(inverted_image, "ascii")

    save(braille_image, f"{path.as_posix()}.vim")
    save(braille_inverted, f"{path.as_posix()}_inverted.vim")


if __name__ == "__main__":
    """
    This loads an image file and converts it to braille
    """
    main()
