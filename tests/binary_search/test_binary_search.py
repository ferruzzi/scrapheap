import pytest

from projects.binary_search.binary_search import binary_search


class TestFirstUnique:
    test_cases = [
        ([1, 2, 3, 4, 5, 6, 7], 4, 3),
        ([1, 2, 3, 4, 5, 6, 7], 3, 2),
        ([1, 2, 3, 4, 5, 6, 7], 1, 0),
        ([1, 2, 3, 4, 5, 6, 7], 7, 6),
        ([1], 1, 0),
        ([1], 9, None),
        ([1], -2, None),
        ([], 1, None),
    ]

    @pytest.mark.parametrize("values, target, expected_result", test_cases)
    def test_binary_search(self, values, target, expected_result):
        result = binary_search(values, target)
        assert result == expected_result
