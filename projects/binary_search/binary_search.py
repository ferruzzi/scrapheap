"""
Implement a binary search that can account for a rotated sorted list.
"""

from typing import List, Optional, TypeVar

T = TypeVar("T")


def binary_search(values: List[T], target: T, min: int = 0, max: int = None) -> T:
    max = max if max is not None else len(values) -1

    if min > max or not len(values) or target > values[max] or target < values[min]:
        return None

    mid: int = (min + max) // 2
    if values[mid] == target:
        return mid
    return (
        binary_search(values, target, min, mid - 1)
        if values[mid] > target
        else binary_search(values, target, mid + 1, max)
    )


if __name__ == "__main__":
    inputs = [
        ([1, 2, 3, 4, 5, 6, 7], 3),
    ]

    for inp in inputs:
        print(f'{inp[1]} is at index {binary_search(*inp)} of input {inp[0]}')
