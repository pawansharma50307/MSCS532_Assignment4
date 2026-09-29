"""
Runs all codes:
"""

import argparse

import pq_timing
import priority_queue
import scheduler
import sort_comparison
import test_heaps
from heapsort import build_max_heap, heapsort


def section(title):
    print()
    print("#" * 70)
    print(f"# {title}")
    print("#" * 70)


def main():
    parser = argparse.ArgumentParser(description="Run all codes.")
    parser.add_argument("--quick", action="store_true", help="smaller sorting benchmark")
    args = parser.parse_args()

    section("1. Correctness tests")
    test_heaps.run_all()

    section("2a. Heapsort demo")
    data = [4, 10, 3, 5, 1, 8, 7, 2, 9, 6]
    heap = list(data)
    build_max_heap(heap)
    print("input:         ", data)
    print("as a max-heap: ", heap)
    print("sorted:        ", heapsort(list(data)))

    section("2b. Priority queue demo")
    priority_queue.demo()

    section("3. Sorting comparison")
    sort_comparison.main(["--quick"] if args.quick else [])

    section("4. Priority queue operation timing")
    pq_timing.main([])

    section("5. Scheduler simulation")
    scheduler.main([])


if __name__ == "__main__":
    main()
