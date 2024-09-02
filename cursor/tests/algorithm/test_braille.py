import numpy as np
import pathlib
from PIL import Image

from cursor.algorithm.braille import BrailleTranslator


def test_from_image():
    bt = BrailleTranslator()

    test_images_path = pathlib.Path(__file__).resolve().parent.parent / "data" / "jpg"
    im = test_images_path / "smiley.png"
    loaded = Image.open(im)
    loaded = loaded.resize((50, 60))
    loaded = loaded.convert('1')
    out = bt.to_braille(loaded, "ascii")[1:]

    img = bt.from_braille(out)

    in_array = np.asarray(loaded)
    out_array = np.asarray(img)

    assert (in_array == out_array).all()


def test_braille():
    bt = BrailleTranslator()

    i1 = bt.matrix_to_binary([[1, 0, 1], [0, 1, 0]])
    assert i1 == bt.get_index('O')

    i2 = bt.matrix_to_binary([[1, 1, 1], [1, 1, 1]])
    assert i2 == bt.get_index('=')


def test_split_into_bits():
    bt = BrailleTranslator()

    bits = bt.split_into_bits(bt.get_index('O'))
    assert bits == [[1, 0, 1], [0, 1, 0]]

    bits = bt.split_into_bits(bt.get_index('='))
    assert bits == [[1, 1, 1], [1, 1, 1]]


def test_from_braille():
    bt = BrailleTranslator()

    img = bt.from_braille(["0=1", "ABC", "D(F"])
    data = np.asarray(img)
    data_to_compare = np.array(
        [[False, False, True, True, False, False],
         [False, True, True, True, True, False],
         [True, True, True, True, False, False],
         [True, False, True, False, True, True],
         [False, False, True, False, False, False],
         [False, False, False, False, False, False],
         [True, True, True, False, True, True],
         [False, True, True, True, True, False],
         [False, False, True, True, False, False]])
    assert (data_to_compare == data).all()
