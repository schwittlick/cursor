import logging
import math
from collections import defaultdict

from cursor.algorithm.color.copic import Color, Copic
from cursor.algorithm.color.copic_pen_enum import CopicColorCode
from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property


def convert_color_coordinates_to_collection(
    color_coords: dict[CopicColorCode, list[tuple]], legende_x: bool, legende_y: bool
) -> Collection:
    """
    creates a layered collection with 8 pens per layer
    sorts the layers by color group, in order to avoid chaos when loading up the pens
    first all blues, then greens, all reds, all RV etc etc
    before that it rotates all points by n degrees from the center of its bounding box
    """
    all_points = [coord for coords in color_coords.values() for coord in coords]
    bb = Path.from_tuple_list(all_points).bb()
    center_x, center_y = bb.center()

    angle = math.radians(0)
    cos_theta, sin_theta = math.cos(angle), math.sin(angle)

    all_paths = Collection()
    for color, coordinates in color_coords.items():
        for coordinate in coordinates:
            x, y = coordinate
            dx, dy = x - center_x, y - center_y
            rotated_x = center_x + (dx * cos_theta - dy * sin_theta)
            rotated_y = center_y + (dx * sin_theta + dy * cos_theta)
            pixel = Path.from_tuple_list([(rotated_x, rotated_y), (rotated_x, rotated_y)])
            pixel.properties["copic_color"] = Copic().color_by_code(color)
            all_paths.add(pixel)

    return sort_collection_by_copic_color_group(all_paths, legende_x, legende_y)


def sort_collection_by_copic_color(collection: Collection) -> dict[Color, Collection]:
    colors: dict[Color, Collection] = {}
    for path in collection:
        path_color = path.properties["copic_color"]
        if path_color not in colors.keys():
            colors[path_color] = Collection()
        colors[path_color].add(path)

    return dict(sorted(colors.items()))


def create_legend_path(
    x: float,
    y: float,
    layer_index: int,
    pen_index: int,
    path_color: Color,
    radius: int,
) -> Path:
    legend_path = Path([Position(x, y), Position(x, y)])
    legend_path.layer = layer_index
    legend_path.pen_select = pen_index
    legend_path.color = path_color.as_rgb()
    legend_path.properties[Property.COPIC_COLOR] = path_color
    for pos in legend_path:
        pos.radius = radius
        pos.color = path_color.as_rgb()
        pos.properties[Property.COPIC_COLOR] = path_color
    return legend_path


def add_legende_all_corners(collection_bb, layer_index, c, pen_index, path_color, legende_scale, radius):
    num_legend_points = 3

    x = collection_bb.x2 + layer_index * legende_scale  # left side for legende
    y = collection_bb.y2 - pen_index * legende_scale
    for _ in range(num_legend_points):
        legend_path = create_legend_path(x, y, layer_index, pen_index, path_color, radius)
        c.add(legend_path)

    x = collection_bb.x2 + layer_index * legende_scale  # left side for legende
    y = collection_bb.y + pen_index * legende_scale
    for _ in range(num_legend_points):
        legend_path = create_legend_path(x, y, layer_index, pen_index, path_color, radius)
        c.add(legend_path)

    x = collection_bb.x + layer_index * legende_scale  # legende on right side
    y = collection_bb.y2 - pen_index * legende_scale
    for _ in range(num_legend_points):
        legend_path = create_legend_path(x, y, layer_index, pen_index, path_color, radius)
        c.add(legend_path)

    x = collection_bb.x + layer_index * legende_scale  # legende on right side
    y = collection_bb.y + pen_index * legende_scale
    for _ in range(num_legend_points):
        legend_path = create_legend_path(x, y, layer_index, pen_index, path_color, radius)
        c.add(legend_path)


_PENS_PER_LAYER = 8
_LEGEND_POINTS = 3
_LEGEND_OFFSET = 400  # 400 units = 1mm in plotter space


def legend_x_extent(legende_scale: float) -> float:
    """Return the max x space (in plotter units) the legend adds to the right of content bb.x2."""
    return _LEGEND_OFFSET + _PENS_PER_LAYER * legende_scale


def _group_paths_by_color_code(collection: Collection) -> dict:
    groups = defaultdict(Collection)
    for path in collection:
        color = path.properties[Property.COPIC_COLOR]
        key = color.code if color.code is not None else color
        groups[key].add(path)
    return groups


def _build_legend_paths(
    bb,
    pen_index: int,
    layer_index: int,
    path_color: Color,
    radius: int,
    legende_x: bool,
    legende_y: bool,
    legende_scale: float,
) -> Collection:
    x = (bb.x2 + _LEGEND_OFFSET if legende_x else bb.x - _LEGEND_OFFSET) + pen_index * legende_scale
    y = (bb.y2 if legende_y else bb.y) + layer_index * legende_scale

    legend = Collection()
    for _ in range(_LEGEND_POINTS):
        legend.add(create_legend_path(x, y, layer_index, pen_index, path_color, radius))
    return legend


def sort_collection_by_copic_color_group(
    collection: Collection,
    legende_x: bool = False,
    legende_y: bool = False,
    legende_scale: float = 1,
    draw_legend: bool = True,
) -> Collection:
    """
    Sorts paths into layers and pens by copic color code.
    Coordinates are in pixel space, not hpgl/plotter space.
    """
    result = Collection()
    pen_mapping: dict[int, dict[int, Color]] = {}
    layer_pen_mapping: dict[int, Color] = {}
    pen_index = 1
    layer_index = 0

    radius = collection.paths[0][0].radius or 0
    bb = collection.bb()
    paths_by_code = _group_paths_by_color_code(collection)

    logging.info(f"{len(paths_by_code)} colors detected")

    for paths_same_code in paths_by_code.values():
        for path_color, paths_same_color in sort_collection_by_copic_color(paths_same_code).items():
            layer_pen_mapping[pen_index] = path_color

            legend = (
                _build_legend_paths(bb, pen_index, layer_index, path_color, radius, legende_x, legende_y, legende_scale)
                if draw_legend
                else Collection()
            )

            for path in legend:
                result.add(path.copy())

            for path in paths_same_color:
                path.pen_select = pen_index
                path.layer = layer_index
                result.add(path)

            for path in legend:
                result.add(path.copy())

            pen_index += 1

            if pen_index > _PENS_PER_LAYER:
                pen_mapping[layer_index] = layer_pen_mapping.copy()
                layer_pen_mapping = {}
                pen_index = 1
                layer_index += 1

        pen_mapping[layer_index] = layer_pen_mapping.copy()
        layer_pen_mapping = {}
        layer_index += 1
        pen_index = 1

    result.properties["pen_mapping"] = pen_mapping

    return result


if __name__ == "__main__":
    collection = Collection()

    p1 = Path(
        [Position(0, 0), Position(1, 1)],
        {"copic_color": Copic().color_by_code(CopicColorCode.B0000)},
    )
    p2 = Path(
        [Position(0, 0), Position(1, 1)],
        {"copic_color": Copic().color_by_code(CopicColorCode.B000)},
    )
    p3_2 = Path(
        [Position(0, 0), Position(1, 1)],
        {"copic_color": Copic().color_by_code(CopicColorCode.R01)},
    )
    p3 = Path(
        [Position(0, 0), Position(1, 1)],
        {"copic_color": Copic().color_by_code(CopicColorCode.B99)},
    )
    p4 = Path(
        [Position(0, 0), Position(1, 1)],
        {"copic_color": Copic().color_by_code(CopicColorCode.B39)},
    )
    p5 = Path(
        [Position(0, 0), Position(1, 1)],
        {"copic_color": Copic().color_by_code(CopicColorCode.B12)},
    )
    p5_2 = Path(
        [Position(0, 0), Position(1, 1)],
        {"copic_color": Copic().color_by_code(CopicColorCode.R08)},
    )

    collection.add(p1)
    collection.add(p2)
    collection.add(p3)
    collection.add(p3_2)
    collection.add(p4)
    collection.add(p5)
    collection.add(p5_2)

    sorted_paths = sort_collection_by_copic_color_group(collection)
    for p in sorted_paths:
        print(p.properties["copic_color"])
    print(sorted_paths)
