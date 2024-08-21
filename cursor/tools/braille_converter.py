import logging
import sys
import tkinter as tk
import pathlib
from enum import Enum
from tkinter import filedialog

from PIL import Image, ImageOps
from PIL.Image import Transpose

from cursor.algorithm.braille import BrailleTranslator


class BrailleFormats(Enum):
    _30_50 = 126, 255  # 297x500mm (this is the max)
    _30_30 = 126, 126  # 297x297
    # a4 missing something like 126, 88?


def save(data: list[str], filename: str) -> None:
    with open(filename, "w") as out_file:
        for line in data:
            out_file.write(f"{line}\n")

    logging.info(f"Saved {filename}")


def detect_paper_size(image_width: int, image_height: int) -> BrailleFormats | bool:
    """
    we want only a few formats of images be allowed
    this code here makes sure the exported .vim text file will fit
    the paper in the braille printer.
    """
    for frmt in BrailleFormats:
        if image_width == frmt.value[0] and image_height == frmt.value[1]:
            return frmt
        elif image_width == frmt.value[1] and image_height == frmt.value[0]:
            return frmt

    return False


def convert(file_path: pathlib.Path) -> list[str]:
    im = Image.open(file_path.as_posix())

    fmt = detect_paper_size(im.width, im.height)
    if not fmt:
        logging.error(f"w:{im.width} h:{im.height}")
        logging.error("Input image has unknown size")
        return []

    # rotating to support landscape images to be accepted
    if im.width != 126:
        im = im.transpose(Transpose.ROTATE_90)

    # print it upside-down. like that it's possible to align embossed
    # blocks of e.g. emojis, to be aligned at the bottom
    im = im.transpose(Transpose.ROTATE_180)

    im = im.convert('1')  # binary
    inverted_im = ImageOps.invert(im)

    # braille_image = BrailleTranslator().to_braille(im, "ascii")
    braille_inverted = BrailleTranslator().to_braille(inverted_im, "ascii")

    # save(braille_image, f"{path.as_posix()}.vim")

    return braille_inverted


def main():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(initialdir='/home/marcel/braille/')

    if not file_path:
        logging.warning("Not selected any file. Aborting")
        sys.exit(0)

    path = pathlib.Path(file_path)

    vim_data = convert(path)
    save(vim_data, f"{path.as_posix()}_inverted.vim")


if __name__ == "__main__":
    """
    This loads an image file and converts it to braille
    """
    main()
