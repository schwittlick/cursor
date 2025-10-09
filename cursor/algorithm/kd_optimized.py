import heapq


class KDNode:
    """Node for optimized KD-Tree."""

    __slots__ = ["point", "properties", "left", "right", "axis"]

    def __init__(self, point, properties=None, axis=0):
        self.point = point
        self.properties = properties
        self.left = None
        self.right = None
        self.axis = axis


class OptimizedKDTree:
    """
    Optimized KD-Tree implementation with better performance characteristics.

    Improvements over the original:
    - Uses explicit node objects instead of lists for better memory layout
    - Iterative search where possible to reduce function call overhead
    - Optimized distance calculations
    - Better heap management for k-NN queries
    """

    def __init__(self, points, dim, dist_sq_func=None):
        """Makes the optimized KD-Tree for fast lookup.

        Parameters
        ----------
        points : list<point> or list<(point, properties)>
            A list of points or (point, properties) pairs.
        dim : int
            The dimension of the points.
        dist_sq_func : function(point, point), optional
            A function that returns the squared Euclidean distance.
        """
        self.dim = dim

        if dist_sq_func is None:
            self.dist_sq_func = self._default_dist_sq
        else:
            self.dist_sq_func = dist_sq_func

        # Process points to ensure consistent format
        processed_points = []
        for p in points:
            if isinstance(p, tuple) and len(p) == 2:
                if isinstance(p[1], dict):
                    processed_points.append(p)
                else:
                    processed_points.append((p, None))
            else:
                processed_points.append((p, None))

        self.root = self._build_tree(processed_points, 0)

    def _default_dist_sq(self, a, b):
        """Optimized default squared distance function."""
        return sum((a[i] - b[i]) ** 2 for i in range(len(a)))

    def _build_tree(self, points, depth):
        """Build the KD-Tree recursively."""
        if not points:
            return None

        axis = depth % self.dim

        # Sort points by the current axis
        points.sort(key=lambda x: x[0][axis])

        # Find median
        median_idx = len(points) // 2
        median_point, median_props = points[median_idx]

        # Create node
        node = KDNode(median_point, median_props, axis)

        # Recursively build left and right subtrees
        node.left = self._build_tree(points[:median_idx], depth + 1)
        node.right = self._build_tree(points[median_idx + 1 :], depth + 1)

        return node

    def add_point(self, point, properties=None):
        """Add a point to the tree."""
        if self.root is None:
            self.root = KDNode(point, properties, 0)
        else:
            self._add_point_iterative(point, properties)

    def _add_point_iterative(self, point, properties):
        """Add a point using iterative approach."""
        current = self.root
        depth = 0

        while True:
            axis = depth % self.dim

            if point[axis] < current.point[axis]:
                if current.left is None:
                    current.left = KDNode(point, properties, axis)
                    break
                current = current.left
            else:
                if current.right is None:
                    current.right = KDNode(point, properties, axis)
                    break
                current = current.right

            depth += 1

    def get_nearest(self, point, return_dist_sq=True):
        """Get the nearest neighbor."""
        if self.root is None:
            return None

        result = self._nearest_neighbor_search(point)

        if result is None:
            return None

        best_node, best_dist_sq = result

        if return_dist_sq:
            return (best_dist_sq, (best_node.point, best_node.properties))
        else:
            return (best_node.point, best_node.properties)

    def _nearest_neighbor_search(self, target):
        """Optimized nearest neighbor search using recursive approach."""
        if self.root is None:
            return None

        best_node = None
        best_dist_sq = float("inf")

        def search_recursive(node, depth):
            nonlocal best_node, best_dist_sq

            if node is None:
                return

            # Calculate distance to current node
            dist_sq = self.dist_sq_func(target, node.point)

            # Update best if this is closer
            if dist_sq < best_dist_sq:
                best_dist_sq = dist_sq
                best_node = node

            # Determine which side to search first
            axis = depth % self.dim
            diff = target[axis] - node.point[axis]

            # Search strategy similar to original implementation
            if diff < 0:
                # Target is on the left side
                search_recursive(node.left, depth + 1)
                # Search right side if it could contain a closer point
                if diff * diff < best_dist_sq:
                    search_recursive(node.right, depth + 1)
            else:
                # Target is on the right side
                search_recursive(node.right, depth + 1)
                # Search left side if it could contain a closer point
                if diff * diff < best_dist_sq:
                    search_recursive(node.left, depth + 1)

        search_recursive(self.root, 0)
        return best_node, best_dist_sq

    def get_knn(self, point, k, return_dist_sq=True):
        """Get k nearest neighbors using optimized heap-based search."""
        if self.root is None:
            return []

        # Use a max heap (negate distances for min behavior)
        heap = []

        self._knn_search(self.root, point, k, heap, 0)

        # Convert heap to sorted list
        result = []
        while heap:
            neg_dist_sq, _, node = heapq.heappop(heap)
            dist_sq = -neg_dist_sq

            if return_dist_sq:
                result.append((dist_sq, (node.point, node.properties)))
            else:
                result.append((node.point, node.properties))

        return result[::-1]  # Reverse to get closest first

    def _knn_search(self, node, target, k, heap, depth):
        """Recursive k-NN search with pruning."""
        if node is None:
            return

        # Calculate distance to current node
        dist_sq = self.dist_sq_func(target, node.point)

        # Add to heap if we have space or if this is closer than the farthest
        if len(heap) < k:
            heapq.heappush(heap, (-dist_sq, id(node), node))
        elif dist_sq < -heap[0][0]:
            heapq.heappushpop(heap, (-dist_sq, id(node), node))

        # Determine search order
        axis = depth % self.dim
        diff = target[axis] - node.point[axis]

        if diff <= 0:
            near_side = node.left
            far_side = node.right
        else:
            near_side = node.right
            far_side = node.left

        # Search near side first
        self._knn_search(near_side, target, k, heap, depth + 1)

        # Search far side only if necessary
        if len(heap) < k or diff * diff < -heap[0][0]:
            self._knn_search(far_side, target, k, heap, depth + 1)

    def update_properties(self, point, new_properties):
        """Update properties of a point in the tree."""
        node = self._find_node(point)
        if node is not None:
            node.properties = new_properties
            return True
        return False

    def _find_node(self, target):
        """Find a node with the given point."""
        current = self.root
        depth = 0

        while current is not None:
            # Check if this is the target point
            if all(current.point[i] == target[i] for i in range(self.dim)):
                return current

            # Navigate to next node
            axis = depth % self.dim
            if target[axis] < current.point[axis]:
                current = current.left
            else:
                current = current.right

            depth += 1

        return None

    def __iter__(self):
        """Iterate over all points in the tree."""
        return self._walk(self.root)

    def _walk(self, node):
        """Walk the tree in-order."""
        if node is not None:
            yield from self._walk(node.left)
            yield (node.point, node.properties)
            yield from self._walk(node.right)
