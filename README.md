# Assignment 4: Heap Data Structures – Implementation, Analysis, and Applications

This repo has my Python code and results. It covers two things:

1. **Heapsort** - my own Heapsort algorithm, along with a timing test with Quicksort and Merge Sort for varying input sizes and orders.
2. **Priority Queue** - a binary max heap using Task objects implementing `insert`, `extract_max`, `increase_key`, `decrease_key` and `is_empty`, and a small CPU scheduler program that utilizes it.

## Files

| File | What it does |
|---|---|
| `heapsort.py` | Heapsort (`sift_down`, `build_max_heap`, `heapsort`) |
| `other_sorts.py` | Randomized Quicksort and Merge Sort, used for the comparison |
| `sort_comparison.py` | Times all three sorts on random, sorted, and reverse-sorted input |
| `priority_queue.py` | `Task` class and `MaxPriorityQueue` (array-based max-heap) |
| `pq_timing.py` | Measures the average time of each priority queue operation |
| `scheduler.py` | Scheduler simulation: FCFS vs Priority vs Priority with aging |
| `test_heaps.py` | Correctness tests for all of the above |
| `main.py` | Runs everything in order |
| `results/` | Created when we run the code|
| `Assignment 4 Report.docx` | The report |

## Requirements

- Python

```bash
pip install -r requirements.txt
```

## How to run

Run everything at once:

```bash
python main.py
```

Or run each part on its own:

```bash
python test_heaps.py          # correctness tests
python heapsort.py            # small heapsort demo
python priority_queue.py      # demo of every priority queue operation
python sort_comparison.py     # sorting benchmark (add --quick for small sizes)
python pq_timing.py           # priority queue operation timing
python scheduler.py           # scheduler simulation
```

## Implementation summary

**Heapsort.** The input array is converted to a max-heap from bottom to top (`build_max_heap`, O(n)), after which the root (max element) is moved to the back of the array, the heap size is decreased by one, and the new root is sifting down (`sift_down`, O(log n)). The process is repeated n - 1 times. `sift_down` is implemented using a loop rather than recursion, thus requiring O(1) auxiliary memory.

**Priority Queue.** Heap is implemented as a Python list, with index arithmetic (`parent = (i-1)//2`, `children = 2i+1, 2i+2`). The max-heap is used, as for my scheduler, the larger the number, the more urgent is the task. In case of ties, the tasks are sorted based on their arrival time, followed by task ID. There is also a dictionary that maintains mapping between `task_id` and list index for `increase_key` and `decrease_key` operations.