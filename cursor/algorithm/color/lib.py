import logging
import math

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
    radius: float,
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


def sort_collection_by_copic_color_group(
    collection: Collection,
    legende_x: bool = False,
    legende_y: bool = False,
    legende_scale: float = 1,
) -> Collection:
    """
    the coordinates of the paths are in pixel space, not in hpgl/plotter space
    """
    out_color_names_pen_mapping = {}
    color_names_pen_mapping = {}

    c = Collection()

    # toggle to separate each pen in a new layer
    separate_sp_to_layer = True

    pen_index = 1
    layer_index = 0
    pens = {}

    radius = collection.paths[0][0].radius

    # separating app paths by the copic color code
    for path in collection:
        path_copic_color = path.properties[Property.COPIC_COLOR]
        if path_copic_color.code not in pens.keys():
            pens[path_copic_color.code] = Collection()

        pens[path_copic_color.code].add(path)

    logging.info(f"{len(pens)} colors detected")
    collection_bb = collection.bb()

    for _, paths in pens.items():
        sorted_by_colors = sort_collection_by_copic_color(paths)

        for path_color, paths_same_color in sorted_by_colors.items():
            color_names_pen_mapping[pen_index] = path_color.code

            # logging.info(f"travel pen up distance before tsp: {paths_same_color.calc_pen_up_distance(40):.2f} mm")
            # paths_same_color.fast_tsp(plot_preview=False, duration_seconds=1)
            # logging.info(f"travel pen up distance after tsp: {paths_same_color.calc_pen_up_distance(40):.2f} mm")

            legend_paths = Collection()
            wtf = True
            if wtf:
                all_corners = False
                if all_corners:
                    add_legende_all_corners(
                        collection_bb,
                        layer_index,
                        legend_paths,
                        pen_index,
                        path_color,
                        legende_scale,
                        radius,
                    )
                else:
                    num_legend_points = 3

                    absolute = False
                    absolute_offset = (400, 400)  # 40 = 1mm

                    if absolute:
                        x = absolute_offset[0] + layer_index * legende_scale
                        y = absolute_offset[1] + pen_index * legende_scale
                        for _ in range(num_legend_points):
                            legend_path = create_legend_path(x, y, layer_index, pen_index, path_color, radius)
                            legend_paths.add(legend_path)
                    else:
                        # adding legende of used colors
                        if legende_x:
                            x = (
                                collection_bb.x2 + absolute_offset[0] + pen_index * legende_scale
                            )  # left side for legende
                        else:
                            x = (
                                collection_bb.x - absolute_offset[0] + pen_index * legende_scale
                            )  # legende on right side
                        if legende_y:
                            y = collection_bb.y2 + layer_index * legende_scale
                        else:
                            y = collection_bb.y + layer_index * legende_scale

                        for _ in range(num_legend_points):
                            legend_path = create_legend_path(x, y, layer_index, pen_index, path_color, radius)
                            legend_paths.add(legend_path)

            # adds legend paths at beginning of layer
            for path in legend_paths:
                c.add(path.copy())

            for path in paths_same_color:
                path.pen_select = pen_index
                path.layer = layer_index
                # path.color = path_color.as_rgb()
                # path.properties[Property.COPIC_COLOR] = path_color

                c.add(path)

            # adds legend paths at end of layer
            for path in legend_paths:
                c.add(path.copy())

            pen_index += 1

            if pen_index == 9:
                out_color_names_pen_mapping[layer_index] = color_names_pen_mapping.copy()
                color_names_pen_mapping = {}
                pen_index = 1
                layer_index += 1

        if separate_sp_to_layer:
            out_color_names_pen_mapping[layer_index] = color_names_pen_mapping.copy()
            layer_index += 1
            pen_index = 1

    if not separate_sp_to_layer:
        out_color_names_pen_mapping[layer_index] = color_names_pen_mapping.copy()

    c.properties["pen_mapping"] = out_color_names_pen_mapping

    return c


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
