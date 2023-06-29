import numpy as np

from cursor.collection import Collection
from cursor.path import Path


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
