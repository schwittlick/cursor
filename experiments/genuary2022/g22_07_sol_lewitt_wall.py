from cursor import path

from shapely.geometry import MultiLineString, box, Point
from shapely.affinity import rotate
from shapely import speedups
from math import sqrt


def hatchbox(rect, angle, spacing):
    """
    returns a Shapely geometry (MULTILINESTRING, or more rarely,
    GEOMETRYCOLLECTION) for a simple hatched rectangle.
    args:
    rect - a Shapely geometry for the outer boundary of the hatch
           Likely most useful if it really is a rectangle
    angle - angle of hatch lines, conventional anticlockwise -ve
    spacing - spacing between hatch lines
    GEOMETRYCOLLECTION case occurs when a hatch line intersects with
    the corner of the clipping rectangle, which produces a point
    along with the usual lines.
    """

    (llx, lly, urx, ury) = rect.bounds
    centre_x = (urx + llx) / 2
    centre_y = (ury + lly) / 2
    diagonal_length = sqrt((urx - llx) ** 2 + (ury - lly) ** 2)
    number_of_lines = 2 + int(diagonal_length / spacing)
    hatch_length = spacing * (number_of_lines - 1)
    coords = []
    for i in range(number_of_lines):
        if i % 2:
            coords.extend(
                [
                    (
                        (
                            centre_x - hatch_length / 2,
                            centre_y - hatch_length / 2 + i * spacing,
                        ),
                        (
                            centre_x + hatch_length / 2,
                            centre_y - hatch_length / 2 + i * spacing,
                        ),
                    )
                ]
            )
        else:
            coords.extend(
                [
                    (
                        (
                            centre_x + hatch_length / 2,
                            centre_y - hatch_length / 2 + i * spacing,
                        ),
                        (
                            centre_x - hatch_length / 2,
                            centre_y - hatch_length / 2 + i * spacing,
                        ),
                    )
                ]
            )
    lines = MultiLineString(coords)
    lines = rotate(lines, angle, origin="centroid", use_radians=False)
    return rect.intersection(lines)


#######################################################
# the two primitives that actually draw stuff


def plot_point(pt, pen):
    print("SP%d;PA%d,%d;PD;PU;" % (pen, int(pt.x), int(pt.y)))


def plot_linestring(line, pen):
    first = 1
    pts = []
    for (x, y) in line.coords:
        if first == 1:
            first = 0
            print("SP%d;PA%d,%d;PD;" % (pen, int(x), int(y)))
        pts.extend((int(x), int(y)))
    print("PA", ",".join(str(p) for p in pts), ";PU;")


#######################################################
# a polygon is just lines


def plot_polygon(poly, pen):
    plot_linestring(poly.exterior, pen)
    for i in poly.interiors:
        plot_linestring(i, pen)


#######################################################
# the multi* functions: just call each type multiple times


def plot_multipoint(multipt, pen):
    for i in multipt.geoms:
        plot_point(i, pen)


def plot_multilinestring(multi, pen):
    for i in multi.geoms:
        plot_linestring(i, pen)


def plot_multipolygon(multipoly, pen):
    for i in multipoly.geoms:
        plot_polygon(i, pen)


#######################################################
# this one gets a bit hairy with recursion


def plot_geomcollection(geomcollection, pen):
    for i in geomcollection.geoms:
        plot(i, pen)


#######################################################
# type-aware plotting function
# you'll probably call this most of all


def plot(obj, pen):
    gtype = obj.geom_type
    if gtype == "Point":
        plot_point(obj, pen)
    elif gtype == "LineString":
        plot_linestring(obj, pen)
    elif gtype == "LinearRing":
        # same as a linestring, but closed
        plot_linestring(obj, pen)
    elif gtype == "Polygon":
        plot_polygon(obj, pen)
    elif gtype == "Multipoint":
        plot_multipoint(obj, pen)
    elif gtype == "MultiLineString":
        plot_multilinestring(obj, pen)
    elif gtype == "MultiPolygon":
        plot_multipolygon(obj, pen)
    elif gtype == "GeomCollection":
        plot_geomcollection(obj, pen)
    else:
        print("*** Un-handled geometry:", gtype, ":", obj)
        exit(1)


#######################################################
# setup/cleanup


def init():

    # enable Shapely speedups, if possible

    if speedups.available:
        speedups.enable()
    print("IN;")


def trailer():
    print("PU;SP;")


if __name__ == "__main__":
    # recordings = data.DataDirHandler().recordings()
    # _loader = loader.Loader(directory=recordings, limit_files=1)
    # pc = _loader.all_paths()

    pc_final = path.PathCollection()

    for l in range(30):
        p = path.Path()
        p.add(0, 0)
        p.add(l, 30)

    for l in range(30):
        p = path.Path()
        p.add(30, 0)
        p.add(30, l)

    for l in range(30):
        p = path.Path()
        p.add(0, 0)
        p.add(l, 30)
