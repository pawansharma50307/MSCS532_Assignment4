def sift_down(arr, heap_size, i):
    """
    Keep on moving arr[i] down the heap till the max-heap property is restored.

    Only arr[0 .. heap_size-1] should be considered the heap. All elements after 
    heap_size are sorted already and will remain untouched.

    """
    while True:
        largest = i
        left = 2 * i + 1
        right = left + 1

        if left < heap_size and arr[left] > arr[largest]:
            largest = left
        if right < heap_size and arr[right] > arr[largest]:
            largest = right

        if largest == i:
            # arr[i] is already bigger than both children, so we are done
            return

        arr[i], arr[largest] = arr[largest], arr[i]
        i = largest


def build_max_heap(arr):
    """
    Construct a heap from arr using the bottom-up approach.

    Leaves (indices n//2 .. n-1) are already heaps of size 1; we will
    begin with the last non-leaf element and perform sift down operations
    towards the root. Although we have roughly n/2 sift_down calls, the majority
    of them occur in the bottom part of the tree and thus cost almost nothing.
    That’s the reason for the O(n) complexity and not O(n log n).
    """
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        sift_down(arr, n, i)


def heapsort(arr):
    """
    Sort array arr in ascending order, in-place.
 
    Time Complexity:   O(n log n), worst / average / best (if all keys are different)
    Space Complexity:  O(1), auxiliary (only a few index variables)
    Not stable:       Same elements might be re-ordered.
    """
    n = len(arr)
    build_max_heap(arr)

    # arr[0] is always the largest element left in the heap.
    # Swap it to the end, then fix the (now smaller) heap.
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        sift_down(arr, end, 0)

    return arr


def is_max_heap(arr, heap_size=None):
    """Helper used for the test: True if arr[0:heap_size] is a valid max-heap."""
    if heap_size is None:
        heap_size = len(arr)
    for i in range(heap_size // 2):
        left = 2 * i + 1
        right = left + 1
        if left < heap_size and arr[i] < arr[left]:
            return False
        if right < heap_size and arr[i] < arr[right]:
            return False
    return True


if __name__ == "__main__":
    # small demo
    data = [4, 10, 3, 5, 1, 8, 7, 2, 9, 6]
    print("Original list:     ", data)

    heap = list(data)
    build_max_heap(heap)
    print("After build_max_heap:", heap, "| valid max-heap:", is_max_heap(heap))

    result = heapsort(list(data))
    print("After heapsort:    ", result)
