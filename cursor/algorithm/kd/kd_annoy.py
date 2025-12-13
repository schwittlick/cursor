import math

from annoy import AnnoyIndex


class KDTree:
    """
    A drop-in replacement for KDTree using Spotify's Annoy library.
    Annoy (Approximate Nearest Neighbors Oh Yeah) is a C++ library with Python bindings
    that provides fast approximate nearest neighbor queries, especially efficient for
    high-dimensional spaces and large datasets.

    This implementation maintains API compatibility with the existing KDTree class
    while leveraging Annoy's performance benefits for nearest neighbor search.
    """

    def __init__(self, points=None, dim=2, metric="euclidean", n_trees=10, n_jobs=16):
        """
        Initialize KDTree.

        Parameters
        ----------
        points : list<point> or list<(point, properties)>, optional
            A list of points or (point, properties) pairs.
            If only points are provided, properties will be set to None.
        dim : int
            The dimension of the points (default 2 for 2D points).
        metric : str
            Distance metric to use. Options: 'angular', 'euclidean', 'manhattan', 'hamming', 'dot'.
            Default is 'euclidean'.
        n_trees : int
            Number of trees to build. More trees give higher precision but use more memory.
            Default is 10.
        n_jobs : int
            Number of threads to use for building. Default is 1 (single-threaded).
            Set to -1 to use all available CPU cores.
        """
        self.dim = dim
        self.metric = metric
        self.n_trees = n_trees
        self.n_jobs = n_jobs
        self._index = AnnoyIndex(dim, metric)
        self._points_data = []  # Store (point, properties) pairs
        self._built = False
        self._next_id = 0

        # Process initial points if provided
        if points:
            processed_points = []
            for p in points:
                if isinstance(p, tuple) and len(p) == 2:
                    # Check if it's a (point, properties) pair
                    if isinstance(p[1], dict) or p[1] is None:
                        processed_points.append(p)
                    else:
                        # Treat entire tuple as a point
                        processed_points.append((p, None))
                else:
                    # It's just a point
                    processed_points.append((p, None))

            for point, properties in processed_points:
                self._add_point_internal(point, properties)

            # Build the index after adding all initial points
            # Annoy requires at least 2 items to build
            if self._next_id >= 2:
                try:
                    self._index.build(self.n_trees, n_jobs=self.n_jobs)
                except TypeError:
                    # Older Annoy versions don't support n_jobs parameter
                    self._index.build(self.n_trees)
                self._built = True
            elif self._next_id == 1:
                # With 1 point, mark as built but skip the build call
                self._built = True

    def _add_point_internal(self, point, properties):
        """Internal method to add a point without rebuilding the index."""
        point_tuple = tuple(point)  # Ensure point is hashable
        self._index.add_item(self._next_id, point)
        self._points_data.append((point_tuple, properties))
        self._next_id += 1

    def add_point(self, point, properties=None):
        """
        Add a point with optional properties to the tree.
        Note: Adding points after initialization requires rebuilding the index,
        which can be expensive for large datasets.

        Parameters
        ----------
        point : array-like
            The point coordinates (e.g., tuple, list, or numpy array).
        properties : any, optional
            Properties associated with the point (typically a dict).
        """
        # Mark index as needing rebuild
        self._built = False
        self._add_point_internal(point, properties)

    def _ensure_built(self):
        """Ensure the index is built before querying."""
        if not self._built and self._next_id > 0:
            # Annoy doesn't support rebuilding, so we need to create a new index
            try:
                import sys

                self._index = AnnoyIndex(self.dim, self.metric)

                # Re-add all points
                for idx, (point, _) in enumerate(self._points_data):
                    self._index.add_item(idx, point)

                # Annoy requires at least 2 items to build properly
                # With 1 item, we skip build and handle queries manually
                if len(self._points_data) >= 2:
                    # Try with n_jobs parameter, fall back to without if it fails
                    try:
                        self._index.build(self.n_trees, n_jobs=self.n_jobs)
                    except TypeError:
                        # Older Annoy versions don't support n_jobs parameter
                        print("DEBUG: n_jobs not supported, calling build without it", file=sys.stderr)
                        self._index.build(self.n_trees)

                # Reset _next_id to match the rebuilt index
                self._next_id = len(self._points_data)
                self._built = True
            except Exception as e:
                # Log the error instead of crashing silently
                import sys

                print(f"ERROR in _ensure_built: {e}", file=sys.stderr)
                print(f"Points count: {len(self._points_data)}, next_id: {self._next_id}", file=sys.stderr)
                import traceback

                traceback.print_exc()
                raise

    def get_nearest(self, point, return_dist_sq=False):
        """
        Find the nearest neighbor to the query point.

        Parameters
        ----------
        point : array-like
            The point coordinates to search near.
        return_dist_sq : bool
            If True, return (distance_squared, (point, data))
            If False, return (point, data)

        Returns
        -------
        (point, properties) or (dist_sq, (point, properties))
            The nearest neighbor with its properties.
            If the tree is empty, returns None.
            If return_dist_sq is True, returns (dist_sq, (point, properties))
        """
        if self._next_id == 0:
            return None

        self._ensure_built()

        # Special case: with only 1 point, return it directly
        if len(self._points_data) == 1:
            nearest_point, properties = self._points_data[0]
            if return_dist_sq:
                # Calculate distance manually
                dist_sq = sum((a - b) ** 2 for a, b in zip(point, nearest_point))
                return (dist_sq, (nearest_point, properties))
            else:
                return (nearest_point, properties)

        # Get 1 nearest neighbor
        indices, distances = self._index.get_nns_by_vector(point, 1, include_distances=True)

        if not indices:
            return None

        idx = indices[0]
        nearest_point, properties = self._points_data[idx]

        if return_dist_sq:
            # Annoy returns Euclidean distance, we need distance squared
            dist_sq = distances[0] ** 2
            return (dist_sq, (nearest_point, properties))
        else:
            return (nearest_point, properties)

    def get_knn(self, point, k, return_dist_sq=True):
        """
        Find k nearest neighbors to the query point.

        Parameters
        ----------
        point : array-like
            The point coordinates to search near.
        k : int
            The number of nearest neighbors to return.
        return_dist_sq : bool
            Whether to return squared Euclidean distances.

        Returns
        -------
        list<(point, properties)> or list<(dist_sq, (point, properties))>
            The k nearest neighbors with their properties.
            If return_dist_sq is True, returns [(dist_sq, (point, properties)), ...]
            Otherwise returns [(point, properties), ...]
        """
        if self._next_id == 0:
            return []

        self._ensure_built()

        # Limit k to the number of points we have
        k = min(k, self._next_id)

        # Special case: with only 1 point, return it directly
        if len(self._points_data) == 1:
            nearest_point, properties = self._points_data[0]
            if return_dist_sq:
                dist_sq = sum((a - b) ** 2 for a, b in zip(point, nearest_point))
                return [(dist_sq, (nearest_point, properties))]
            else:
                return [(nearest_point, properties)]

        # Get k nearest neighbors
        indices, distances = self._index.get_nns_by_vector(point, k, include_distances=True)

        results = []
        for idx, dist in zip(indices, distances):
            nearest_point, properties = self._points_data[idx]
            if return_dist_sq:
                dist_sq = dist**2
                results.append((dist_sq, (nearest_point, properties)))
            else:
                results.append((nearest_point, properties))

        return results

    def size(self):
        """Return the number of points in the tree."""
        return self._next_id

    def is_empty(self):
        """Check if the tree is empty."""
        return self._next_id == 0

    def __iter__(self):
        """Iterate over all (point, properties) pairs in the tree."""
        return iter(self._points_data)

    def save(self, filepath):
        """
        Save the Annoy index to disk.

        Parameters
        ----------
        filepath : str
            Path to save the index file.
        """
        self._ensure_built()
        self._index.save(filepath)

    def load(self, filepath):
        """
        Load a previously saved Annoy index from disk.
        Note: This only loads the index, not the properties data.
        You need to separately save/load _points_data if needed.

        Parameters
        ----------
        filepath : str
            Path to the saved index file.
        """
        self._index.load(filepath)
        self._built = True
        # Note: _next_id and _points_data need to be managed separately

    def get_distance(self, point1, point2):
        """
        Calculate distance between two points using the configured metric.

        Parameters
        ----------
        point1, point2 : array-like
            Points to calculate distance between.

        Returns
        -------
        float
            Distance between the points.
        """
        if self.metric == "euclidean":
            return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))
        elif self.metric == "manhattan":
            return sum(abs(a - b) for a, b in zip(point1, point2))
        else:
            # For other metrics, use Annoy's internal distance calculation
            # Add both points temporarily if needed
            raise NotImplementedError(f"Direct distance calculation for {self.metric} metric not implemented")


# Example usage
if __name__ == "__main__":
    # Test the implementation
    annoy_tree = KDTree([], 2)

    # Add some points
    annoy_tree.add_point((1.0, 2.0), {"color": "red", "value": 10})
    annoy_tree.add_point((3.0, 4.0), {"color": "blue", "value": 20})
    annoy_tree.add_point((5.0, 1.0), {"color": "green", "value": 30})

    # Find nearest neighbor
    nearest = annoy_tree.get_nearest((2.0, 3.0), True)
    if nearest:
        dist_squared, (point, data) = nearest
        print(f"Nearest point: {point}, Data: {data}, Distance�: {dist_squared}")

    # Test with initial points
    initial_points = [
        ((0.0, 0.0), {"id": 1}),
        ((1.0, 1.0), {"id": 2}),
        ((2.0, 0.0), {"id": 3}),
    ]
    annoy_tree2 = KDTree(initial_points, 2)

    nearest2 = annoy_tree2.get_nearest((0.5, 0.5), False)
    if nearest2:
        point, data = nearest2
        print(f"Nearest to (0.5, 0.5): {point}, Data: {data}")

    # Test k-nearest neighbors
    knn = annoy_tree2.get_knn((0.5, 0.5), 2, return_dist_sq=True)
    print("\n2 nearest neighbors to (0.5, 0.5):")
    for dist_sq, (pt, props) in knn:
        print(f"  Point: {pt}, Properties: {props}, Distance�: {dist_sq}")
