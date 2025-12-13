import numpy as np
from sklearn.neighbors import KDTree as SKLearnKDTree


class KDTree:
    """
    A wrapper around sklearn's KDTree implementation with the same interface as kd.py.
    This implementation is highly optimized and can handle millions of points efficiently.
    """

    def __init__(self, points, dim, dist_sq_func=None):
        """Makes the KD-Tree for fast lookup using sklearn's implementation.

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
            This parameter is accepted for compatibility but ignored
            (sklearn always uses Euclidean distance).
        """
        self.dim = dim
        self._points = []
        self._properties = []

        # Convert points to (point, properties) pairs if they aren't already
        for p in points:
            if isinstance(p, tuple) and len(p) == 2:
                # Check if it's a (point, properties) pair
                if isinstance(p[1], dict) or p[1] is None:
                    point, props = p
                    self._points.append(point)
                    self._properties.append(props)
                else:
                    # It's just a point tuple
                    self._points.append(p)
                    self._properties.append(None)
            else:
                # It's just a point, add None as properties
                self._points.append(p)
                self._properties.append(None)

        # Build the sklearn KDTree
        if self._points:
            self._points_array = np.array(self._points, dtype=np.float64)
            self._tree = SKLearnKDTree(self._points_array, leaf_size=30)
        else:
            self._points_array = np.empty((0, dim), dtype=np.float64)
            self._tree = None

    def __iter__(self):
        """Iterate over all (point, properties) pairs in the tree."""
        for point, props in zip(self._points, self._properties):
            yield (point, props)

    def add_point(self, point, properties=None):
        """Adds a point with optional properties to the kd-tree.

        Note: Adding points one at a time is inefficient with sklearn's KDTree
        as it requires rebuilding the entire tree. For best performance,
        initialize with all points at once.

        Parameters
        ----------
        point : array-like
            The point.
        properties : any, optional
            Properties associated with the point.
        """
        # Add to our lists
        self._points.append(point)
        self._properties.append(properties)

        # Rebuild the tree
        self._points_array = np.array(self._points, dtype=np.float64)
        self._tree = SKLearnKDTree(self._points_array, leaf_size=30)

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
        if self._tree is None or len(self._points) == 0:
            return []

        # Ensure point is a numpy array with correct shape
        query_point = np.array(point, dtype=np.float64).reshape(1, -1)

        # Query the tree (sklearn returns distances, not squared distances)
        k_actual = min(k, len(self._points))
        distances, indices = self._tree.query(query_point, k=k_actual)

        # Flatten the results (sklearn returns 2D arrays)
        distances = distances[0]
        indices = indices[0]

        # Build result list
        results = []
        for dist, idx in zip(distances, indices):
            point_props = (self._points[idx], self._properties[idx])
            if return_dist_sq:
                # Square the distance since sklearn returns Euclidean distance
                results.append((dist**2, point_props))
            else:
                results.append(point_props)

        return results

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
        results = self.get_knn(point, 1, return_dist_sq)
        return results[0] if results else None

    def size(self):
        """Return the number of points in the tree.

        Returns
        -------
        int
            The number of points stored in the tree.
        """
        return len(self._points)

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
        point_array = np.array(point, dtype=np.float64)

        # Find exact matches
        for i, stored_point in enumerate(self._points):
            stored_array = np.array(stored_point, dtype=np.float64)
            if np.allclose(stored_array, point_array, rtol=1e-9, atol=1e-9):
                self._properties[i] = new_properties
                return True

        return False


# Example usage and testing
if __name__ == "__main__":
    import time

    # Test basic functionality
    print("Testing basic functionality...")
    points = [
        ((1.0, 2.0), {"color": "red"}),
        ((3.0, 4.0), {"color": "blue"}),
        ((5.0, 1.0), {"color": "green"}),
        ((2.0, 3.0), {"color": "yellow"}),
    ]

    tree = KDTree(points, dim=2)

    # Test get_nearest with distance
    query = (2.5, 3.5)
    result = tree.get_nearest(query, return_dist_sq=True)
    if result:
        dist_sq, (point, props) = result
        print(f"Nearest to {query}: {point}, properties: {props}, dist�: {dist_sq}")

    # Test get_knn
    k_results = tree.get_knn(query, k=3, return_dist_sq=True)
    print(f"\n3 nearest neighbors to {query}:")
    for dist_sq, (point, props) in k_results:
        print(f"  {point}, properties: {props}, dist�: {dist_sq}")

    # Test add_point
    tree.add_point((0.0, 0.0), {"color": "black"})
    result = tree.get_nearest((0.1, 0.1), return_dist_sq=True)
    if result:
        dist_sq, (point, props) = result
        print(f"\nNearest to (0.1, 0.1) after adding (0, 0): {point}, {props}")

    # Test update_properties
    success = tree.update_properties((1.0, 2.0), {"color": "red", "updated": True})
    print(f"\nUpdate properties: {success}")

    # Test iteration
    print("\nAll points in tree:")
    for point, props in tree:
        print(f"  {point}: {props}")

    # Performance test with larger dataset
    print("\n" + "=" * 50)
    print("Performance test with 100,000 points...")
    n_points = 100000
    large_points = [(np.random.rand(2).tolist(), {"id": i}) for i in range(n_points)]

    start = time.time()
    large_tree = KDTree(large_points, dim=2)
    build_time = time.time() - start
    print(f"Build time: {build_time:.3f}s")

    # Query performance
    n_queries = 1000
    query_points = [np.random.rand(2).tolist() for _ in range(n_queries)]

    start = time.time()
    for qp in query_points:
        large_tree.get_nearest(qp)
    query_time = time.time() - start
    print(f"Time for {n_queries} nearest neighbor queries: {query_time:.3f}s")
    print(f"Average query time: {query_time / n_queries * 1000:.3f}ms")

    # KNN queries
    start = time.time()
    for qp in query_points[:100]:
        large_tree.get_knn(qp, k=10)
    knn_time = time.time() - start
    print(f"Time for 100 k=10 queries: {knn_time:.3f}s")
    print(f"Average k-NN query time: {knn_time / 100 * 1000:.3f}ms")
