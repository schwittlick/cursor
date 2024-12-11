from typing import List, Set, Tuple, TypeAlias, Dict
import numpy as np
from scipy.ndimage import label, generate_binary_structure
from collections import deque

# Type aliases for clarity
Point: TypeAlias = Tuple[int, int]
Path: TypeAlias = List[Point]
Paths: TypeAlias = List[Path]


def preprocess_image(img: np.ndarray) -> np.ndarray:
    """
    Preprocess the image to ensure it's binary with white lines (1) on black background (0).
    """
    # Handle different dtypes
    if img.dtype in [np.float64, np.float32]:
        binary = (img > 0.5).astype(np.uint8)
    elif img.dtype == np.uint8:
        binary = (img > 128).astype(np.uint8)
    elif img.dtype in [np.int64, np.int32, np.int16, np.int8]:
        binary = (img > 0).astype(np.uint8)
    else:
        raise ValueError(f"Unexpected image dtype: {img.dtype}")

    return binary


def get_pixel_neighbors(img: np.ndarray, point: Point) -> List[Point]:
    """
    Get all 8-connected neighbors of a pixel that are part of the skeleton.
    """
    y, x = point
    neighbors: List[Point] = []

    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dy == 0 and dx == 0:
                continue

            ny, nx = y + dy, x + dx
            if (0 <= ny < img.shape[0] and
                    0 <= nx < img.shape[1] and
                    img[ny, nx]):
                neighbors.append((int(ny), int(nx)))

    return neighbors


def count_neighbors(img: np.ndarray, point: Point) -> int:
    """
    Count the number of 8-connected neighbors of a pixel.
    """
    return len(get_pixel_neighbors(img, point))


def find_special_points(skel: np.ndarray) -> Tuple[List[Point], List[Point]]:
    """
    Find endpoints (1 neighbor) and junctions (3+ neighbors) in the skeleton.
    """
    endpoints: List[Point] = []
    junctions: List[Point] = []

    # Iterate through all white pixels
    white_points = np.column_stack(np.where(skel > 0))

    for y, x in white_points:
        point = (int(y), int(x))
        neighbor_count = count_neighbors(skel, point)

        if neighbor_count == 1:
            endpoints.append(point)
        elif neighbor_count >= 3:
            junctions.append(point)

    return endpoints, junctions


def trace_path(skel: np.ndarray, start: Point, visited: Set[Point],
               allow_junction_to_junction: bool = True) -> Path:
    """
    Trace a path from start point until hitting endpoint or junction.
    """
    path = [start]
    current = start
    visited.add(start)
    is_start_junction = count_neighbors(skel, start) >= 3

    while True:
        neighbors = [n for n in get_pixel_neighbors(skel, current)
                     if n not in visited]

        if not neighbors:
            break

        neighbor_counts = [count_neighbors(skel, n) for n in neighbors]

        # If we're at a junction point
        if len(neighbors) > 1:
            # Choose the neighbor that continues the most similar direction
            if len(path) >= 2:
                prev_dir = (path[-1][0] - path[-2][0], path[-1][1] - path[-2][1])
                best_dir_diff = float('inf')
                best_neighbor = neighbors[0]

                for n in neighbors:
                    new_dir = (n[0] - path[-1][0], n[1] - path[-1][1])
                    dir_diff = abs(np.arctan2(new_dir[0], new_dir[1]) -
                                   np.arctan2(prev_dir[0], prev_dir[1]))
                    if dir_diff < best_dir_diff:
                        best_dir_diff = dir_diff
                        best_neighbor = n

                current = best_neighbor
            else:
                current = neighbors[0]
        else:
            current = neighbors[0]

        # Check if we've hit a junction
        is_junction = count_neighbors(skel, current) >= 3
        if is_junction and not is_start_junction and not allow_junction_to_junction:
            break

        path.append(current)
        visited.add(current)

    return path

def should_connect_paths(skel: np.ndarray, path1: Path, path2: Path, max_distance: int = 2) -> bool:
    """
    Check if two paths should be connected based on the original skeleton.

    Args:
        skel: Original skeleton image
        path1: First path
        path2: Second path
        max_distance: Maximum Manhattan distance to check for connections
    """
    # Check all endpoint combinations
    endpoints1 = [path1[0], path1[-1]]
    endpoints2 = [path2[0], path2[-1]]

    for p1 in endpoints1:
        for p2 in endpoints2:
            # Check if endpoints are close enough
            if abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) <= max_distance:
                # Verify connection in original skeleton
                y_min = max(0, min(p1[0], p2[0]) - 1)
                y_max = min(skel.shape[0], max(p1[0], p2[0]) + 2)
                x_min = max(0, min(p1[1], p2[1]) - 1)
                x_max = min(skel.shape[1], max(p1[1], p2[1]) + 2)

                # Check if there's a connecting pixel in the neighborhood
                neighborhood = skel[y_min:y_max, x_min:x_max]
                if np.any(neighborhood):
                    return True
    return False

def connect_paths(paths: Paths, skel: np.ndarray) -> Paths:
    """
    Connect paths that are connected in the original skeleton.
    """
    result_paths = paths.copy()

    # Find all path connections
    connections = []
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            if should_connect_paths(skel, paths[i], paths[j]):
                connections.append((i, j))

    # Create new connected paths
    for i, j in connections:
        path1, path2 = paths[i], paths[j]

        # Find closest endpoints
        endpoints1 = [path1[0], path1[-1]]
        endpoints2 = [path2[0], path2[-1]]
        min_dist = float('inf')
        best_endpoints = None

        for p1 in endpoints1:
            for p2 in endpoints2:
                dist = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
                if dist < min_dist:
                    min_dist = dist
                    best_endpoints = (p1, p2)

        if best_endpoints:
            # Create new path connecting the endpoints
            new_path = []

            # Choose correct path orientation
            if best_endpoints[0] == path1[0]:
                new_path.extend(reversed(path1))
            else:
                new_path.extend(path1)

            if best_endpoints[1] == path2[-1]:
                new_path.extend(reversed(path2))
            else:
                new_path.extend(path2)

            result_paths.append(new_path)

    return result_paths


def skeleton_to_vectors(img: np.ndarray,
                        min_path_length: int = 2,
                        allow_junction_to_junction: bool = True,
                        connect_paths_flag: bool = True) -> Paths:
    """
    Convert skeletonized image to vector paths.

    Args:
        img: 2D numpy array representing the skeletonized image
        min_path_length: Minimum number of points required for a valid path
        allow_junction_to_junction: If True, allows paths between junctions
        connect_paths_flag: If True, attempts to connect paths that are connected in the skeleton

    Returns:
        List of paths, where each path is a list of (y, x) coordinate tuples
    """
    # Preprocess the image
    skel = preprocess_image(img)

    # Find all endpoints and junctions
    endpoints, junctions = find_special_points(skel)

    # Start points are endpoints and junctions
    start_points = endpoints + junctions

    # Keep track of visited pixels
    visited: Set[Point] = set()

    # Store all paths
    paths: Paths = []

    # First trace paths from endpoints
    for start in endpoints:
        if start not in visited:
            path = trace_path(skel, start, visited, allow_junction_to_junction)
            if len(path) >= min_path_length:
                paths.append(path)

    # Then trace remaining paths from junctions
    for start in junctions:
        # Get unvisited neighbors of the junction
        neighbors = [n for n in get_pixel_neighbors(skel, start)
                     if n not in visited]

        for neighbor in neighbors:
            if neighbor not in visited:
                # Start the path from the junction
                path = trace_path(skel, start, visited, allow_junction_to_junction)
                if len(path) >= min_path_length:
                    paths.append(path)

    # Check for any unvisited pixels that might form closed loops
    remaining = np.column_stack(np.where(skel > 0))
    for y, x in remaining:
        point = (int(y), int(x))
        if point not in visited:
            path = trace_path(skel, point, visited, True)
            if len(path) >= min_path_length:
                paths.append(path)

    # Connect paths if requested
    if connect_paths_flag:
        paths = connect_paths(paths, skel)

    return paths


# Example usage:
"""
import numpy as np
from skimage import io

# Load image (white lines on black background)
img = io.imread('skeleton.png', as_gray=True)

# Convert to vectors
paths = skeleton_to_vectors(img, min_path_length=2, allow_junction_to_junction=True)

# Optionally visualize the paths
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 10))
plt.imshow(img, cmap='gray')
for path in paths:
    path_array = np.array(path)
    plt.plot(path_array[:, 1], path_array[:, 0], 'r-', linewidth=1)
plt.axis('equal')
plt.show()
"""
