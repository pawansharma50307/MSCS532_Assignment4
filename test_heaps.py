"""
Simple correctness checks.
"""

import random

from heapsort import heapsort, build_max_heap, is_max_heap
from other_sorts import quicksort, merge_sort
from priority_queue import MaxPriorityQueue, Task


def _sample_lists():
    rng = random.Random(1)
    return [
        [],
        [1],
        [2, 1],
        [5, 5, 5, 5],
        [3, -1, 0, -7, 8, 2],
        list(range(50)),
        list(range(50, 0, -1)),
        [rng.randint(0, 20) for _ in range(200)],       # lots of duplicates
        [rng.random() for _ in range(300)],             # floats
    ]


def test_build_max_heap():
    for data in _sample_lists():
        arr = list(data)
        build_max_heap(arr)
        assert is_max_heap(arr), f"build_max_heap failed on {data[:10]}..."
        assert sorted(arr) == sorted(data), "build_max_heap lost or changed elements"


def test_sorting_algorithms():
    for data in _sample_lists():
        expected = sorted(data)
        assert heapsort(list(data)) == expected, "heapsort wrong"
        assert quicksort(list(data)) == expected, "quicksort wrong"
        assert merge_sort(list(data)) == expected, "merge_sort wrong"


def test_pq_basic_order():
    pq = MaxPriorityQueue()
    assert pq.is_empty()
    for i, p in enumerate([4, 9, 1, 7, 7, 3]):
        pq.insert(Task(task_id=i, priority=p, arrival_time=i))
        assert pq.check_heap()
    assert not pq.is_empty()
    assert len(pq) == 6

    out = []
    while not pq.is_empty():
        out.append(pq.extract_max())
        assert pq.check_heap()
    assert [t.priority for t in out] == [9, 7, 7, 4, 3, 1]
    # the two 7s: the one that arrived first (task 3) should come out first
    assert out[1].task_id == 3 and out[2].task_id == 4


def test_pq_key_changes():
    pq = MaxPriorityQueue()
    for i in range(10):
        pq.insert(Task(task_id=i, priority=i))
    pq.increase_key(0, 100)
    assert pq.peek().task_id == 0
    pq.decrease_key(0, -5)
    assert pq.peek().task_id == 9
    pq.change_priority(3, 50)
    assert pq.peek().task_id == 3
    assert pq.check_heap()

    # bad calls should raise errors
    for bad in (lambda: pq.increase_key(3, 1),
                lambda: pq.decrease_key(3, 99),
                lambda: pq.increase_key(999, 5)):
        try:
            bad()
        except (ValueError, KeyError):
            pass
        else:
            raise AssertionError("expected an error")


def test_pq_errors_on_empty_and_duplicates():
    pq = MaxPriorityQueue()
    try:
        pq.extract_max()
    except IndexError:
        pass
    else:
        raise AssertionError("extract_max on empty queue should raise IndexError")

    pq.insert(Task(task_id=1, priority=1))
    try:
        pq.insert(Task(task_id=1, priority=5))
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate task_id should raise ValueError")


def test_pq_random_operations():
    """Throw a lot of random operations at the queue and keep checking it."""
    rng = random.Random(99)
    pq = MaxPriorityQueue()
    inside = {}
    next_id = 0
    for _ in range(3000):
        action = rng.random()
        if action < 0.45 or not inside:
            t = Task(task_id=next_id, priority=rng.randint(0, 100), arrival_time=next_id)
            pq.insert(t)
            inside[next_id] = t
            next_id += 1
        elif action < 0.70:
            top = pq.extract_max()
            assert top.priority == max(t.priority for t in inside.values())
            del inside[top.task_id]
        else:
            tid = rng.choice(list(inside.keys()))
            pq.change_priority(tid, rng.randint(0, 100))
        assert pq.check_heap()
        assert len(pq) == len(inside)


def run_all():
    tests = [
        test_build_max_heap,
        test_sorting_algorithms,
        test_pq_basic_order,
        test_pq_key_changes,
        test_pq_errors_on_empty_and_duplicates,
        test_pq_random_operations,
    ]
    for test in tests:
        test()
        print(f"  PASS  {test.__name__}")
    print(f"All {len(tests)} tests passed.")


if __name__ == "__main__":
    run_all()
