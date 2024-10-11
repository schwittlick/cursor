from typing import Tuple
import colour

from cursor.algorithm.color.combinations import ColorDictionary
from cursor.algorithm.color.copic import Copic, Color as CopicColor


def find_similar_copic_color(color_dict: ColorDictionary, copic: Copic, target_color_name: str) -> Tuple[
        CopicColor, float]:
    target_color = color_dict.get_color(target_color_name)
    if not target_color:
        raise ValueError(
            f"Color '{target_color_name}' not found in ColorDictionary")

    target_rgb = tuple(v / 255 for v in target_color.rgb)
    target_xyz = colour.sRGB_to_XYZ(target_rgb)
    target_lab = colour.XYZ_to_Lab(target_xyz)

    min_delta = float('inf')
    most_similar_color = None

    for copic_color in copic.available_colors.values():
        copic_xyz = colour.sRGB_to_XYZ(copic_color.as_srgb())
        copic_lab = colour.XYZ_to_Lab(copic_xyz)
        delta = colour.delta_E(target_lab, copic_lab, method='CIE 2000')

        if delta < min_delta:
            min_delta = delta
            most_similar_color = copic_color

    return most_similar_color, min_delta


def test_comparison():
    color_dict = ColorDictionary()
    copic = Copic()
    copic_color = copic.random()
    match, delta = color_dict.compare_with_copic(copic_color, copic)
    print(
        f"Copic color {copic_color.name} is most similar to {match.name} with delta {delta}")


def test_more():
    color_dict = ColorDictionary()
    copic = Copic()

    # target_color_name = "Dark Tyrian Blue"
    target_color_name = "Pinkish Cinnamon"
    similar_copic, delta = find_similar_copic_color(
        color_dict, copic, target_color_name)

    target_color = color_dict.get_color(target_color_name)
    print(f"Target color: {target_color_name} (#{target_color.hex})")
    print(
        f"Most similar Copic color: {similar_copic.name} "
        f"({similar_copic.code.name}) "
        f"(#{similar_copic.as_rgb()[0]:02x}"
        f"{similar_copic.as_rgb()[1]:02x}"
        f"{similar_copic.as_rgb()[2]:02x})"
    )
    print(f"Color difference (Delta E): {delta:.2f}")

    # Print the top 5 closest matches
    print("\nTop 5 closest Copic colors:")
    sorted_colors = sorted(copic.available_colors.values(), key=lambda c: colour.delta_E(
        colour.XYZ_to_Lab(colour.sRGB_to_XYZ(
            tuple(v / 255 for v in target_color.rgb))),
        colour.XYZ_to_Lab(colour.sRGB_to_XYZ(c.as_srgb())),
        method='CIE 2000'
    ))
    for i, color in enumerate(sorted_colors[:5], 1):
        delta = colour.delta_E(
            colour.XYZ_to_Lab(colour.sRGB_to_XYZ(
                tuple(v / 255 for v in target_color.rgb))),
            colour.XYZ_to_Lab(colour.sRGB_to_XYZ(color.as_srgb())),
            method='CIE 2000'
        )
        print(
            f"{i}. {color.name} ({color.code.name}) "
            f"(#{color.as_rgb()[0]:02x}{color.as_rgb()[1]:02x}{color.as_rgb()[2]:02x}) "
            f"- Delta E: {delta:.2f}"
        )
