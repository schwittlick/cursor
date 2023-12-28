import json
import random
import pathlib
import colour

from cursor.algorithm.color.copic_pen_enum import CopicPen


class CopicColor:
    def __init__(self, code: CopicPen, name: str, rgb: tuple[float, float, float]):
        self.code = code
        self.name = name
        self.rgb = rgb

    def __repr__(self):
        return f"{self.code.name}: {self.name}"

    def as_srgb(self) -> tuple[float, float, float]:
        return self.rgb[0] / 255, self.rgb[1] / 255, self.rgb[2] / 255


class Copic:
    def __init__(self):
        self.available_colors = self.__parse_data()

    def __parse_data(self) -> dict[CopicPen, CopicColor]:
        """
        parses all copic color information from a json data file
        only colors that are added to the ColorCode enum class are indexed
        these are the colors that have a representation as a pen in the lab
        """
        copic_data_final = {}
        here = pathlib.Path(__file__).parent
        with open(here / "data" / "data_copic.json", 'r') as copic_data_file:
            all_data = "".join(copic_data_file.readlines())
            copic_data = json.loads(all_data)
            for element in copic_data:
                try:
                    id = CopicPen[element["id"]]
                    rgb = str(element['rgb']).split(',')
                    rgb_tup = int(rgb[0]), int(rgb[1]), int(rgb[2])
                    copic_data_final[id] = CopicColor(id, element['name'], rgb_tup)
                except KeyError:
                    # only adding colors that have been turned into a pen
                    pass
        return copic_data_final

    def color(self, code: CopicPen) -> CopicColor:
        return self.available_colors[code]

    def random(self) -> CopicColor:
        return random.choice(list(self.available_colors.values()))

    def most_similar(self, c1_rgb: tuple[int, int, int]) -> CopicColor:
        """
        put in a color in RGB (0-255)
        will return the most similar color of the available Copic colors
        the similarity is calculated in CIE 1931 color space
        """
        color_srgb = c1_rgb[0] / 255, c1_rgb[1] / 255, c1_rgb[2] / 255

        color_to_compare_cie = colour.sRGB_to_XYZ(color_srgb)

        deltas = {}
        for copic_color_code, copic_color in Copic().available_colors.items():
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
        return Copic().available_colors[first_key]
