"""
Averages the cost of performing each priority queue operation on several
sizes of queues. If these operations do have O(log n) complexity, then the 
cost per operation should increase slowly (about log2 n).
"""

import math
import random
import time

from priority_queue import MaxPriorityQueue, Task

SIZES = [1000, 10000, 100000]
KEY_CHANGES = 2000
SEED = 123


def time_operations(n, rng):
    pq = MaxPriorityQueue()
    tasks = [Task(task_id=i, priority=rng.randint(1, 1_000_000), arrival_time=i) for i in range(n)]

    # insert
    start = time.perf_counter()
    for t in tasks:
        pq.insert(t)
    insert_us = (time.perf_counter() - start) / n * 1e6

    # increase_key on random tasks
    picks = [rng.randrange(n) for _ in range(KEY_CHANGES)]
    start = time.perf_counter()
    for i in picks:
        task = tasks[i]
        pq.increase_key(task.task_id, task.priority + rng.randint(1, 1000))
    inc_us = (time.perf_counter() - start) / KEY_CHANGES * 1e6

    # decrease_key on random tasks
    picks = [rng.randrange(n) for _ in range(KEY_CHANGES)]
    start = time.perf_counter()
    for i in picks:
        task = tasks[i]
        pq.decrease_key(task.task_id, task.priority - rng.randint(1, 1000))
    dec_us = (time.perf_counter() - start) / KEY_CHANGES * 1e6

    assert pq.check_heap(), "heap property broken after key changes"

    # extract_max until empty, and check the order is correct
    start = time.perf_counter()
    previous = None
    while not pq.is_empty():
        t = pq.extract_max()
        if previous is not None and t.priority > previous:
            raise AssertionError("extract_max returned tasks out of order")
        previous = t.priority
    extract_us = (time.perf_counter() - start) / n * 1e6

    return insert_us, extract_us, inc_us, dec_us


def main(argv=None):
    rng = random.Random(SEED)
    print("=== Priority queue operation timing (microseconds per operation) ===")
    header = (f"{'n':>8} | {'log2 n':>6} | {'insert':>8} | {'extract_max':>11} | "
              f"{'increase_key':>12} | {'decrease_key':>12}")
    print(header)
    print("-" * len(header))
    for n in SIZES:
        ins, ext, inc, dec = time_operations(n, rng)
        print(f"{n:>8} | {math.log2(n):>6.1f} | {ins:>8.3f} | {ext:>11.3f} | "
              f"{inc:>12.3f} | {dec:>12.3f}")
    print("\n(insert and increase_key are usually cheap on random data because new/boosted")
    print(" items rarely need to climb far; extract_max always sifts from the root.)")


if __name__ == "__main__":
    main()
