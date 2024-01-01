import json
import random
import pathlib
import colour

from cursor.algorithm.color.copic_pen_enum import CopicColorCode as CCC


class Color:
    def __init__(self, rgb: tuple[float, float, float], code: CCC = None, name: str = "NoName"):
        self.code = code
        self.name = name
        self.__rgb = rgb

    def is_copic(self) -> bool:
        return True if self.code else False

    def __repr__(self):
        if self.code:
            return f"{self.code.name}: {self.name}"
        else:
            return f"{self.__rgb}"

    def as_srgb(self) -> tuple[float, ...]:
        return self.__rgb

    def as_rgb(self) -> tuple[int, ...]:
        return tuple(int(v * 255) for v in self.__rgb)


class Copic:
    def __init__(self):
        self.available_colors_pens = self.init_available_pens()
        self.available_colors = self.__parse_data()

    def init_available_pens(self) -> list[CCC]:
        pens = []
        pens.extend([CCC._110])
        pens.extend(
            [CCC.B0000, CCC.B000, CCC.B00, CCC.B01, CCC.B02, CCC.B04, CCC.B05,
             CCC.B06, CCC.B12, CCC.B14, CCC.B16, CCC.B18, CCC.B21, CCC.B23, CCC.B24,
             CCC.B26, CCC.B28, CCC.B29, CCC.B32, CCC.B34, CCC.B37, CCC.B39, CCC.B41,
             CCC.B45, CCC.B52, CCC.B60, CCC.B63, CCC.B66, CCC.B69, CCC.B79, CCC.B91,
             CCC.B93, CCC.B95, CCC.B97, CCC.B99,
             CCC.FB2])

        pens.extend(
            [CCC.Y00, CCC.Y02, CCC.Y04, CCC.Y06, CCC.Y08, CCC.Y11, CCC.Y13, CCC.Y15, CCC.Y17,
             CCC.Y18, CCC.Y19, CCC.Y21, CCC.Y23, CCC.Y28, CCC.Y32, CCC.Y35, CCC.Y38,
             CCC.FY1])

        pens.extend(
            [CCC.R00, CCC.R01, CCC.R02, CCC.R05, CCC.R08, CCC.R11, CCC.R12, CCC.R14, CCC.R17,
             CCC.R20, CCC.R21, CCC.R22, CCC.R24, CCC.R27, CCC.R29, CCC.R30, CCC.R32, CCC.R35,
             CCC.R37, CCC.R39, CCC.R43, CCC.R46, CCC.R56, CCC.R59, CCC.R81, CCC.R83, CCC.R85,
             CCC.R89,
             CCC.FRV1])

        pens.extend(
            [CCC.G00, CCC.G02, CCC.G03, CCC.G05, CCC.G07, CCC.G14, CCC.G17, CCC.G29, CCC.G85])

        return pens

    def __parse_data(self) -> dict[CCC, Color]:
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
                    id = CCC[element["id"]]

                    if id not in self.available_colors_pens:
                        continue

                    rgb = str(element['rgb']).split(',')
                    rgb_tup = int(rgb[0]) / 255, int(rgb[1]) / 255, int(rgb[2]) / 255
                    copic_data_final[id] = Color(rgb_tup, id, element['name'])
                except KeyError:
                    # only adding colors that have been turned into a pen
                    pass
        return copic_data_final

    def color(self, code: CCC) -> Color:
        return self.available_colors[code]

    def random(self) -> Color:
        return random.choice(list(self.available_colors.values()))

    def most_similar(self, c1_rgb: tuple[float, float, float]) -> Color:
        """
        put in a color in RGB (0-1)
        will return the most similar color of the available Copic colors
        the similarity is calculated in CIE 1931 color space
        """
        color_to_compare_cie = colour.sRGB_to_XYZ(c1_rgb)

        deltas = {}
        for copic_color_code, copic_color in Copic().available_colors.items():
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
        return Copic().available_colors[first_key]
