import pytest

from projects.tts_numbers.exceptions import InvalidInputException
from projects.tts_numbers.tts_numbers import (
    INPUT_CONTAINS_LETTERS,
    INPUT_TOO_LONG,
    MAX_DIGITS,
    pre_process,
    process,
)


class TestPreProcess:
    test_cases = [
        # Format is ("user input", ["expected", "output"])
        ("1234567890", ["1", "234", "567", "890"]),
        ("1,234", ["1", "234"]),
        ("12", ["12"]),
    ]

    @pytest.mark.parametrize("user_input, expected_result", test_cases)
    def test_valid_inputs(self, user_input, expected_result):
        result = pre_process(user_input)
        assert result == expected_result

    test_cases = [
        ("123a123", InvalidInputException, INPUT_CONTAINS_LETTERS),
        ("hello world", InvalidInputException, INPUT_CONTAINS_LETTERS),
        ("1".ljust(MAX_DIGITS + 1, "1"), InvalidInputException, INPUT_TOO_LONG),
    ]

    @pytest.mark.parametrize(
        "user_input, expected_exception, expected_message", test_cases
    )
    def test_invalid_inputs(self, user_input, expected_exception, expected_message):

        with pytest.raises(expected_exception) as raised_exception:
            pre_process(user_input)

        assert str(raised_exception.value) == expected_message


class TestProcess:
    test_cases = [
        (["0"], "zero"),
        (["0000"], "zero"),
        (["1"], "one"),
        (["01"], "one"),
        (["001"], "one"),
        (["001"], "one"),
        (["17"], "seventeen"),
        (["100"], "one hundred"),
        (["114"], "one hundred fourteen"),
        (["160"], "one hundred sixty"),
        (["169"], "one hundred sixty nine"),
        (["1", "000"], "one thousand"),
        (["1", "000", "000"], "one million"),
        (["1", "000", "000", "000"], "one billion"),
        (["1", "000", "234", "000"], "one billion, two hundred thirty four thousand"),
        (["1", "000", "234", "001"], "one billion, two hundred thirty four thousand, one",),
        (["1", "234", "567", "890"], "one billion, two hundred thirty four million, "
                                     "five hundred sixty seven thousand, eight hundred ninety",),
        (["1", "000", "000", "000", "000"], "one trillion"),
    ]

    @pytest.mark.parametrize("user_input, expected_result", test_cases)
    def test_valid_inputs(self, user_input, expected_result):
        result = process(user_input)
        assert result == expected_result
