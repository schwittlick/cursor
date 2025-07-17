import time
import random
import numpy as np
from cursor.algorithm.kd import KDTree
from cursor.algorithm.kd_optimized import OptimizedKDTree


def generate_random_points(n, dim=2, seed=42):
    """Generate n random points in dim dimensions."""
    random.seed(seed)
    np.random.seed(seed)
    return [(np.random.rand(dim) * 1000).tolist() for _ in range(n)]


def benchmark_construction(tree_class, points, dim=2):
    """Benchmark tree construction time."""
    start = time.perf_counter()
    tree = tree_class(points, dim)
    end = time.perf_counter()
    return end - start, tree


def benchmark_nearest_neighbor(tree, query_points):
    """Benchmark nearest neighbor queries."""
    start = time.perf_counter()
    for point in query_points:
        tree.get_nearest(point, return_dist_sq=False)
    end = time.perf_counter()
    return end - start


def benchmark_k_nearest_neighbors(tree, query_points, k=5):
    """Benchmark k-nearest neighbor queries."""
    start = time.perf_counter()
    for point in query_points:
        tree.get_knn(point, k, return_dist_sq=False)
    end = time.perf_counter()
    return end - start


def run_benchmark_suite(tree_class, name, points, query_points, dim=2):
    """Run a complete benchmark suite for a tree implementation."""
    print(f"\n=== {name} ===")
    
    # Construction benchmark
    construction_time, tree = benchmark_construction(tree_class, points, dim)
    print(f"Construction time: {construction_time:.4f}s")
    
    # Nearest neighbor benchmark
    nn_time = benchmark_nearest_neighbor(tree, query_points)
    print(f"Nearest neighbor (100 queries): {nn_time:.4f}s")
    print(f"Average per query: {nn_time/len(query_points)*1000:.2f}ms")
    
    # K-nearest neighbors benchmark
    knn_time = benchmark_k_nearest_neighbors(tree, query_points, k=5)
    print(f"5-nearest neighbors (100 queries): {knn_time:.4f}s")
    print(f"Average per query: {knn_time/len(query_points)*1000:.2f}ms")
    
    return {
        'construction_time': construction_time,
        'nn_time': nn_time,
        'knn_time': knn_time
    }


def compare_implementations():
    """Compare original and optimized implementations."""
    print("KD-Tree Performance Comparison")
    print("=" * 50)
    
    # Test parameters
    n_points = 10000
    n_queries = 100
    dim = 2
    
    # Generate test data
    points = generate_random_points(n_points, dim)
    query_points = generate_random_points(n_queries, dim, seed=123)
    
    print(f"Dataset: {n_points} points, {dim}D")
    print(f"Queries: {n_queries} random points")
    
    # Benchmark original implementation
    original_results = run_benchmark_suite(KDTree, "Original KDTree", points, query_points, dim)
    
    # Benchmark optimized implementation
    optimized_results = run_benchmark_suite(OptimizedKDTree, "Optimized KDTree", points, query_points, dim)
    
    # Print comparison
    print(f"\n=== Performance Comparison ===")
    print(f"Construction speedup: {original_results['construction_time'] / optimized_results['construction_time']:.2f}x")
    print(f"Nearest neighbor speedup: {original_results['nn_time'] / optimized_results['nn_time']:.2f}x")
    print(f"K-NN speedup: {original_results['knn_time'] / optimized_results['knn_time']:.2f}x")
    
    return original_results


if __name__ == "__main__":
    results = compare_implementations()