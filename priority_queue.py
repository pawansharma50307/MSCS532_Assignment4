"""
A max-heap priority queue for scheduling tasks.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    """
    One task/job for the scheduler.

    unique_id           unique identifier (utilized in position map)
    priority          current priority (higher priority = more important)
    arrival_time      time of arrival within the system
    deadline          time by which task is to be completed
    duration          length of time for which task requires the CPU
    name              optional name (used only for printing purposes)
    original_priority priority on arrival (aging can increase `priority` value)
    start_time        computed by scheduler
    finish_time       computed by scheduler
    """
    task_id: int
    priority: int
    arrival_time: float = 0.0
    deadline: float = float("inf")
    duration: float = 1.0
    name: str = ""
    original_priority: Optional[int] = None
    start_time: Optional[float] = None
    finish_time: Optional[float] = None

    def __post_init__(self):
        if self.original_priority is None:
            self.original_priority = self.priority

    def __str__(self):
        label = self.name or f"T{self.task_id}"
        return (f"{label}(prio={self.priority}, arr={self.arrival_time}, "
                f"dur={self.duration}, dl={self.deadline})")


class MaxPriorityQueue:
    """Binary max-heap of Task objects, stored in a Python list."""

    def __init__(self):
        self._heap = []   # the array holding the heap
        self._pos = {}    # task_id -> current index in self._heap

    # small helpers
    def __len__(self):
        return len(self._heap)

    def __contains__(self, task_or_id):
        return self._get_id(task_or_id) in self._pos

    def is_empty(self):
        """O(1): True if there are no tasks in the queue."""
        return len(self._heap) == 0

    def peek(self):
        """O(1): look at the highest priority task without removing it."""
        if self.is_empty():
            raise IndexError("peek from an empty priority queue")
        return self._heap[0]

    def tasks(self):
        """Snapshot of the tasks currently in the queue (heap order, not sorted)."""
        return list(self._heap)

    @staticmethod
    def _get_id(task_or_id):
        return task_or_id.task_id if isinstance(task_or_id, Task) else task_or_id

    @staticmethod
    def _higher(a, b):
        """True if task a should come out of the queue before task b."""
        if a.priority != b.priority:
            return a.priority > b.priority
        if a.arrival_time != b.arrival_time:
            return a.arrival_time < b.arrival_time
        return a.task_id < b.task_id

    def _swap(self, i, j):
        """Swap two heap slots and keep the position map in sync."""
        heap = self._heap
        heap[i], heap[j] = heap[j], heap[i]
        self._pos[heap[i].task_id] = i
        self._pos[heap[j].task_id] = j

    def _sift_up(self, i):
        """Move the task at i up while it beats its parent. O(log n)."""
        while i > 0:
            parent = (i - 1) // 2
            if self._higher(self._heap[i], self._heap[parent]):
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i):
        """Move the task at i down while a child beats it. O(log n)."""
        n = len(self._heap)
        while True:
            best = i
            left = 2 * i + 1
            right = left + 1
            if left < n and self._higher(self._heap[left], self._heap[best]):
                best = left
            if right < n and self._higher(self._heap[right], self._heap[best]):
                best = right
            if best == i:
                return
            self._swap(i, best)
            i = best

    def _index_of(self, task_or_id):
        task_id = self._get_id(task_or_id)
        if task_id not in self._pos:
            raise KeyError(f"task {task_id} is not in the priority queue")
        return self._pos[task_id]

    # core operations
    def insert(self, task):
        """
        Append a new element. Insert it at the end of the array, and sift it upwards.

        Adding an element to a Python list is O(1) amortized, and sift up goes
        no higher than the height of the tree, log2 n, hence insert is O(log n).
        """
        if task.task_id in self._pos:
            raise ValueError(f"task {task.task_id} is already in the queue")
        self._heap.append(task)
        index = len(self._heap) - 1
        self._pos[task.task_id] = index
        self._sift_up(index)

    def extract_max(self):
        """
        Remove and return the top priority task.

        The root holds the solution. Swap the last task into the root position and
        let it sink down to restore the heap. O(log n).
        """
        if self.is_empty():
            raise IndexError("extract_max from an empty priority queue")

        top = self._heap[0]
        last = self._heap.pop()
        del self._pos[top.task_id]

        if self._heap:
            self._heap[0] = last
            self._pos[last.task_id] = 0
            self._sift_down(0)

        return top

    def increase_key(self, task_or_id, new_priority):
        """
        Boost the priority of the task and bring it up. O(log n)

        The location of the task can be located in O(1) time by the position map. A higher priority will only violate the heap
        property with its parent; hence, sift up is sufficient.
        """
        i = self._index_of(task_or_id)
        task = self._heap[i]
        if new_priority < task.priority:
            raise ValueError("new priority is lower than the current one, use decrease_key")
        task.priority = new_priority
        self._sift_up(i)

    def decrease_key(self, task_or_id, new_priority):
        """Lower a task's priority and move it down. O(log n)."""
        i = self._index_of(task_or_id)
        task = self._heap[i]
        if new_priority > task.priority:
            raise ValueError("new priority is higher than the current one, use increase_key")
        task.priority = new_priority
        self._sift_down(i)

    def change_priority(self, task_or_id, new_priority):
        """Convenience wrapper: calls increase_key or decrease_key as needed."""
        i = self._index_of(task_or_id)
        if new_priority >= self._heap[i].priority:
            self.increase_key(task_or_id, new_priority)
        else:
            self.decrease_key(task_or_id, new_priority)

    # used by the tests
    def check_heap(self):
        """True if the heap property and the position map are both correct."""
        n = len(self._heap)
        for i in range(n):
            left, right = 2 * i + 1, 2 * i + 2
            if left < n and self._higher(self._heap[left], self._heap[i]):
                return False
            if right < n and self._higher(self._heap[right], self._heap[i]):
                return False
        if len(self._pos) != n:
            return False
        return all(self._pos[t.task_id] == i for i, t in enumerate(self._heap))


def demo():
    """Walk through every core operation on a small example."""
    pq = MaxPriorityQueue()
    print("is_empty() on a new queue:", pq.is_empty())

    tasks = [
        Task(1, priority=3, arrival_time=0, name="backup"),
        Task(2, priority=7, arrival_time=1, name="email"),
        Task(3, priority=5, arrival_time=2, name="report"),
        Task(4, priority=9, arrival_time=3, name="alert"),
        Task(5, priority=5, arrival_time=4, name="cleanup"),
    ]
    for t in tasks:
        pq.insert(t)
        print(f"insert {t.name:<8} -> top is now {pq.peek().name}")

    print("\nincrease_key(backup, 10)")
    pq.increase_key(1, 10)
    print("top is now:", pq.peek().name)

    print("decrease_key(alert, 2)")
    pq.decrease_key(4, 2)
    print("heap still valid:", pq.check_heap())

    print("\nExtracting everything:")
    while not pq.is_empty():
        t = pq.extract_max()
        print(f"  {t.name:<8} priority={t.priority} (arrived at {t.arrival_time})")
    print("is_empty() at the end:", pq.is_empty())


if __name__ == "__main__":
    demo()
