import pytest

from projects.bracket_match.bracket_match import process_string


class TestBracketMatch:
    test_cases = [
        ("", True),
        ("[]", True),
        ("(banana)", True),
        ("[{fish}(banana?)]", True),
        ("[fish(banana[app.le])]", True),
        ("[", False),
        ("][", False),
        ("[{banana]", False),
        ("{[}]", False),
    ]

    @pytest.mark.parametrize("value, expected_result", test_cases)
    def test_bracket_match(self, value, expected_result):
        assert process_string(value) == expected_result
