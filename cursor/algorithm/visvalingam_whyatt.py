from cursor.path import Path
from cursor.position import Position


def triangle_area(p1: Position, p2: Position, p3: Position) -> float:
    """Calculate the area of a triangle formed by three points."""
    return abs((p2.x - p1.x) * (p3.y - p1.y) - (p3.x - p1.x) * (p2.y - p1.y)) / 2


class VisvalingamWhyatt:
    def __init__(self):
        self.points: Path = Path()
        self.areas: dict[int, float] = {}
        self.removed: set[int] = set()

    def _calculate_effective_area(self, idx: int) -> float:
        """Calculate the effective area for a point at given index."""
        if idx <= 0 or idx >= len(self.points) - 1:
            return float("inf")

        return triangle_area(self.points[idx - 1], self.points[idx], self.points[idx + 1])

    def _initialize_areas(self):
        """Initialize areas for all points."""
        self.areas = {}
        self.removed = set()

        # Calculate initial areas for all points
        for i in range(1, len(self.points) - 1):
            self.areas[i] = self._calculate_effective_area(i)

    def simplify(self, points: Path, threshold: float = 0) -> Path:
        """
        Simplify a polyline using the Visvalingam-Whyatt algorithm.

        Args:
            points: List of Position objects
            threshold: Minimum effective area to retain a point

        Returns:
            List of simplified Position objects
        """
        if len(points) <= 2:
            return points.copy()

        self.points = points.copy()
        self._initialize_areas()

        # Remove points with area <= threshold
        while True:
            # Find point with smallest area
            min_area = float("inf")
            min_idx = -1

            for idx, area in self.areas.items():
                if idx not in self.removed and area < min_area:
                    min_area = area
                    min_idx = idx

            # If no more points to remove or smallest area > threshold, stop
            if min_idx == -1 or min_area > threshold:
                break

            # If we would have less than 3 points and this isn't a high threshold, stop
            if len(points) - len(self.removed) <= 3 and threshold <= 1.0:
                break

            # Remove the point
            self.removed.add(min_idx)

            # Update areas of adjacent points
            for adj_idx in [min_idx - 1, min_idx + 1]:
                if 0 < adj_idx < len(self.points) - 1:
                    if adj_idx not in self.removed:
                        self.areas[adj_idx] = self._calculate_effective_area(adj_idx)

        # Return points that weren't removed, maintaining order
        result = [p for i, p in enumerate(self.points) if i not in self.removed]

        # Special case: if threshold > 1.0, only keep endpoints
        if threshold > 1.0:
            return Path.from_list([result[0], result[-1]])

        return Path.from_list(result)


def simplify_vw(points: Path, threshold: float = 0) -> Path:
    """
    Convenience function to simplify a polyline using Position objects.

    Args:
        points: List of Position objects
        threshold: Minimum effective area to retain a point

    Returns:
        List of simplified Position objects
    """
    vw = VisvalingamWhyatt()
    return vw.simplify(points, threshold)
