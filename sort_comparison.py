"""
Heapsort, Quicksort, and Merge Sort for various data sizes and types (random, sorted, reverse-sorted).
"""

import argparse
import csv
import math
import os
import random
import statistics
import time

from heapsort import heapsort
from other_sorts import quicksort, merge_sort

FULL_SIZES = [1000, 5000, 10000, 50000, 100000]
QUICK_SIZES = [500, 1000, 5000]
DISTRIBUTIONS = ["random", "sorted", "reverse"]
REPEATS = 3
SEED = 42

ALGORITHMS = {
    "Heapsort": heapsort,
    "Quicksort": quicksort,
    "Merge Sort": merge_sort,
    "sorted() ref": sorted,
}

RESULTS_DIR = "results"


def make_input(n, kind, rng):
    "Create an input list of size n with the required distribution."
    if kind == "random":
        return [rng.randint(0, n * 10) for _ in range(n)]
    if kind == "sorted":
        return list(range(n))
    if kind == "reverse":
        return list(range(n, 0, -1))
    raise ValueError(f"unknown distribution: {kind}")


def time_sort(func, data):
    """Run func on a copy of data and return (seconds, output list)."""
    copy = list(data)
    start = time.perf_counter()
    output = func(copy)
    elapsed = time.perf_counter() - start
    return elapsed, output


def run_benchmark(sizes, repeats):
    rng = random.Random(SEED)
    random.seed(SEED)  # quicksort uses the global random module for pivots

    rows = []
    for dist in DISTRIBUTIONS:
        for n in sizes:
            data = make_input(n, dist, rng)
            expected = sorted(data)

            for name, func in ALGORITHMS.items():
                times = []
                for _ in range(repeats):
                    elapsed, output = time_sort(func, data)
                    if output != expected:
                        raise AssertionError(f"{name} gave a wrong answer (n={n}, {dist})")
                    times.append(elapsed)

                mean_s = statistics.mean(times)
                rows.append({
                    "distribution": dist,
                    "n": n,
                    "algorithm": name,
                    "mean_ms": mean_s * 1000,
                    "min_ms": min(times) * 1000,
                    # time / (n log2 n), in nanoseconds. If the algorithm is really
                    # O(n log n), this number should stay roughly flat as n grows.
                    "ns_per_nlogn": (mean_s * 1e9) / (n * math.log2(n)),
                })
            print(f"  done: {dist:<8} n={n}")
    return rows


def print_tables(rows, sizes):
    names = list(ALGORITHMS.keys())
    for dist in DISTRIBUTIONS:
        print()
        print(f"=== {dist.upper()} input: mean time in ms (average of {REPEATS} runs) ===")
        header = f"{'n':>8} | " + " | ".join(f"{name:>13}" for name in names)
        print(header)
        print("-" * len(header))
        for n in sizes:
            cells = []
            for name in names:
                row = next(r for r in rows
                           if r["distribution"] == dist and r["n"] == n and r["algorithm"] == name)
                cells.append(f"{row['mean_ms']:>13.2f}")
            print(f"{n:>8} | " + " | ".join(cells))

    print()
    print("=== Heapsort time / (n log2 n) in nanoseconds (should stay roughly flat) ===")
    header = f"{'n':>8} | " + " | ".join(f"{d:>10}" for d in DISTRIBUTIONS)
    print(header)
    print("-" * len(header))
    for n in sizes:
        cells = []
        for dist in DISTRIBUTIONS:
            row = next(r for r in rows
                       if r["distribution"] == dist and r["n"] == n and r["algorithm"] == "Heapsort")
            cells.append(f"{row['ns_per_nlogn']:>10.2f}")
        print(f"{n:>8} | " + " | ".join(cells))


def save_csv(rows):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "sort_results.csv")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for r in rows:
            writer.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
    print(f"\nSaved CSV to {path}")


def save_plot(rows, sizes):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed, skipping the chart (pip install matplotlib)")
        return

    fig, axes = plt.subplots(1, len(DISTRIBUTIONS), figsize=(15, 4.5), sharey=True)
    for ax, dist in zip(axes, DISTRIBUTIONS):
        for name in ALGORITHMS:
            ys = [next(r["mean_ms"] for r in rows
                       if r["distribution"] == dist and r["n"] == n and r["algorithm"] == name)
                  for n in sizes]
            style = "--" if name == "sorted() ref" else "-"
            ax.plot(sizes, ys, style, marker="o", label=name)
        ax.set_title(f"{dist} input")
        ax.set_xlabel("n (number of elements)")
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("mean time (ms)")
    axes[0].legend()
    fig.suptitle("Heapsort vs Quicksort vs Merge Sort")
    fig.tight_layout()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "sort_comparison.png")
    fig.savefig(path, dpi=150)
    print(f"Saved chart to {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare Heapsort, Quicksort and Merge Sort.")
    parser.add_argument("--quick", action="store_true", help="use small sizes for a fast run")
    args = parser.parse_args(argv)

    sizes = QUICK_SIZES if args.quick else FULL_SIZES
    print(f"Running sort comparison on sizes {sizes}, {REPEATS} repeats each...")
    rows = run_benchmark(sizes, REPEATS)
    print_tables(rows, sizes)
    save_csv(rows)
    save_plot(rows, sizes)


if __name__ == "__main__":
    main()
