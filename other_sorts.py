"""
Both Quicksort and Merge Sort were used solely for the purpose of comparison with Heap Sort in sort_comparison.py.
"""

import random


# Quicksort
def _hoare_partition(arr, lo, hi):
    """
    Partition array arr[lo..hi] about a randomly selected pivot.

    Function returns index j such that all elements in arr[lo..j] are <= pivot 
    and all elements in arr[j+1..hi] are >= pivot. lo <= j < hi, which means
    that both halves are smaller than the original interval.
    """
    p = random.randint(lo, hi)
    arr[lo], arr[p] = arr[p], arr[lo]
    pivot = arr[lo]

    i = lo - 1
    j = hi + 1
    while True:
        i += 1
        while arr[i] < pivot:
            i += 1
        j -= 1
        while arr[j] > pivot:
            j -= 1
        if i >= j:
            return j
        arr[i], arr[j] = arr[j], arr[i]


def _quicksort(arr, lo, hi):
    while lo < hi:
        p = _hoare_partition(arr, lo, hi)
        # recurse on the smaller part, keep looping on the larger part
        if p - lo < hi - p:
            _quicksort(arr, lo, p)
            lo = p + 1
        else:
            _quicksort(arr, p + 1, hi)
            hi = p


def quicksort(arr):
    """Sort arr in place (ascending) and return it."""
    _quicksort(arr, 0, len(arr) - 1)
    return arr


# Merge Sort
def _merge(left, right):
    result = []
    i = j = 0
    len_left, len_right = len(left), len(right)

    while i < len_left and j < len_right:
        # <= keeps it stable (equal items from the left half go first)
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # one of these will be empty
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(arr):
    """Returns a new list that is sorted in ascending order."""
    if len(arr) <= 1:
        return list(arr)
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


if __name__ == "__main__":
    data = [5, 2, 9, 1, 5, 6, 3, 8, 7, 4]
    print("Original:  ", data)
    print("Quicksort: ", quicksort(list(data)))
    print("Merge sort:", merge_sort(data))
