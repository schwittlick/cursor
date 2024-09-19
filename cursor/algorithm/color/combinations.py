import json
import pathlib
from typing import List, Dict, Tuple

import colour


class Color:
    def __init__(self, name: str, hex: str, rgb: List[int], lab: List[float], cmyk: List[int], combinations: List[int]):
        self.name = name
        self.hex = hex
        self.rgb = tuple(rgb)
        self.lab = tuple(lab)
        self.cmyk = tuple(cmyk)
        self.combinations = combinations

    def as_srgb(self) -> Tuple[float, float, float]:
        return tuple(v / 255 for v in self.rgb)


class ColorDictionary:
    def __init__(self):
        self.colors: Dict[str, Color] = {}

        data_path = pathlib.Path(__file__).parent / "data" / "color_dictionary.json"
        self.load_colors(data_path.as_posix())

    def load_colors(self, json_file: str):
        with open(json_file, 'r') as f:
            color_data = json.load(f)

        for color in color_data:
            self.colors[color['name']] = Color(
                name=color['name'],
                hex=color['hex'],
                rgb=color['rgb'],
                lab=color['lab'],
                cmyk=color['cmyk'],
                combinations=color.get('combinations', [])
            )

    def get_color(self, name: str) -> Color:
        return self.colors.get(name)

    def most_similar(self, target_color: Tuple[float, float, float]) -> Color:
        target_cie = colour.sRGB_to_XYZ(target_color)

        min_delta = float('inf')
        most_similar_color = None

        for color in self.colors.values():
            color_cie = colour.sRGB_to_XYZ(color.as_srgb())
            delta = colour.delta_E(target_cie, color_cie)

            if delta < min_delta:
                min_delta = delta
                most_similar_color = color

        return most_similar_color

    def compare_with_copic(self, copic_color: 'Color', copic_instance: 'Copic') -> Tuple[Color, float]:
        target_rgb = copic_color.as_srgb()
        color_dict_match = self.most_similar(target_rgb)

        copic_cie = colour.sRGB_to_XYZ(target_rgb)
        color_dict_cie = colour.sRGB_to_XYZ(color_dict_match.as_srgb())

        delta = colour.delta_E(copic_cie, color_dict_cie)

        return color_dict_match, delta
