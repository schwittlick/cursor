import random

from cursor.algorithm.kd import KDTree
from cursor.path import Path


def test_all():
    dim = 3

    def dist_sq_func(a, b):
        return sum((x - b[i]) ** 2 for i, x in enumerate(a))

    def get_knn_naive(points, point, k, return_dist_sq=True):
        neighbors = []
        for i, pp in enumerate(points):
            dist_sq = dist_sq_func(point, pp)
            neighbors.append((dist_sq, pp))
        neighbors = sorted(neighbors)[:k]
        return neighbors if return_dist_sq else [n[1] for n in neighbors]

    def get_nearest_naive(points, point, return_dist_sq=True):
        nearest = min(points, key=lambda p: dist_sq_func(p, point))
        if return_dist_sq:
            return (dist_sq_func(nearest, point), nearest)
        return nearest

    def rand_point(dim):
        return [random.uniform(-1, 1) for d in range(dim)]

    points = [rand_point(dim) for x in range(10000)]
    additional_points = [rand_point(dim) for x in range(100)]
    query_points = [rand_point(dim) for x in range(100)]

    kd_tree_results = []
    naive_results = []

    def test_and_bench_kd_tree():
        global kd_tree
        kd_tree = KDTree(points, dim)
        for point in additional_points:
            kd_tree.add_point(point)
        kd_tree_results.append(tuple(kd_tree.get_knn([0] * dim, 8)))
        for t in query_points:
            kd_tree_results.append(tuple(kd_tree.get_knn(t, 8)))
        for t in query_points:
            kd_tree_results.append(tuple(kd_tree.get_nearest(t)))

    def test_and_bench_naive():
        all_points = points + additional_points
        naive_results.append(tuple(get_knn_naive(all_points, [0] * dim, 8)))
        for t in query_points:
            naive_results.append(tuple(get_knn_naive(all_points, t, 8)))
        for t in query_points:
            naive_results.append(tuple(get_nearest_naive(all_points, t)))

    print("Running KDTree...")
    test_and_bench_kd_tree()

    print("Running naive version...")
    test_and_bench_naive()

    print("Query results same as naive version?: {}"
          .format(kd_tree_results == naive_results))

    assert kd_tree_results == naive_results, "Query results mismatch"

    assert len(list(kd_tree)) == len(points) + len(additional_points), "Number of points from iterator mismatch"


def test_extension():
    path = Path.from_tuple_list([(0, 0), (1, 1), (2, 3), (3, 1), (1, 5)])

    kd_tree = KDTree(path.as_tuple_list(), 2)
    kd_tree.add_point((4, 4))

    nearest = kd_tree.get_nearest((3, 4), False)
    assert nearest == (4, 4)

    nearest_with_distance = kd_tree.get_nearest((3, 4), True)
    assert nearest_with_distance == (1, (4, 4))
