import heapq


class KDTree:
    """
    A super short KD-Tree for points...
    The points can be any array-like type, e.g:
        lists, tuples, numpy arrays.
    Points can have associated properties stored with them.
    """

    def __init__(self, points, dim, dist_sq_func=None):
        """Makes the KD-Tree for fast lookup.

        Parameters
        ----------
        points : list<point> or list<(point, properties)>
            A list of points or (point, properties) pairs.
            If only points are provided, properties will be set to None.
        dim : int
            The dimension of the points.
        dist_sq_func : function(point, point), optional
            A function that returns the squared Euclidean distance
            between the two points.
            If omitted, it uses the default implementation.
        """

        if dist_sq_func is None:
            def dist_sq_func(a, b):
                return sum((x - b[i]) ** 2
                           for i, x in enumerate(a))

        # Convert points to (point, properties) pairs if they aren't already
        processed_points = []
        for p in points:
            if isinstance(p, tuple) and len(p) == 2:
                # Assume it's already a (point, properties) pair
                if isinstance(p[1], dict):
                    processed_points.append(p)
                else:
                    processed_points.append((p, None))
            else:
                # It's just a point, add None as properties
                processed_points.append((p, None))

        def make(points, i=0):
            if len(points) > 1:
                points.sort(key=lambda x: x[0][i])  # Sort by the i-th coordinate of the point
                i = (i + 1) % dim
                m = len(points) >> 1
                return [make(points[:m], i), make(points[m + 1:], i),
                        points[m]]
            if len(points) == 1:
                return [None, None, points[0]]

        def add_point(node, point_props, i=0):
            point, _ = point_props
            if node is not None:
                dx = node[2][0][i] - point[i]  # Compare with the point part
                for j, c in ((0, dx >= 0), (1, dx < 0)):
                    if c and node[j] is None:
                        node[j] = [None, None, point_props]
                    elif c:
                        add_point(node[j], point_props, (i + 1) % dim)

        def get_knn(node, point, k, return_dist_sq, heap, i=0, tiebreaker=1):
            if node is not None:
                node_point = node[2][0]  # Extract the point part
                dist_sq = dist_sq_func(point, node_point)
                dx = node_point[i] - point[i]
                if len(heap) < k:
                    heapq.heappush(heap, (-dist_sq, tiebreaker, node[2]))
                elif dist_sq < -heap[0][0]:
                    heapq.heappushpop(heap, (-dist_sq, tiebreaker, node[2]))
                i = (i + 1) % dim
                # Goes into the left branch, then the right branch if needed
                for b in (dx < 0, dx >= 0)[:1 + (dx * dx < -heap[0][0])]:
                    get_knn(node[b], point, k, return_dist_sq,
                            heap, i, (tiebreaker << 1) | b)
            if tiebreaker == 1:
                if return_dist_sq:
                    return [(-h[0], h[2]) for h in sorted(heap)][::-1]
                else:
                    return [h[2] for h in sorted(heap)][::-1]

        def walk(node):
            if node is not None:
                for j in 0, 1:
                    for x in walk(node[j]):
                        yield x
                yield node[2]

        self._add_point = add_point
        self._get_knn = get_knn
        self._root = make(processed_points)
        self._walk = walk
        self.dim = dim

    def __iter__(self):
        return self._walk(self._root)

    def add_point(self, point, properties=None):
        """Adds a point with optional properties to the kd-tree.

        Parameters
        ----------
        point : array-like
            The point.
        properties : any, optional
            Properties associated with the point.
        """
        point_props = (point, properties)
        if self._root is None:
            self._root = [None, None, point_props]
        else:
            self._add_point(self._root, point_props)

    def get_knn(self, point, k, return_dist_sq=True):
        """Returns k nearest neighbors.

        Parameters
        ----------
        point : array-like
            The point.
        k: int
            The number of nearest neighbors.
        return_dist_sq : boolean
            Whether to return the squared Euclidean distances.

        Returns
        -------
        list<(point, properties)> or list<(dist_sq, (point, properties))>
            The nearest neighbors with their properties.
            If `return_dist_sq` is true, the return will be:
                [(dist_sq, (point, properties)), ...]
            else:
                [(point, properties), ...]
        """
        return self._get_knn(self._root, point, k, return_dist_sq, [])

    def get_nearest(self, point, return_dist_sq=True):
        """Returns the nearest neighbor.

        Parameters
        ----------
        point : array-like
            The point.
        return_dist_sq : boolean
            Whether to return the squared Euclidean distance.

        Returns
        -------
        (point, properties) or (dist_sq, (point, properties))
            The nearest neighbor with its properties.
            If the tree is empty, returns `None`.
            If `return_dist_sq` is true, the return will be:
                (dist_sq, (point, properties))
            else:
                (point, properties)
        """
        l = self._get_knn(self._root, point, 1, return_dist_sq, [])
        return l[0] if len(l) else None

    def update_properties(self, point, new_properties):
        """Updates the properties of a point in the kd-tree.

        Parameters
        ----------
        point : array-like
            The point whose properties to update.
        new_properties : any
            The new properties to associate with the point.

        Returns
        -------
        boolean
            True if the point was found and its properties updated, False otherwise.
        """

        def update_recursive(node, point, new_properties, i=0):
            if node is None:
                return False

            node_point, node_props = node[2]

            # Check if this is the point we're looking for
            if all(node_point[j] == point[j] for j in range(self.dim)):
                # Update properties
                node[2] = (node_point, new_properties)
                return True

            # Continue searching
            dx = node_point[i] - point[i]
            next_i = (i + 1) % self.dim

            if dx >= 0:  # Point might be in left subtree
                if update_recursive(node[0], point, new_properties, next_i):
                    return True
            if dx <= 0:  # Point might be in right subtree
                if update_recursive(node[1], point, new_properties, next_i):
                    return True

            return False

        return update_recursive(self._root, point, new_properties)
