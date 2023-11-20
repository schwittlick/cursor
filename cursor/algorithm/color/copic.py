import random

import colour
import numpy as np

from cursor.algorithm.color.color_enums import ColorCode


class Color:
    @staticmethod
    def linear_srgb_to_oklab(
            c: tuple[float, float, float]
    ) -> tuple[float, float, float]:
        l = 0.4122214708 * c[0] + 0.5363325363 * c[1] + 0.0514459929 * c[2]
        m = 0.2119034982 * c[0] + 0.6806995451 * c[1] + 0.1073969566 * c[2]
        s = 0.0883024619 * c[0] + 0.2817188376 * c[1] + 0.6299787005 * c[2]

        l_ = np.cbrt(l)
        m_ = np.cbrt(m)
        s_ = np.cbrt(s)

        return (
            0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
        )

    @staticmethod
    def oklab_to_linear_srgb(
            c: tuple[float, float, float]
    ) -> tuple[float, float, float]:
        l_ = c[0] + 0.3963377774 * c[1] + 0.2158037573 * c[2]
        m_ = c[0] - 0.1055613458 * c[1] - 0.0638541728 * c[2]
        s_ = c[0] - 0.0894841775 * c[1] - 1.2914855480 * c[2]

        l = l_ * l_ * l_
        m = m_ * m_ * m_
        s = s_ * s_ * s_

        return (
            +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
        )

    @staticmethod
    def lerp(
            v0: tuple[float, float, float],
            v1: tuple[float, float, float],
            percentage: float,
    ):
        x = (1 - percentage) * v0[0] + percentage * v1[0]
        y = (1 - percentage) * v0[1] + percentage * v1[1]
        z = (1 - percentage) * v0[2] + percentage * v1[2]
        return (x, y, z)

    @staticmethod
    def interpolate(
            c1_srgb: tuple[float, float, float],
            c2_srgb: tuple[float, float, float],
            perc: float,
            oklab: bool = True,
    ) -> tuple[float, float, float]:
        if oklab:
            c1_oklab = Color.linear_srgb_to_oklab(c1_srgb)
            c2_oklab = Color.linear_srgb_to_oklab(c2_srgb)
            interpolated = Color.lerp(c1_oklab, c2_oklab, perc)
            interpolated = Color.oklab_to_linear_srgb(interpolated)

        else:
            interpolated = Color.lerp(c1_srgb, c2_srgb, perc)

        return interpolated


class CopicColor:
    def __init__(self, code: ColorCode, name: str, rgb: tuple[float, float, float]):
        self.code = code
        self.name = name
        self.rgb = rgb

    def __repr__(self):
        return f"{self.code.name}: {self.name}"

    def as_srgb(self) -> tuple[float, float, float]:
        return self.rgb[0] / 255, self.rgb[1] / 255, self.rgb[2] / 255


class CopicPhotograph:
    def __init__(self):
        self.colors = {}

        self.colors[ColorCode.Y06] = CopicColor(ColorCode.Y06, 'Yellow', (251, 238, 130))
        self.colors[ColorCode.YG21] = CopicColor(ColorCode.YG21, 'Anise', (227, 227, 170))
        self.colors[ColorCode.Y13] = CopicColor(ColorCode.Y13, 'Lemon Yellow', (248, 232, 153))
        self.colors[ColorCode.Y17] = CopicColor(ColorCode.Y17, 'Golden Yellow', (250, 189, 109))

        self.colors[ColorCode.YR24] = CopicColor(ColorCode.YR24, 'Pale Sepia', (166, 124, 104))
        self.colors[ColorCode.E37] = CopicColor(ColorCode.E37, 'Sepia', (192, 112, 85))
        self.colors[ColorCode.E39] = CopicColor(ColorCode.E39, 'Leather', (182, 99, 81))

        self.colors[ColorCode.RV13] = CopicColor(ColorCode.RV13, 'Tender Pink', (242, 185, 202))
        self.colors[ColorCode.RV09] = CopicColor(ColorCode.RV09, 'Fuchsia', (118, 96, 154))
        self.colors[ColorCode.R17] = CopicColor(ColorCode.R17, 'Lipstick Orange', (198, 77, 108))
        self.colors[ColorCode.YR07] = CopicColor(ColorCode.YR07, 'Cadmium Orange', (224, 99, 105))
        self.colors[ColorCode.R29] = CopicColor(ColorCode.R29, 'Lipstick Red', (222, 57, 108))

        self.colors[ColorCode.V12] = CopicColor(ColorCode.V12, 'Pale Lilac', (222, 204, 222))

        self.colors[ColorCode.G02] = CopicColor(ColorCode.G02, 'Spectrum Green', (155, 222, 175))
        self.colors[ColorCode.G14] = CopicColor(ColorCode.G14, 'Apple Green', (181, 221, 124))
        self.colors[ColorCode.G07] = CopicColor(ColorCode.G07, 'Nile Green', (92, 147, 92))
        self.colors[ColorCode.YG67] = CopicColor(ColorCode.YG67, 'Moss', (140, 164, 108))
        self.colors[ColorCode.G29] = CopicColor(ColorCode.G29, 'Pine Tree Green', (84, 125, 101))
        self.colors[ColorCode.G17] = CopicColor(ColorCode.G17, 'Forest Green', (60, 169, 116))
        self.colors[ColorCode.BG18] = CopicColor(ColorCode.BG18, 'Teal Blue', (121, 182, 181))

        self.colors[ColorCode.B12] = CopicColor(ColorCode.B12, 'Ice Blue', (73, 116, 182))
        self.colors[ColorCode.B24] = CopicColor(ColorCode.B24, 'Sky', (106, 180, 192))
        self.colors[ColorCode.B39] = CopicColor(ColorCode.B39, 'Prussian Blue', (71, 110, 160))

        self.colors[ColorCode.B110] = CopicColor(ColorCode.B110, 'Special Black', (75, 67, 74))

        self.colors[ColorCode.E97] = CopicColor(ColorCode.E97, 'Deep Orange', (246, 170, 116))
        self.colors[ColorCode.G40] = CopicColor(ColorCode.G40, 'Dim Green', (246, 246, 224))
        self.colors[ColorCode.YG01] = CopicColor(ColorCode.YG01, 'Green Bice', (223, 240, 89))
        self.colors[ColorCode.R20] = CopicColor(ColorCode.R20, 'Blush', (245, 198, 202))
        self.colors[ColorCode.YR04] = CopicColor(ColorCode.YR04, 'Chrome Orange', (248, 127, 87))
        self.colors[ColorCode.YR02] = CopicColor(ColorCode.YR02, 'Light Orange', (242, 145, 155))

        self.colors[ColorCode.E04] = CopicColor(ColorCode.E04, 'Lipstick Rose', (211, 150, 167))
        self.colors[ColorCode.G03] = CopicColor(ColorCode.G03, 'Maedow Green', (137, 218, 148))
        self.colors[ColorCode.BG09] = CopicColor(ColorCode.BG09, 'Blue Green', (41, 167, 168))
        self.colors[ColorCode.BG13] = CopicColor(ColorCode.BG13, 'Mint Green', (116, 217, 203))
        self.colors[ColorCode.BG15] = CopicColor(ColorCode.BG15, 'Aqua', (85, 212, 192))
        self.colors[ColorCode.G85] = CopicColor(ColorCode.G85, 'Verdigris', (165, 175, 134))


class Copic:
    def __init__(self):
        self.colors = {}

        self.colors[ColorCode.B110] = CopicColor(ColorCode.B110, "Special Black", (3, 7, 8))
        self.colors[ColorCode.B000] = CopicColor(ColorCode.B000, "White / Nothing", (255, 255, 255))

        self.colors[ColorCode.B12] = CopicColor(ColorCode.B12, "Ice Blue", (200, 230, 240))
        self.colors[ColorCode.B14] = CopicColor(ColorCode.B14, "Light Blue", (113, 207, 235))
        self.colors[ColorCode.B23] = CopicColor(ColorCode.B23, "Phthalo Blue", (146, 194, 232))
        self.colors[ColorCode.B24] = CopicColor(ColorCode.B24, "Sky", (138, 206, 243))
        self.colors[ColorCode.B29] = CopicColor(ColorCode.B29, "Ultramarine", (1, 119, 193))
        self.colors[ColorCode.B39] = CopicColor(ColorCode.B39, "Prussian Blue", (43, 100, 169))

        self.colors[ColorCode.BG09] = CopicColor(ColorCode.BG09, "Blue Green", (220, 240, 239))
        self.colors[ColorCode.BG10] = CopicColor(ColorCode.BG10, "Cool Shadow", (220, 240, 239))
        self.colors[ColorCode.BG13] = CopicColor(ColorCode.BG13, "Mint Green", (196, 231, 233))
        self.colors[ColorCode.BG15] = CopicColor(ColorCode.BG15, "Aqua", (160, 217, 210))
        self.colors[ColorCode.BG18] = CopicColor(ColorCode.BG18, "Teal Blue", (55, 192, 176))

        self.colors[ColorCode.BV0000] = CopicColor(ColorCode.BV0000, "Pale Thistle", (234, 231, 242))

        self.colors[ColorCode.E04] = CopicColor(ColorCode.E04, "Lipstick Rose", (228, 188, 196))
        self.colors[ColorCode.E37] = CopicColor(ColorCode.E37, "Sepia", (204, 145, 89))
        self.colors[ColorCode.E39] = CopicColor(ColorCode.E39, "Leather", (197, 116, 63))
        self.colors[ColorCode.E97] = CopicColor(ColorCode.E97, "Deep Orange", (180, 96, 52))

        self.colors[ColorCode.G02] = CopicColor(ColorCode.G02, "Spectrum Green", (207, 232, 211))
        self.colors[ColorCode.G03] = CopicColor(ColorCode.G03, "Maedow Green", (182, 218, 156))
        self.colors[ColorCode.G07] = CopicColor(ColorCode.G07, "Nile Green", (123, 197, 118))
        self.colors[ColorCode.G14] = CopicColor(ColorCode.G14, "Apple Green", (151, 207, 144))
        self.colors[ColorCode.G17] = CopicColor(ColorCode.G17, "Forest Green", (20, 179, 125))
        self.colors[ColorCode.G20] = CopicColor(ColorCode.G20, "Wax White", (237, 246, 219))
        self.colors[ColorCode.G29] = CopicColor(ColorCode.G29, "Pine Tree Green", (25, 124, 93))
        self.colors[ColorCode.G40] = CopicColor(ColorCode.G40, "Dim Green", (228, 241, 223))
        self.colors[ColorCode.G85] = CopicColor(ColorCode.G85, "Verdigris", (157, 195, 170))

        self.colors[ColorCode.R00] = CopicColor(ColorCode.R00, "Pinkish White", (254, 234, 225))
        self.colors[ColorCode.R01] = CopicColor(ColorCode.R01, "Pinkish Vanilla", (253, 224, 216))
        self.colors[ColorCode.R02] = CopicColor(ColorCode.R02, "Rose Salmon", (253, 211, 199))
        self.colors[ColorCode.R17] = CopicColor(ColorCode.R17, "Lipstick Orange", (244, 132, 108))
        self.colors[ColorCode.R20] = CopicColor(ColorCode.R20, "Blush", (252, 215, 207))
        self.colors[ColorCode.R29] = CopicColor(ColorCode.R29, "Lipstick Red", (237, 23, 75))

        self.colors[ColorCode.RV09] = CopicColor(ColorCode.RV09, "Fuchsia", (255, 87, 51))
        self.colors[ColorCode.RV13] = CopicColor(ColorCode.RV13, "Tender Pink", (249, 201, 215))
        self.colors[ColorCode.RV93] = CopicColor(ColorCode.RV93, "Smoky Purple", (234, 190, 209))

        self.colors[ColorCode.Y06] = CopicColor(ColorCode.Y06, "Yellow", (254, 245, 108))
        self.colors[ColorCode.Y13] = CopicColor(ColorCode.Y13, "Lemon Yellow", (251, 247, 174))
        self.colors[ColorCode.Y17] = CopicColor(ColorCode.Y17, "Golden Yellow", (255, 228, 85))

        self.colors[ColorCode.YG01] = CopicColor(ColorCode.YG01, "Green Bice", (226, 235, 178))
        self.colors[ColorCode.YG21] = CopicColor(ColorCode.YG21, "Anise", (247, 246, 190))
        self.colors[ColorCode.YG67] = CopicColor(ColorCode.YG67, "Moss", (129, 191, 140))

        self.colors[ColorCode.YR02] = CopicColor(ColorCode.YR02, "Light Orange", (252, 220, 197))
        self.colors[ColorCode.YR04] = CopicColor(ColorCode.YR04, "Chrome Orange", (254, 195, 105))
        self.colors[ColorCode.YR07] = CopicColor(ColorCode.YR07, "Cadmium Orange", (242, 111, 57))
        self.colors[ColorCode.YR24] = CopicColor(ColorCode.YR24, "Pale Sepia", (240, 207, 100))

        self.colors[ColorCode.V12] = CopicColor(ColorCode.V12, "Pale Lilac", (238, 215, 233))
        self.colors[ColorCode.V17] = CopicColor(ColorCode.V17, "Amethyst", (160, 146, 199))

        self.colors[ColorCode.N3] = CopicColor(ColorCode.N3, "Neutral Gray no.3", (209, 210, 212))
        self.colors[ColorCode.T9] = CopicColor(ColorCode.T9, "Toner Gray no.9", (76, 75, 73))
        self.colors[ColorCode.W9] = CopicColor(ColorCode.W9, "Warm Gray no.9", (76, 77, 72))

    def color(self, code: ColorCode) -> CopicColor:
        return self.colors[code]

    def random(self) -> CopicColor:
        return random.choice(list(self.colors.values()))

    def most_similar(self, c1_rgb: tuple[int, int, int]) -> CopicColor:
        """
        put in a color in RGB (0-255)
        will return the most similar color of the available Copic colors
        the similarity is calculated in CIE 1931 color space
        """
        color_srgb = c1_rgb[0] / 255, c1_rgb[1] / 255, c1_rgb[2] / 255

        color_to_compare_cie = colour.sRGB_to_XYZ(color_srgb)

        deltas = {}
        for copic_color_code, copic_color in Copic().colors.items():
            copic_color_srgb = copic_color.as_srgb()
            copic_color_cie = colour.sRGB_to_XYZ(copic_color_srgb)

            # color difference in CIE2000 (Color Difference Formula)
            # Designed to quantify the perceptual difference between two colors.
            # Offers more consistent and accurate results, particularly for large color differences and in
            # problematic regions of previous formulas (e.g., blues). ncorporates corrections for lightness,
            # chroma, and hue differences, as well as terms to account for interactions between these color
            # attributes. Used in various industries for quality control and to ensure color consistency.
            delta = colour.delta_E(color_to_compare_cie, copic_color_cie)

            deltas[copic_color_code] = delta

        sorted_deltas = dict(sorted(deltas.items(), key=lambda item: item[1]))

        first_key = list(sorted_deltas.keys())[0]
        return Copic().colors[first_key]