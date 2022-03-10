"""
Given an array, return the first unique element.
  For example, given the array: a, 1, c, 1, a, a, d, 1
  Your method should output: c

What if this was a stream of data with no end?
  How would your solution change to return the _current_ first unique element when polled?
"""

from typing import List, Optional, TypeVar, Dict

T = TypeVar('T')


def first_unique(input_list: List[T], find: T = None) -> T:
    if len(input_list) == 0:
        return None
    if input_list.count(input_list[0]) > 1:
        return first_unique([x for x in input_list if x != find], input_list[0])
    return input_list[0]


def first_unique_map(input_list: List[T]) -> T:
    if len(input_list) == 0:
        return None
    result: Dict[T, int] = {}
    for value in input_list:
        result[value] = result.get(value, 0) + 1

    for value in input_list:
        if result[value] == 1:
            return value


if __name__ == "__main__":
    inputs = [
        ['a', '1', 'c', '1', 'a', 'a', 'd', '1'],
        ['a', 'a'],
        [],
        ['b'],
    ]

    for input_list in inputs:
        print(f'Input: {input_list}')
        print(f'\tRecursive Solution: {first_unique(input_list)}')
        print(f'\tMap Solution: {first_unique_map(input_list)} \n')
