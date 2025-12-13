import hnswlib
import numpy as np


class HNSWKDTree:
    """
    Drop-in replacement for KDTree using HNSW (Hierarchical Navigable Small World).

    HNSW is an excellent choice for dynamic nearest neighbor search:
    - Very fast queries (often faster than KD-trees for high dimensions)
    - Efficient incremental point additions (no full rebuild needed!)
    - Good memory efficiency
    - Approximate nearest neighbor (controllable accuracy)

    This implementation maintains API compatibility with the existing KDTree classes
    while leveraging HNSW's performance benefits.
    """

    def __init__(self, points=None, dim=2, space="l2", max_elements=1000000, ef_construction=200, M=16):
        """
        Initialize HNSWKDTree.

        Parameters
        ----------
        points : list<point> or list<(point, properties)>, optional
            A list of points or (point, properties) pairs.
        dim : int
            The dimension of the points (default 2 for 2D points).
        space : str
            Distance metric. Options: 'l2' (Euclidean), 'ip' (inner product), 'cosine'.
            Default is 'l2'.
        max_elements : int
            Maximum number of elements that can be stored. Can be increased later with resize_index.
            Default is 1,000,000.
        ef_construction : int
            Controls index construction time/accuracy tradeoff. Higher = better quality but slower.
            Typical range: 100-500. Default is 200.
        M : int
            Number of bi-directional links per element. Higher = better recall but more memory.
            Typical range: 5-48. Default is 16.
        """
        self.dim = dim
        self.space = space
        self.max_elements = max_elements
        self.ef_construction = ef_construction
        self.M = M

        # Create HNSW index
        self._index = hnswlib.Index(space=space, dim=dim)
        self._index.init_index(max_elements=max_elements, ef_construction=ef_construction, M=M)

        # Set ef (controls recall during search)
        # Higher ef = better accuracy but slower queries
        self._index.set_ef(50)

        self._points_data = []  # Store (point, properties) pairs
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

            # Batch add all points
            if processed_points:
                points_array = np.array([list(p[0]) for p in processed_points], dtype=np.float32)
                ids = np.arange(len(processed_points))
                self._index.add_items(points_array, ids)

                # Store points and properties
                for point, props in processed_points:
                    self._points_data.append((tuple(point), props))

                self._next_id = len(processed_points)

    def add_point(self, point, properties=None):
        """
        Add a point with optional properties to the tree.

        HNSW efficiently handles dynamic additions without rebuilding!

        Parameters
        ----------
        point : array-like
            The point coordinates (e.g., tuple, list, or numpy array).
        properties : any, optional
            Properties associated with the point (typically a dict).
        """
        # Check if we need to resize
        if self._next_id >= self.max_elements:
            # Increase capacity by 50%
            new_max = int(self.max_elements * 1.5)
            self._index.resize_index(new_max)
            self.max_elements = new_max

        # Convert point to numpy array
        point_array = np.array(list(point), dtype=np.float32).reshape(1, -1)

        # Add to index
        self._index.add_items(point_array, np.array([self._next_id]))

        # Store point and properties
        point_tuple = tuple(point)
        self._points_data.append((point_tuple, properties))
        self._next_id += 1

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
        """
        if self._next_id == 0:
            return None

        # Convert query point to numpy array
        query_array = np.array(list(point), dtype=np.float32).reshape(1, -1)

        # Query for 1 nearest neighbor
        labels, distances = self._index.knn_query(query_array, k=1)

        idx = labels[0][0]
        dist = distances[0][0]

        nearest_point, properties = self._points_data[idx]

        if return_dist_sq:
            # HNSW returns distance (not squared for L2)
            # For L2 space, the distance is already Euclidean distance, so square it
            if self.space == "l2":
                dist_sq = dist * dist
            else:
                dist_sq = dist  # For other spaces, just return the distance
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
            Whether to return squared distances.

        Returns
        -------
        list<(point, properties)> or list<(dist_sq, (point, properties))>
            The k nearest neighbors with their properties.
        """
        if self._next_id == 0:
            return []

        # Limit k to available points
        k = min(k, self._next_id)

        # Convert query point to numpy array
        query_array = np.array(list(point), dtype=np.float32).reshape(1, -1)

        # Query for k nearest neighbors
        labels, distances = self._index.knn_query(query_array, k=k)

        results = []
        for idx, dist in zip(labels[0], distances[0]):
            nearest_point, properties = self._points_data[idx]
            if return_dist_sq:
                # For L2 space, square the distance
                if self.space == "l2":
                    dist_sq = dist * dist
                else:
                    dist_sq = dist
                results.append((dist_sq, (nearest_point, properties)))
            else:
                results.append((nearest_point, properties))

        return results

    def set_ef(self, ef):
        """
        Set ef parameter (controls recall during search).

        Higher ef = better accuracy but slower queries.
        Typical range: 10-500.

        Parameters
        ----------
        ef : int
            The ef parameter value.
        """
        self._index.set_ef(ef)

    def size(self):
        """Return the number of points in the tree."""
        return self._next_id

    def is_empty(self):
        """Check if the tree is empty."""
        return self._next_id == 0

    def __iter__(self):
        """Iterate over all (point, properties) pairs in the tree."""
        return iter(self._points_data)

    def save_index(self, filepath):
        """
        Save the HNSW index to disk.

        Parameters
        ----------
        filepath : str
            Path to save the index file.
        """
        self._index.save_index(filepath)

    def load_index(self, filepath, max_elements=None):
        """
        Load a previously saved HNSW index from disk.
        Note: You need to separately save/load _points_data.

        Parameters
        ----------
        filepath : str
            Path to the saved index file.
        max_elements : int, optional
            Maximum number of elements. If not provided, uses current max_elements.
        """
        if max_elements is None:
            max_elements = self.max_elements

        self._index.load_index(filepath, max_elements=max_elements)

    def get_stats(self):
        """Get statistics about the index."""
        return {
            "size": self._next_id,
            "max_elements": self.max_elements,
            "dimension": self.dim,
            "space": self.space,
            "M": self.M,
            "ef_construction": self.ef_construction,
        }


# Example usage
if __name__ == "__main__":
    # Test the implementation
    print("Creating HNSW index...")
    hnsw_tree = HNSWKDTree([], 2)

    # Add some points
    print("Adding initial points...")
    hnsw_tree.add_point((1.0, 2.0), {"color": "red", "value": 10})
    hnsw_tree.add_point((3.0, 4.0), {"color": "blue", "value": 20})
    hnsw_tree.add_point((5.0, 1.0), {"color": "green", "value": 30})

    # Find nearest neighbor
    print("\nQuerying nearest neighbor...")
    nearest = hnsw_tree.get_nearest((2.0, 3.0), True)
    if nearest:
        dist_squared, (point, data) = nearest
        print(f"Nearest point: {point}, Data: {data}, Distance²: {dist_squared}")

    # Test with initial points
    print("\nCreating index with initial points...")
    initial_points = [
        ((0.0, 0.0), {"id": 1}),
        ((1.0, 1.0), {"id": 2}),
        ((2.0, 0.0), {"id": 3}),
    ]
    hnsw_tree2 = HNSWKDTree(initial_points, 2)

    nearest2 = hnsw_tree2.get_nearest((0.5, 0.5), False)
    if nearest2:
        point, data = nearest2
        print(f"Nearest to (0.5, 0.5): {point}, Data: {data}")

    # Test k-nearest neighbors
    knn = hnsw_tree2.get_knn((0.5, 0.5), 2, return_dist_sq=True)
    print("\n2 nearest neighbors to (0.5, 0.5):")
    for dist_sq, (pt, props) in knn:
        print(f"  Point: {pt}, Properties: {props}, Distance²: {dist_sq}")

    # Test dynamic additions
    print("\n\nTesting dynamic additions (adding 1000 points)...")
    import time

    start = time.perf_counter()
    for i in range(1000):
        hnsw_tree2.add_point((i * 0.1, i * 0.2), {"id": i + 100})
    elapsed = time.perf_counter() - start
    print(f"Added 1000 points in {elapsed * 1000:.2f}ms ({elapsed * 1000 / 1000:.4f}ms per point)")

    # Query after additions
    print("\nQuerying after additions...")
    nearest3 = hnsw_tree2.get_nearest((50.0, 100.0), True)
    if nearest3:
        dist_squared, (point, data) = nearest3
        print(f"Nearest point: {point}, Data: {data}, Distance²: {dist_squared}")

    print(f"\nIndex stats: {hnsw_tree2.get_stats()}")
