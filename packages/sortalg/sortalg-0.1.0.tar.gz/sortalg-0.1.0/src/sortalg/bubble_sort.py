from itertools import repeat
import random


def bubble_sort(arr):
    arr = arr.copy()
    last_index = len(arr) - 1
    for pas in range(last_index, 0, -1):
        for i in range(pas):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
    return arr


if __name__ == "__main__":
    arr = [random.randint(1, 20000000) for _ in repeat(None, 1000)]
    sarr = bubble_sort(arr)
    print(sarr == sorted(arr))
