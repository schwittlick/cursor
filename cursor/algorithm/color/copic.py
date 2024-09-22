from __future__ import annotations

import json
import logging
import pathlib
import random

import colour

from cursor.algorithm.color.copic_pen_enum import CopicColorCode as CCC
from cursor.algorithm.color.copic_pen_enum import CopicColorGroup as CCG
from cursor.algorithm.kd import KDTree
from cursor.timer import timing


class Color:
    def __init__(
            self, rgb: tuple[float, float, float], code: CCC = None, group: CCG = None, name: str = "NoName"
    ):
        self.code = code
        self.group = group
        self.name = name
        self.__rgb = rgb

    def is_copic(self) -> bool:
        return True if self.code else False

    def as_srgb(self) -> tuple[float, ...]:
        return self.__rgb

    def as_rgb(self) -> tuple[int, ...]:
        return tuple(int(v * 255) for v in self.__rgb)

    def __repr__(self):
        if self.code:
            return f"{self.code.name}: {self.name}"
        else:
            return f"{self.__rgb}"

    def __eq__(self, other: Color):
        return self.code == other.code

    def __lt__(self, other: Color):
        return self.code.value < other.code.value

    def __hash__(self):
        return hash(str(self.__rgb))


class Copic:
    _instance = None
    available_colors_pens = None
    available_colors = None
    rgb_kdtree = None

    def __new__(cls):
        """
        Singleton so all this is never parsed twice
        """
        if cls._instance is None:
            cls._instance = super(Copic, cls).__new__(cls)
            cls.available_colors_pens: dict[CCG, list[CCC]] = init_available_pens()
            cls.available_colors, cls.available_colors_rgb_index = cls.__parse_data(cls)

        return cls._instance

    def __parse_data(self) -> tuple[dict[CCC, Color], dict[tuple, Color]]:
        """
        parses all copic color information from a json data file
        only colors that are added to the ColorCode enum class are indexed
        these are the colors that have a representation as a pen in the lab
        """

        logging.info("Loading Copic data..")
        copic_data_final = {}
        copic_data_srgb_index_final = {}
        here = pathlib.Path(__file__).parent
        with open(here / "data" / "data_copic.json", "r") as copic_data_file:
            all_data = "".join(copic_data_file.readlines())
            copic_data = json.loads(all_data)
            for element in copic_data:
                try:
                    id_str = element["id"]

                    if id_str == "110":
                        id_str = (
                            "_110"  # can't use an enum starting with a number in python
                        )
                    id = CCC[id_str]

                    for ccg, ccc in self.available_colors_pens.items():
                        if id in ccc:
                            rgb = str(element["rgb"]).split(",")
                            rgb_tup = int(rgb[0]) / 255, int(rgb[1]) / 255, int(rgb[2]) / 255
                            color = Color(rgb_tup, id, ccg, element["name"])
                            copic_data_final[id] = color
                            copic_data_srgb_index_final[color.as_srgb()] = color
                except KeyError:
                    # only adding colors that have been turned into a pen
                    pass
        logging.info(".. done")
        return copic_data_final, copic_data_srgb_index_final

    def color_by_code(self, code: CCC) -> Color:
        return self.available_colors[code]

    def color_by_srgb(self, srgb_tuple: tuple[float, float, float]) -> Color:
        if srgb_tuple in self.available_colors_rgb_index.keys():
            return self.available_colors_rgb_index[srgb_tuple]
        raise Exception("No available color with this srgb tuple")

    def random(self) -> Color:
        return random.choice(list(self.available_colors.values()))

    def get_colors_by_group(self, ccg: CCG) -> list[CCC]:
        """
        Returns a list of Copic colors from the passed in color group enum
        """
        return self.available_colors_pens[ccg]

    def most_similar_rgb_kdtree(self, c1_rgbs: tuple[float, float, float]) -> Color:
        """
        Simply create a kd-tree here and add all rgb values of available copic colors
        here just find the closest one in linear euclidean distance space
        should be much faster. but is there a difference? a test should be written
        to compare the results of this and the better function below.
        eventually we could pre-compute all distances for each and just save that up.
        should be a small file that can just live next to the copic_data json. maybe even
        add that data to the json
        """
        if not self.rgb_kdtree:
            rgb_points = [color.as_srgb() for ccc, color in self.available_colors.items()]
            self.rgb_kdtree = KDTree(rgb_points, 3)

        rgb_dist, closest_color = self.rgb_kdtree.get_nearest(c1_rgbs)
        closest = self.available_colors_rgb_index[closest_color]
        return closest

    @timing
    def most_similar(self, c1_rgb: tuple[float, float, float]) -> Color:
        """
        put in a color in RGB (0-1)
        will return the most similar color of the available Copic colors
        the similarity is calculated in CIE 1931 color space
        """
        color_to_compare_cie = colour.sRGB_to_XYZ(c1_rgb)

        deltas = {}
        for copic_color_code, copic_color in self.available_colors.items():
            copic_color_cie = colour.sRGB_to_XYZ(copic_color.as_srgb())

            # color difference in CIE2000 (Color Difference Formula)
            # Designed to quantify the perceptual difference between two colors.
            # Offers more consistent and accurate results, particularly for large color differences and in
            # problematic regions of previous formulas (e.g., blues). incorporates corrections for lightness,
            # chroma, and hue differences, as well as terms to account for interactions between these color
            # attributes. Used in various industries for quality control and to ensure color consistency.
            delta = colour.delta_E(color_to_compare_cie, copic_color_cie)

            deltas[copic_color_code] = delta

        sorted_deltas = dict(sorted(deltas.items(), key=lambda item: item[1]))

        first_key = list(sorted_deltas.keys())[0]
        return self.available_colors[first_key]


def init_available_pens() -> dict[CCG, list[CCC]]:
    pens: dict[CCG, list[CCC]] = {}

    pens[CCG.BLACK] = [
        CCC._110
    ]

    pens[CCG.BV] = [
        CCC.BV0000, CCC.BV04, CCC.BV11, CCC.BV20, CCC.BV31, CCC.BV34
    ]

    pens[CCG.V] = [
        CCC.V09, CCC.V12, CCC.V15, CCC.V17, CCC.V20, CCC.V91, CCC.V99, CCC.FV
    ]

    pens[CCG.RV] = [
        CCC.RV06, CCC.RV09, CCC.RV11, CCC.RV13, CCC.RV19, CCC.RV29, CCC.RV63, CCC.RV93,
        CCC.FRV1,
    ]

    pens[CCG.R] = [
        CCC.R00, CCC.R01, CCC.R02, CCC.R05, CCC.R08, CCC.R11, CCC.R12, CCC.R14, CCC.R17, CCC.R20, CCC.R21,
        CCC.R22, CCC.R24, CCC.R27, CCC.R29, CCC.R30, CCC.R32, CCC.R35, CCC.R37, CCC.R39, CCC.R43, CCC.R46,
        CCC.R56, CCC.R59, CCC.R81, CCC.R83, CCC.R85, CCC.R89,
    ]

    pens[CCG.YR] = [
        CCC.YR01, CCC.YR02, CCC.YR04, CCC.YR07, CCC.YR12, CCC.YR18, CCC.YR23, CCC.YR24, CCC.YR68,
        CCC.FYR,
    ]

    pens[CCG.Y] = [
        CCC.Y00, CCC.Y02, CCC.Y04, CCC.Y06, CCC.Y08, CCC.Y11, CCC.Y13, CCC.Y15, CCC.Y17, CCC.Y18, CCC.Y19,
        CCC.Y21, CCC.Y23, CCC.Y28, CCC.Y32, CCC.Y35, CCC.Y38,
        CCC.FY1,
    ]

    pens[CCG.YG] = [
        CCC.YG01, CCC.YG05, CCC.YG11, CCC.YG21, CCC.YG25, CCC.YG45, CCC.YG67, CCC.YG91,
        CCC.FYG1,
    ]

    pens[CCG.G] = [
        CCC.G00, CCC.G02, CCC.G03, CCC.G05, CCC.G07, CCC.G09, CCC.G12, CCC.G14, CCC.G16, CCC.G17, CCC.G19,
        CCC.G20, CCC.G21, CCC.G24, CCC.G28, CCC.G29, CCC.G40, CCC.G43, CCC.G46, CCC.G82, CCC.G85, CCC.G94,
        CCC.G99,
        CCC.FYG2,
    ]

    pens[CCG.BG] = [
        CCC.BG01, CCC.BG02, CCC.BG07, CCC.BG09, CCC.BG10, CCC.BG13, CCC.BG15, CCC.BG18, CCC.BG57, CCC.BG72,
        CCC.FBG2,
    ]

    pens[CCG.B] = [
        CCC.B0000, CCC.B000, CCC.B00, CCC.B01, CCC.B02, CCC.B04, CCC.B05, CCC.B06, CCC.B12, CCC.B14, CCC.B16,
        CCC.B18, CCC.B21, CCC.B23, CCC.B24, CCC.B26, CCC.B28, CCC.B29, CCC.B32, CCC.B34, CCC.B37, CCC.B39,
        CCC.B41, CCC.B45, CCC.B52, CCC.B60, CCC.B63, CCC.B66, CCC.B69, CCC.B79, CCC.B91, CCC.B93, CCC.B95,
        CCC.B97, CCC.B99,
        CCC.FB2,
    ]

    pens[CCG.E] = [
        CCC.E01, CCC.E04, CCC.E11, CCC.E17, CCC.E23, CCC.E37, CCC.E39, CCC.E53, CCC.E87, CCC.E97,
    ]

    pens[CCG.W] = [
        CCC.W1, CCC.W2, CCC.W3, CCC.W4, CCC.W5, CCC.W6, CCC.W8, CCC.W9, CCC.W10
    ]

    pens[CCG.T] = [
        CCC.T9
    ]

    pens[CCG.N] = [
        CCC.N3
    ]

    return pens
