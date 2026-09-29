"""
A small single-CPU scheduler simulation that uses MaxPriorityQueue.
"""

import argparse
import copy
import csv
import os
import random
import statistics

from priority_queue import MaxPriorityQueue, Task

MAX_PRIORITY = 10
MIN_PRIORITY = 1
RESULTS_DIR = "results"


# workload
def generate_tasks(num_tasks, seed, mean_gap=4.0):
    """
    Generate a repeatable sequence of random tasks:

    - intervals of arrivals are distributed exponentially (mean_gap)
    - duration is 1..8 time units (average 4.5)
    - priority is 1..10
    - deadline = arrival + duration + slack (5..40)

    mean_gap=4.0 and average duration of 4.5 mean that tasks arrive slightly
    faster than the CPU can process them, leading to the task queue.
    """
    rng = random.Random(seed)
    tasks = []
    clock = 0.0
    for i in range(num_tasks):
        clock += rng.expovariate(1.0 / mean_gap)
        duration = rng.randint(1, 8)
        priority = rng.randint(MIN_PRIORITY, MAX_PRIORITY)
        slack = rng.randint(5, 40)
        arrival = round(clock, 2)
        tasks.append(Task(
            task_id=i + 1,
            priority=priority,
            arrival_time=arrival,
            deadline=round(arrival + duration + slack, 2),
            duration=duration,
        ))
    return tasks


# policies
def run_fcfs(tasks):
    """First come first served. Just run tasks in arrival order."""
    tasks = sorted((copy.copy(t) for t in tasks), key=lambda t: (t.arrival_time, t.task_id))
    clock = 0.0
    for t in tasks:
        clock = max(clock, t.arrival_time)   # CPU might be idle until it arrives
        t.start_time = clock
        clock += t.duration
        t.finish_time = clock
    return tasks, {"inserts": 0, "extracts": 0, "increase_key": 0}


def run_priority(tasks, aging_threshold=None):
    """
    Non-preemptive priority scheduling using the max-heap.
    """
    pending = sorted((copy.copy(t) for t in tasks), key=lambda t: (t.arrival_time, t.task_id))
    pq = MaxPriorityQueue()
    stats = {"inserts": 0, "extracts": 0, "increase_key": 0}
    last_boost = {}   # task_id -> time the aging clock was last reset for that task
    finished = []
    clock = 0.0
    idx = 0

    def admit_arrivals():
        """Insert every task that has arrived by the current clock."""
        nonlocal idx
        while idx < len(pending) and pending[idx].arrival_time <= clock:
            task = pending[idx]
            pq.insert(task)
            stats["inserts"] += 1
            last_boost[task.task_id] = task.arrival_time
            idx += 1

    while idx < len(pending) or not pq.is_empty():
        admit_arrivals()

        if pq.is_empty():
            # nothing ready, so the CPU is idle until the next arrival
            clock = pending[idx].arrival_time
            continue

        task = pq.extract_max()
        stats["extracts"] += 1
        last_boost.pop(task.task_id, None)

        task.start_time = clock
        clock += task.duration
        task.finish_time = clock
        finished.append(task)

        if aging_threshold is not None:
            # tasks that showed up while this one was running should age too
            admit_arrivals()
            for waiting in pq.tasks():
                if waiting.priority >= MAX_PRIORITY:
                    continue
                waited = clock - last_boost[waiting.task_id]
                if waited >= aging_threshold:
                    steps = int(waited // aging_threshold)
                    new_priority = min(MAX_PRIORITY, waiting.priority + steps)
                    pq.increase_key(waiting.task_id, new_priority)
                    stats["increase_key"] += 1
                    last_boost[waiting.task_id] += steps * aging_threshold

    return finished, stats


# metrics / output
def priority_group(p):
    if p >= 8:
        return "high (8-10)"
    if p >= 4:
        return "medium (4-7)"
    return "low (1-3)"


def summarize(policy_name, finished, stats):
    waits = [t.start_time - t.arrival_time for t in finished]
    turnarounds = [t.finish_time - t.arrival_time for t in finished]
    missed = sum(1 for t in finished if t.finish_time > t.deadline)

    group_waits = {}
    for t in finished:
        group_waits.setdefault(priority_group(t.original_priority), []).append(
            t.start_time - t.arrival_time)

    return {
        "policy": policy_name,
        "tasks": len(finished),
        "avg_wait": statistics.mean(waits),
        "max_wait": max(waits),
        "avg_turnaround": statistics.mean(turnarounds),
        "missed_deadlines": missed,
        "missed_pct": 100.0 * missed / len(finished),
        "makespan": max(t.finish_time for t in finished),
        "wait_high": statistics.mean(group_waits.get("high (8-10)", [0])),
        "wait_medium": statistics.mean(group_waits.get("medium (4-7)", [0])),
        "wait_low": statistics.mean(group_waits.get("low (1-3)", [0])),
        "pq_inserts": stats["inserts"],
        "pq_extracts": stats["extracts"],
        "pq_increase_key": stats["increase_key"],
    }


def print_summary(summaries):
    print()
    print("=== Scheduling results (time units) ===")
    header = (f"{'policy':<16} | {'avg wait':>9} | {'max wait':>9} | {'avg turn':>9} | "
              f"{'missed':>6} | {'missed %':>8} | {'makespan':>9}")
    print(header)
    print("-" * len(header))
    for s in summaries:
        print(f"{s['policy']:<16} | {s['avg_wait']:>9.2f} | {s['max_wait']:>9.2f} | "
              f"{s['avg_turnaround']:>9.2f} | {s['missed_deadlines']:>6} | "
              f"{s['missed_pct']:>7.1f}% | {s['makespan']:>9.2f}")

    print()
    print("=== Average waiting time by ORIGINAL priority group ===")
    header = f"{'policy':<16} | {'high (8-10)':>12} | {'medium (4-7)':>12} | {'low (1-3)':>12}"
    print(header)
    print("-" * len(header))
    for s in summaries:
        print(f"{s['policy']:<16} | {s['wait_high']:>12.2f} | {s['wait_medium']:>12.2f} | "
              f"{s['wait_low']:>12.2f}")

    print()
    print("=== Priority queue operation counts ===")
    for s in summaries:
        print(f"{s['policy']:<16} inserts={s['pq_inserts']}, extracts={s['pq_extracts']}, "
              f"increase_key={s['pq_increase_key']}")


def print_trace(finished, limit=12):
    print()
    print(f"=== First {limit} tasks dispatched under Priority+Aging ===")
    header = (f"{'task':>5} | {'orig prio':>9} | {'prio at run':>11} | {'arrival':>8} | "
              f"{'start':>8} | {'finish':>8} | {'deadline':>8} | met?")
    print(header)
    print("-" * len(header))
    for t in finished[:limit]:
        met = "yes" if t.finish_time <= t.deadline else "NO"
        print(f"{t.task_id:>5} | {t.original_priority:>9} | {t.priority:>11} | "
              f"{t.arrival_time:>8.2f} | {t.start_time:>8.2f} | {t.finish_time:>8.2f} | "
              f"{t.deadline:>8.2f} | {met}")


def save_csv(summaries):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, "scheduler_summary.csv")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0].keys()))
        writer.writeheader()
        for s in summaries:
            writer.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()})
    print(f"\nSaved CSV to {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Priority queue scheduler simulation.")
    parser.add_argument("--tasks", type=int, default=200, help="number of tasks (default 200)")
    parser.add_argument("--seed", type=int, default=7, help="random seed (default 7)")
    parser.add_argument("--aging", type=float, default=20.0,
                        help="aging threshold in time units (default 20)")
    args = parser.parse_args(argv)

    tasks = generate_tasks(args.tasks, args.seed)
    print(f"Simulating {args.tasks} tasks (seed={args.seed}, aging threshold={args.aging})")

    fcfs_done, fcfs_stats = run_fcfs(tasks)
    prio_done, prio_stats = run_priority(tasks, aging_threshold=None)
    aging_done, aging_stats = run_priority(tasks, aging_threshold=args.aging)

    summaries = [
        summarize("FCFS", fcfs_done, fcfs_stats),
        summarize("Priority", prio_done, prio_stats),
        summarize("Priority+Aging", aging_done, aging_stats),
    ]
    print_summary(summaries)
    print_trace(aging_done)
    save_csv(summaries)


if __name__ == "__main__":
    main()
