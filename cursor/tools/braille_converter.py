import logging
import sys
import tkinter as tk
import pathlib
from tkinter import filedialog

from PIL import Image, ImageOps
from PIL.Image import Transpose

from cursor.algorithm.braille import BrailleTranslator


def save(data: list[str], filename: str) -> None:
    with open(filename, "w") as out_file:
        for line in data:
            out_file.write(f"{line}\n")

    logging.info(f"Saved {filename}")


def convert(file_path: str):
    path = pathlib.Path(file_path)

    logging.info(f"Loaded {path.as_posix()}")

    loaded = Image.open(path.as_posix())

    # rotating to support landscape images to be accepted
    if loaded.width != 126:
        loaded = loaded.transpose(Transpose.ROTATE_90)

    # for 297x500mm paper, this is the resolution
    assert loaded.width == 126
    assert loaded.height == 225

    # print it upside-down. like that it's possible to align embossed
    # blocks of e.g. emojis, to be aligned at the bottom
    loaded = loaded.transpose(Transpose.ROTATE_180)

    image = loaded.convert('1')  # binary
    inverted_image = ImageOps.invert(image)

    braille_image = BrailleTranslator().to_braille(image, "ascii")
    braille_inverted = BrailleTranslator().to_braille(inverted_image, "ascii")
    # 👀︎👁︎👀︎👁︎
    save(braille_image, f"{path.as_posix()}.vim")
    save(braille_inverted, f"{path.as_posix()}_inverted.vim")
    # ︎🐞︎🐟︎ ︎❤


def main():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(initialdir='/home/marcel/braille/')

    if not file_path:
        logging.warning("Not selected any file. Aborting")
        sys.exit(0)

    convert(file_path)


if __name__ == "__main__":
    """
    This loads an image file and converts it to braille
    """
    main()
