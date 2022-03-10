import pytest

from projects.first_unique.first_unique import first_unique


class TestFirstUnique:
    test_cases = [
        (['a', '1', 'c', '1', 'a', 'a', 'd', '1'], 'c'),
        (['a', 'a'], None),
        ([], None),
        (['b'], 'b'),
        (['b', 1, 'b', 1], None),
        (['b', 1, 'b'], 1),
        (['b', ['b'], 'b'], ['b']),
    ]

    @pytest.mark.parametrize("user_input, expected_result", test_cases)
    def test_first_unique(self, user_input, expected_result):
        result = first_unique(user_input)
        assert result == expected_result
