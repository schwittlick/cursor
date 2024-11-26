from cursor.algorithm.color.copic import Copic, Color
from cursor.algorithm.color.copic_pen_enum import CopicColorCode
from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position


def convert_color_coordinates_to_collection(color_coords: dict[CopicColorCode, list[tuple]]) -> Collection:
    """
    creates a layered collection with 8 pens per layer
    sorts the layers by color group, in order to avoid chaos when loading up the pens
    first all blues, then greens, all reds, all RV etc etc
    """
    all_paths = Collection()
    for color, coordinates in color_coords.items():
        for coordinate in coordinates:
            pixel = Path.from_tuple_list([(coordinate[0], coordinate[1]), (coordinate[0], coordinate[1])])
            pixel.properties["copic_color"] = Copic().color_by_code(color)
            all_paths.add(pixel)

    return sort_collection_by_copic_color_group(all_paths)


def sort_collection_by_copic_color(collection: Collection) -> dict[Color, Collection]:
    colors: dict[Color, Collection] = {}
    for path in collection:
        path_color = path.properties["copic_color"]
        if path_color not in colors.keys():
            colors[path_color] = Collection()
        colors[path_color].add(path)

    return dict(sorted(colors.items()))


def sort_collection_by_copic_color_group(collection: Collection) -> Collection:
    """
    the coordinates of the paths are in pixel space, not in hpgl/plotter space
    """
    out_color_names_pen_mapping = {}
    color_names_pen_mapping = {}

    c = Collection()

    pen_index = 1
    layer_index = 0
    groups = {}

    add_legende = True

    # separating app paths into the copic color groups
    for path in collection:
        path_copic_color = path.properties["copic_color"]
        if path_copic_color.group not in groups.keys():
            groups[path_copic_color.group] = Collection()

        groups[path_copic_color.group].add(path)

    for group, paths in groups.items():
        sorted_by_colors = sort_collection_by_copic_color(paths)

        for path_color, paths_same_color in sorted_by_colors.items():
            color_names_pen_mapping[pen_index] = path_color.code

            if add_legende:
                # here add a single point at 0,0 with that color and pen number
                x = layer_index * 2
                y = pen_index * 2
                legend_path = Path(
                    [Position(x, y), Position(x, y)])
                legend_path.layer = layer_index
                legend_path.pen_select = pen_index
                legend_path.color = path_color.as_rgb()
                c.add(legend_path)

            for path in paths_same_color:
                path.pen_select = pen_index
                path.layer = layer_index
                path.color = path_color.as_rgb()

                c.add(path)

            pen_index += 1

            if pen_index == 9:
                out_color_names_pen_mapping[layer_index] = color_names_pen_mapping.copy()
                color_names_pen_mapping = {}
                pen_index = 1
                layer_index += 1

        # out_color_names_pen_mapping[layer_index] = color_names_pen_mapping.copy()
        # layer_index += 1
        # pen_index = 1

    out_color_names_pen_mapping[layer_index] = color_names_pen_mapping.copy()

    c.properties["pen_mapping"] = out_color_names_pen_mapping

    return c


if __name__ == "__main__":
    collection = Collection()

    p1 = Path([Position(0, 0), Position(1, 1)], {"copic_color": Copic().color_by_code(CopicColorCode.B0000)})
    p2 = Path([Position(0, 0), Position(1, 1)], {"copic_color": Copic().color_by_code(CopicColorCode.B000)})
    p3_2 = Path([Position(0, 0), Position(1, 1)], {"copic_color": Copic().color_by_code(CopicColorCode.R01)})
    p3 = Path([Position(0, 0), Position(1, 1)], {"copic_color": Copic().color_by_code(CopicColorCode.B99)})
    p4 = Path([Position(0, 0), Position(1, 1)], {"copic_color": Copic().color_by_code(CopicColorCode.B39)})
    p5 = Path([Position(0, 0), Position(1, 1)], {"copic_color": Copic().color_by_code(CopicColorCode.B12)})
    p5_2 = Path([Position(0, 0), Position(1, 1)], {"copic_color": Copic().color_by_code(CopicColorCode.R08)})

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
