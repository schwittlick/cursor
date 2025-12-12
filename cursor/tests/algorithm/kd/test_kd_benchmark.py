"""
Benchmark comparison test for KD-tree implementations.

Compares performance of four implementations:
1. KDTree (kd.py) - Compact implementation with heapq
2. KDTree2 (kd2.py) - Traditional recursive implementation
3. AnnoyKDTree (kd_annoy.py) - Spotify Annoy library wrapper
4. HNSWKDTree (kd_hnsw.py) - HNSW (Hierarchical Navigable Small World)

Run with: python -m pytest cursor/tests/algorithm/test_kd_benchmark.py -v -s
"""

import time
import random
from cursor.algorithm.kd.kd import KDTree as KDTreeCompact
from cursor.algorithm.kd.kd2 import KDTree as KDTreeTraditional
from cursor.algorithm.kd.kd_annoy import AnnoyKDTree
from cursor.algorithm.kd.kd_hnsw import HNSWKDTree
import statistics


def generate_random_points_2d(n, min_val=0, max_val=1000):
    """Generate n random 2D points with properties."""
    return [
        ((random.uniform(min_val, max_val), random.uniform(min_val, max_val)), {"id": i})
        for i in range(n)
    ]


def generate_random_points_3d(n, min_val=0, max_val=1000):
    """Generate n random 3D points with properties."""
    return [
        (
            (
                random.uniform(min_val, max_val),
                random.uniform(min_val, max_val),
                random.uniform(min_val, max_val),
            ),
            {"id": i},
        )
        for i in range(n)
    ]


class BenchmarkResult:
    """Store and display benchmark results."""

    def __init__(self, name):
        self.name = name
        self.build_time = 0
        self.query_times = []
        self.knn_times = []

    def add_query_time(self, t):
        self.query_times.append(t)

    def add_knn_time(self, t):
        self.knn_times.append(t)

    @property
    def avg_query_time(self):
        return statistics.mean(self.query_times) if self.query_times else 0

    @property
    def avg_knn_time(self):
        return statistics.mean(self.knn_times) if self.knn_times else 0

    @property
    def median_query_time(self):
        return statistics.median(self.query_times) if self.query_times else 0

    @property
    def median_knn_time(self):
        return statistics.median(self.knn_times) if self.knn_times else 0

    def __str__(self):
        return f"""
{self.name}:
  Build time: {self.build_time*1000:.2f}ms
  Single query (avg): {self.avg_query_time*1000:.4f}ms
  Single query (median): {self.median_query_time*1000:.4f}ms
  KNN query (avg): {self.avg_knn_time*1000:.4f}ms
  KNN query (median): {self.median_knn_time*1000:.4f}ms
"""


def benchmark_tree(tree_class, points, query_points, k=10, dim=2, **kwargs):
    """
    Benchmark a tree implementation.

    Parameters
    ----------
    tree_class : class
        The tree class to benchmark.
    points : list
        List of (point, properties) tuples to initialize the tree.
    query_points : list
        List of points to query.
    k : int
        Number of nearest neighbors for KNN queries.
    dim : int
        Dimensionality of points.
    **kwargs : dict
        Additional arguments for tree initialization.

    Returns
    -------
    BenchmarkResult
        Object containing timing results.
    """
    result = BenchmarkResult(tree_class.__name__)

    # Benchmark build time
    start = time.perf_counter()
    tree = tree_class(points, dim, **kwargs)
    result.build_time = time.perf_counter() - start

    # Determine parameter name for get_nearest (different between implementations)
    # kd2.py uses return_distance, others use return_dist_sq
    is_kd2 = tree_class.__name__ == "KDTree" and not hasattr(tree, "get_knn")
    distance_param = "return_distance" if is_kd2 else "return_dist_sq"

    # Benchmark single nearest neighbor queries
    for query_point in query_points:
        start = time.perf_counter()
        tree.get_nearest(query_point, **{distance_param: False})
        result.add_query_time(time.perf_counter() - start)

    # Benchmark k-nearest neighbor queries (if supported)
    if hasattr(tree, "get_knn"):
        for query_point in query_points:
            start = time.perf_counter()
            tree.get_knn(query_point, k, return_dist_sq=False)
            result.add_knn_time(time.perf_counter() - start)
    else:
        # Fallback: call get_nearest k times for trees without get_knn
        for query_point in query_points:
            start = time.perf_counter()
            # Simulate KNN by calling get_nearest k times
            # (This is obviously not accurate, but gives us something to compare)
            for _ in range(k):
                tree.get_nearest(query_point, **{distance_param: False})
            result.add_knn_time(time.perf_counter() - start)

    return result


def print_comparison_table(results):
    """Print a comparison table of benchmark results."""
    print("\n" + "=" * 80)
    print("BENCHMARK COMPARISON TABLE")
    print("=" * 80)

    # Find baseline (fastest) for each metric
    fastest_build = min(r.build_time for r in results)
    fastest_query = min(r.avg_query_time for r in results)
    fastest_knn = min(r.avg_knn_time for r in results)

    print(f"\n{'Implementation':<20} {'Build (ms)':<15} {'Query (ms)':<15} {'KNN (ms)':<15}")
    print("-" * 80)

    has_kd2 = any("KDTree" in r.name and "Compact" not in r.name and "Traditional" in r.name for r in results)

    for r in results:
        build_speedup = f"{r.build_time / fastest_build:.2f}x" if fastest_build > 0 else "N/A"
        query_speedup = (
            f"{r.avg_query_time / fastest_query:.2f}x" if fastest_query > 0 else "N/A"
        )
        knn_speedup = f"{r.avg_knn_time / fastest_knn:.2f}x" if fastest_knn > 0 else "N/A"

        build_str = f"{r.build_time*1000:.2f} ({build_speedup})"
        query_str = f"{r.avg_query_time*1000:.4f} ({query_speedup})"
        knn_str = f"{r.avg_knn_time*1000:.4f} ({knn_speedup})"

        # Add asterisk for KDTreeTraditional which doesn't have native get_knn
        if "Traditional" in r.name or ("KDTree" == r.name):
            knn_str += "*"

        print(f"{r.name:<20} {build_str:<15} {query_str:<15} {knn_str:<15}")

    print("=" * 80)
    if has_kd2:
        print("* KDTreeTraditional doesn't have get_knn; simulated by calling get_nearest k times")
    print()


def test_benchmark_small_2d():
    """Benchmark with small dataset (100 points) in 2D."""
    print("\n" + "=" * 80)
    print("TEST: Small Dataset (100 points, 2D)")
    print("=" * 80)

    random.seed(42)
    n_points = 100
    n_queries = 50
    k = 5

    points = generate_random_points_2d(n_points)
    query_points = [p[0] for p in generate_random_points_2d(n_queries)]

    results = []

    # Benchmark each implementation
    print("\nBenchmarking KDTreeCompact...")
    results.append(benchmark_tree(KDTreeCompact, points, query_points, k=k, dim=2))

    print("Benchmarking KDTreeTraditional...")
    results.append(benchmark_tree(KDTreeTraditional, points, query_points, k=k, dim=2))

    print("Benchmarking AnnoyKDTree...")
    results.append(
        benchmark_tree(AnnoyKDTree, points, query_points, k=k, dim=2, n_trees=10)
    )

    print("Benchmarking HNSWKDTree...")
    results.append(
        benchmark_tree(HNSWKDTree, points, query_points, k=k, dim=2, M=16, ef_construction=200)
    )

    # Print detailed results
    for result in results:
        print(result)

    print_comparison_table(results)


def test_benchmark_medium_2d():
    """Benchmark with medium dataset (1000 points) in 2D."""
    print("\n" + "=" * 80)
    print("TEST: Medium Dataset (1,000 points, 2D)")
    print("=" * 80)

    random.seed(42)
    n_points = 1000
    n_queries = 100
    k = 10

    points = generate_random_points_2d(n_points)
    query_points = [p[0] for p in generate_random_points_2d(n_queries)]

    results = []

    print("\nBenchmarking KDTreeCompact...")
    results.append(benchmark_tree(KDTreeCompact, points, query_points, k=k, dim=2))

    print("Benchmarking KDTreeTraditional...")
    results.append(benchmark_tree(KDTreeTraditional, points, query_points, k=k, dim=2))

    print("Benchmarking AnnoyKDTree...")
    results.append(
        benchmark_tree(AnnoyKDTree, points, query_points, k=k, dim=2, n_trees=20)
    )

    print("Benchmarking HNSWKDTree...")
    results.append(
        benchmark_tree(HNSWKDTree, points, query_points, k=k, dim=2, M=16, ef_construction=200)
    )

    for result in results:
        print(result)

    print_comparison_table(results)


def test_benchmark_large_2d():
    """Benchmark with large dataset (10,000 points) in 2D."""
    print("\n" + "=" * 80)
    print("TEST: Large Dataset (10,000 points, 2D)")
    print("=" * 80)

    random.seed(42)
    n_points = 10000
    n_queries = 100
    k = 10

    points = generate_random_points_2d(n_points)
    query_points = [p[0] for p in generate_random_points_2d(n_queries)]

    results = []

    print("\nBenchmarking KDTreeCompact...")
    results.append(benchmark_tree(KDTreeCompact, points, query_points, k=k, dim=2))

    print("Benchmarking KDTreeTraditional...")
    results.append(benchmark_tree(KDTreeTraditional, points, query_points, k=k, dim=2))

    print("Benchmarking AnnoyKDTree...")
    results.append(
        benchmark_tree(AnnoyKDTree, points, query_points, k=k, dim=2, n_trees=30)
    )

    print("Benchmarking HNSWKDTree...")
    results.append(
        benchmark_tree(HNSWKDTree, points, query_points, k=k, dim=2, M=16, ef_construction=200)
    )

    for result in results:
        print(result)

    print_comparison_table(results)


def test_benchmark_3d():
    """Benchmark with 3D points."""
    print("\n" + "=" * 80)
    print("TEST: 3D Dataset (1,000 points)")
    print("=" * 80)

    random.seed(42)
    n_points = 1000
    n_queries = 100
    k = 10

    points = generate_random_points_3d(n_points)
    query_points = [p[0] for p in generate_random_points_3d(n_queries)]

    results = []

    print("\nBenchmarking KDTreeCompact...")
    results.append(benchmark_tree(KDTreeCompact, points, query_points, k=k, dim=3))

    print("Benchmarking KDTreeTraditional...")
    results.append(benchmark_tree(KDTreeTraditional, points, query_points, k=k, dim=3))

    print("Benchmarking AnnoyKDTree...")
    results.append(
        benchmark_tree(AnnoyKDTree, points, query_points, k=k, dim=3, n_trees=20)
    )

    print("Benchmarking HNSWKDTree...")
    results.append(
        benchmark_tree(HNSWKDTree, points, query_points, k=k, dim=3, M=16, ef_construction=200)
    )

    for result in results:
        print(result)

    print_comparison_table(results)


def test_benchmark_varying_k():
    """Benchmark with varying k values for KNN queries."""
    print("\n" + "=" * 80)
    print("TEST: Varying K (1,000 points, 2D)")
    print("=" * 80)

    random.seed(42)
    n_points = 1000
    n_queries = 50
    k_values = [1, 5, 10, 20, 50]

    points = generate_random_points_2d(n_points)
    query_points = [p[0] for p in generate_random_points_2d(n_queries)]

    for k in k_values:
        print(f"\n--- K = {k} ---")
        results = []

        results.append(benchmark_tree(KDTreeCompact, points, query_points, k=k, dim=2))
        results.append(
            benchmark_tree(KDTreeTraditional, points, query_points, k=k, dim=2)
        )
        results.append(
            benchmark_tree(AnnoyKDTree, points, query_points, k=k, dim=2, n_trees=20)
        )
        results.append(
            benchmark_tree(HNSWKDTree, points, query_points, k=k, dim=2, M=16, ef_construction=200)
        )

        print_comparison_table(results)


def test_benchmark_incremental_adds():
    """Benchmark incremental point additions."""
    print("\n" + "=" * 80)
    print("TEST: Incremental Additions (adding 100 points one by one)")
    print("=" * 80)

    random.seed(42)
    n_points = 100
    points = generate_random_points_2d(n_points)

    results = []

    # Benchmark KDTreeCompact
    print("\nBenchmarking KDTreeCompact incremental adds...")
    tree = KDTreeCompact([], 2)
    start = time.perf_counter()
    for point, props in points:
        tree.add_point(point, props)
    compact_time = time.perf_counter() - start

    # Benchmark KDTreeTraditional
    print("Benchmarking KDTreeTraditional incremental adds...")
    tree = KDTreeTraditional([], 2)
    start = time.perf_counter()
    for point, props in points:
        tree.add_point(point, props)
    traditional_time = time.perf_counter() - start

    # Benchmark AnnoyKDTree
    print("Benchmarking AnnoyKDTree incremental adds...")
    tree = AnnoyKDTree([], 2, n_trees=10)
    start = time.perf_counter()
    for point, props in points:
        tree.add_point(point, props)
    annoy_time = time.perf_counter() - start

    # Benchmark HNSWKDTree
    print("Benchmarking HNSWKDTree incremental adds...")
    tree = HNSWKDTree([], 2, M=16, ef_construction=200)
    start = time.perf_counter()
    for point, props in points:
        tree.add_point(point, props)
    hnsw_time = time.perf_counter() - start

    print("\n" + "=" * 80)
    print("INCREMENTAL ADD COMPARISON")
    print("=" * 80)
    print(f"{'Implementation':<20} {'Time (ms)':<15} {'Relative':<15}")
    print("-" * 80)

    fastest = min(compact_time, traditional_time, annoy_time, hnsw_time)
    print(
        f"{'KDTreeCompact':<20} {compact_time*1000:.2f}{'':<9} {compact_time/fastest:.2f}x"
    )
    print(
        f"{'KDTreeTraditional':<20} {traditional_time*1000:.2f}{'':<9} {traditional_time/fastest:.2f}x"
    )
    print(
        f"{'AnnoyKDTree':<20} {annoy_time*1000:.2f}{'':<9} {annoy_time/fastest:.2f}x"
    )
    print(
        f"{'HNSWKDTree':<20} {hnsw_time*1000:.2f}{'':<9} {hnsw_time/fastest:.2f}x"
    )
    print("=" * 80)
    print("\nNotes:")
    print("  - Annoy is slower for incremental adds (rebuilds entire index each time)")
    print("  - HNSW is designed for dynamic additions (no rebuild needed!)")
    print("  - For Annoy: Initialize with all points at once for best performance")
    print("  - For HNSW: Can add points incrementally without performance penalty\n")


def test_benchmark_summary():
    """Run all benchmarks and provide a summary."""
    print("\n" + "=" * 80)
    print("RUNNING COMPLETE BENCHMARK SUITE")
    print("=" * 80)
    print("\nThis will run multiple benchmark tests comparing four KD-tree implementations:")
    print("  1. KDTreeCompact (kd.py) - Compact heap-based implementation")
    print("  2. KDTreeTraditional (kd2.py) - Traditional recursive implementation")
    print("  3. AnnoyKDTree (kd_annoy.py) - Spotify Annoy library wrapper")
    print("  4. HNSWKDTree (kd_hnsw.py) - HNSW (Hierarchical Navigable Small World)")
    print("\nBenchmarks include:")
    print("  - Small dataset (100 points)")
    print("  - Medium dataset (1,000 points)")
    print("  - Large dataset (10,000 points)")
    print("  - 3D points")
    print("  - Varying K values")
    print("  - Incremental additions (most important for dynamic use!)")
    print("\n" + "=" * 80 + "\n")

    # Run all benchmarks
    test_benchmark_small_2d()
    test_benchmark_medium_2d()
    test_benchmark_large_2d()
    test_benchmark_3d()
    test_benchmark_varying_k()
    test_benchmark_incremental_adds()

    print("\n" + "=" * 80)
    print("BENCHMARK SUITE COMPLETE")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("  - KDTreeCompact: Good all-around, has get_knn, compact code")
    print("  - KDTreeTraditional: Readable, educational purposes, no get_knn")
    print("  - AnnoyKDTree: Fast queries, SLOW incremental adds (rebuilds every time)")
    print("  - HNSWKDTree: BEST for dynamic additions, fast queries, scales well")
    print("\n🏆 Recommendations:")
    print("  - Need dynamic additions? → HNSWKDTree (no rebuild penalty!)")
    print("  - Static small datasets? → KDTreeCompact")
    print("  - Educational/exact NN? → KDTreeTraditional")
    print("  - Static large datasets? → AnnoyKDTree or HNSWKDTree")
    print("\nAPI Notes:")
    print("  - KDTreeCompact, AnnoyKDTree, HNSWKDTree: use return_dist_sq parameter")
    print("  - KDTreeTraditional: uses return_distance parameter")
    print("  - KDTreeTraditional: doesn't have get_knn method (only get_nearest)")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Run the full benchmark suite
    test_benchmark_summary()
