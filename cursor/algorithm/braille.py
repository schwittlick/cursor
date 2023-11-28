import numpy as np
from PIL import Image
import numpy


class BrailleTranslator:
    def __init__(self):
        self.ascii_mapping = " A1B'K2L@CIF/MSP\"E3H9O6R^DJG>NTQ,*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)="
        self.unicode_mapping = "⠀⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫⠬⠭⠮⠯⠰⠱⠲⠳⠴⠵⠶⠷⠸⠹⠺⠻⠼⠽⠾⠿"

        self.extend_page = "DPL500;"

    def get_index(self, char: str) -> int:
        assert char.upper() in self.ascii_mapping
        return self.ascii_mapping.find(char.upper())

    def matrix_to_binary(self, matrix: list[list[int]]):
        assert len(matrix) == 2
        assert len(matrix[0]) == 3
        #  _______
        # | 1 | 4 |
        # |---|---|
        # | 2 | 5 |
        # |---|---|
        # | 3 | 6 |
        #  _______
        #
        # [[1, 2, 3], [4, 5, 6]]

        # incoming matrix needs to be 2x3 e.g. [[1, 0, 1], [0, 1, 0]]
        # concatenates the incoming matrix and reverses it
        # like that we end up with an index in the mapping string
        return int(''.join([str(int(j)) for i in matrix for j in i])[::-1], 2)

    def toBraille(self, image: Image, mode="ascii") -> list[str]:
        assert image.width % 2 == 0
        assert image.height % 3 == 0
        out = ["1"]

        data = numpy.asarray(image)

        for y in range(0, data.shape[0], 3):
            line = ""
            for x in range(0, data.shape[1], 2):
                _0 = data[y][x]
                _1 = data[y + 1][x]
                _2 = data[y + 2][x]
                _3 = data[y][x + 1]
                _4 = data[y + 1][x + 1]
                _5 = data[y + 2][x + 1]
                ll = [[_0, _1, _2], [_3, _4, _5]]
                idx = self.matrix_to_binary(ll)
                if mode == "ascii":
                    char = self.ascii_mapping[idx]
                else:  # unicode
                    char = self.unicode_mapping[idx]
                line = f"{line}{char}"
            out.append(line)
        return out

    @staticmethod
    def split_into_bits(number) -> list[list[int]]:
        # Using bit manipulation to extract each bit from the integer
        # Only using 6 bits, we dont need more. Also reverted
        bits = [(number >> i) & 1 for i in range(5, -1, -1)][::-1]
        return [bits[:3], bits[3:]]

    def fromBraille(self, data: list[str]) -> Image:
        w = len(data[0]) * 2
        h = len(data) * 3

        pixels = np.zeros(shape=(h, w), dtype=bool)

        y = 0
        for line in data:
            x = 0
            for char in line:
                braille_index = self.get_index(char)
                bits = self.split_into_bits(braille_index)
                pixels[y][x] = bits[0][0]
                pixels[y + 1][x] = bits[0][1]
                pixels[y + 2][x] = bits[0][2]
                pixels[y][x + 1] = bits[1][0]
                pixels[y + 1][x + 1] = bits[1][1]
                pixels[y + 2][x + 1] = bits[1][2]

                x += 2
            y += 3

        return Image.fromarray(pixels)
