class KDTreeNode:
    def __init__(self, point, data, axis, left=None, right=None):
        self.point = point
        self.data = data
        self.axis = axis
        self.left = left
        self.right = right


class KDTree:
    def __init__(self, points=None, dimensions=2):
        """
        Initialize KDTree.

        Args:
            points: List of (point, data) tuples to initialize with
            dimensions: Number of dimensions (default 2 for 2D points)
        """
        self.dimensions = dimensions
        self.root = None

        if points:
            # Build tree from initial points
            point_data_pairs = [(p[0], p[1]) for p in points]
            self.root = self._build_tree(point_data_pairs, 0)

    def _build_tree(self, points, depth):
        """Recursively build the KD-tree."""
        if not points:
            return None

        axis = depth % self.dimensions

        # Sort points by the current axis
        points.sort(key=lambda x: x[0][axis])

        # Find median
        median_idx = len(points) // 2
        median_point, median_data = points[median_idx]

        # Create node and recursively build subtrees
        node = KDTreeNode(
            median_point,
            median_data,
            axis,
            self._build_tree(points[:median_idx], depth + 1),
            self._build_tree(points[median_idx + 1 :], depth + 1),
        )

        return node

    def add_point(self, point, data):
        """
        Add a point with associated data to the tree.

        Args:
            point: Tuple of coordinates (x, y)
            data: Associated data (dict or any object)
        """
        if self.root is None:
            self.root = KDTreeNode(point, data, 0)
        else:
            self._insert(self.root, point, data, 0)

    def _insert(self, node, point, data, depth):
        """Recursively insert a point into the tree."""
        axis = depth % self.dimensions

        if point[axis] < node.point[axis]:
            if node.left is None:
                node.left = KDTreeNode(point, data, axis)
            else:
                self._insert(node.left, point, data, depth + 1)
        else:
            if node.right is None:
                node.right = KDTreeNode(point, data, axis)
            else:
                self._insert(node.right, point, data, depth + 1)

    def get_nearest(self, query_point, return_distance=False):
        """
        Find the nearest neighbor to the query point.

        Args:
            query_point: Tuple of coordinates to search near
            return_distance: If True, return (distance_squared, (point, data))
                           If False, return (point, data)

        Returns:
            If return_distance=True: (distance_squared, (nearest_point, data))
            If return_distance=False: (nearest_point, data)
        """
        if self.root is None:
            return None

        best = [None, float("inf")]  # [node, distance_squared]
        self._nearest_search(self.root, query_point, 0, best)

        if best[0] is None:
            return None

        result = (best[0].point, best[0].data)

        if return_distance:
            return (best[1], result)
        else:
            return result

    def _nearest_search(self, node, query_point, depth, best):
        """Recursively search for the nearest neighbor."""
        if node is None:
            return

        # Calculate squared distance to current node
        dist_squared = sum((a - b) ** 2 for a, b in zip(query_point, node.point))

        # Update best if this node is closer
        if dist_squared < best[1]:
            best[0] = node
            best[1] = dist_squared

        axis = depth % self.dimensions
        diff = query_point[axis] - node.point[axis]

        # Choose which side to search first
        if diff < 0:
            self._nearest_search(node.left, query_point, depth + 1, best)
            # Check if we need to search the other side
            if diff * diff < best[1]:
                self._nearest_search(node.right, query_point, depth + 1, best)
        else:
            self._nearest_search(node.right, query_point, depth + 1, best)
            # Check if we need to search the other side
            if diff * diff < best[1]:
                self._nearest_search(node.left, query_point, depth + 1, best)

    def size(self):
        """Return the number of points in the tree."""
        return self._count_nodes(self.root)

    def _count_nodes(self, node):
        """Recursively count nodes in the tree."""
        if node is None:
            return 0
        return 1 + self._count_nodes(node.left) + self._count_nodes(node.right)

    def is_empty(self):
        """Check if the tree is empty."""
        return self.root is None


# Example usage and testing
if __name__ == "__main__":
    # Test the implementation
    kd_tree = KDTree([], 2)

    # Add some points
    kd_tree.add_point((1.0, 2.0), {"color": "red", "value": 10})
    kd_tree.add_point((3.0, 4.0), {"color": "blue", "value": 20})
    kd_tree.add_point((5.0, 1.0), {"color": "green", "value": 30})

    # Find nearest neighbor
    nearest = kd_tree.get_nearest((2.0, 3.0), True)
    if nearest:
        dist_squared, (point, data) = nearest
        print(f"Nearest point: {point}, Data: {data}, Distance²: {dist_squared}")

    # Test with initial points
    initial_points = [
        ((0.0, 0.0), {"id": 1}),
        ((1.0, 1.0), {"id": 2}),
        ((2.0, 0.0), {"id": 3}),
    ]
    kd_tree2 = KDTree(initial_points, 2)

    nearest2 = kd_tree2.get_nearest((0.5, 0.5), False)
    if nearest2:
        point, data = nearest2
        print(f"Nearest to (0.5, 0.5): {point}, Data: {data}")
