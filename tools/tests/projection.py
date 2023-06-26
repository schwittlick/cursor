import arcade
import numpy as np
from HersheyFonts import HersheyFonts

from cursor import misc
from cursor.collection import Collection
from cursor.path import Path
from cursor.renderer import RealtimeRenderer
from cursor.timer import Timer
from tools.spline_experiment import transform_path


def project_point_to_plane(point, plane_point, plane_normal):
    plane_normal = plane_normal / np.linalg.norm(plane_normal)  # Normalize the plane normal vector
    v = point - plane_point  # Vector from point on plane to point
    d = np.dot(v, plane_normal)  # Project v onto plane normal to get distance
    projected_point = point - d * plane_normal  # Move point along normal vector
    return projected_point


def compute_2d_coordinates(point_3d, basis1, basis2):
    coord1 = np.dot(point_3d, basis1) / np.linalg.norm(basis1)
    coord2 = np.dot(point_3d, basis2) / np.linalg.norm(basis2)
    return np.array([coord1, coord2])


def project(point_list: list[list[list[float]]], plane_point: np.array = np.array([0, 0, 0]),
            plane_normal: np.array = np.array([0, 0, 1]), basis1: np.array = np.array([1, 0, 0]),
            basis2: np.array = np.array([0, 1, 0])):
    c = Collection()

    for line in point_list:
        p = Path()
        points = np.array(line)

        for point in points:
            projected_point = project_point_to_plane(point, plane_point, plane_normal)

            projected_point_2d = compute_2d_coordinates(projected_point, basis1, basis2)
            p.add(projected_point_2d[0], projected_point_2d[1])
        c.add(p)

    return c


def on_mouse(rr: RealtimeRenderer, x, y, dx, dy):
    print(rr)
    print(x, y, dx, dy)

    v1 = misc.map(x, 0, rr.width, -5, 5)
    v2 = misc.map(y, 0, rr.height, -5, 5)

    basis1 = np.array([1, 0, 0])
    basis2 = np.array([0, 1, 0])

    plane_point = np.array([0, 0, 0])
    plane_normal = np.array([v1, v2, 1])

    c = project(temp_points, plane_point, plane_normal, basis1, basis2)

    c_final = Collection()

    bb = c.bb()
    for p in c:
        c_final.add(transform_path(p, bb, ((0, 0), (400, 400))))
    rr.clear_list()
    rr.add_collection(c_final, line_width=2, color=arcade.color.GRAY)


if __name__ == "__main__":
    temp_points = []
    thefont = HersheyFonts()
    thefont.load_default_font()
    thefont.normalize_rendering(100)
    for (x1, y1), (x2, y2) in thefont.lines_for_text('III...III'):
        temp_points.append([[x1, -y1, 0], [x2, -y2, 0]])

    plane_point = np.array([0, 0, 0])
    plane_normal = np.array([0, 0, 1])

    # Choose basis vectors for the plane (they should be orthogonal)
    basis1 = np.array([1, 0, 0])
    basis2 = np.array([0, 1, 0])

    timer = Timer()
    c = project(temp_points, plane_point, plane_normal, basis1, basis2)

    c_final = Collection()

    bb = c.bb()
    for p in c:
        c_final.add(transform_path(p, bb, ((0, 0), (400, 400))))

    timer.print_elapsed("this took ")

    rr = RealtimeRenderer(400, 400, "projection")
    rr.set_bg_color(arcade.color.WHITE)
    rr.add_collection(c_final, line_width=2, color=arcade.color.GRAY)
    rr.set_on_mouse_cb(on_mouse)

    rr.run()
