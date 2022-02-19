"""
Text to speach numbers processor.

Known issues:
 -  If the input ends in "000" the output will end in a comma.  For example "1000" results in "one thousand,"
    See "to do" comment in _process() for details.
 -  Input '0' returns an empty string instead of does not output "zero"
"""

import re
from typing import List, Union

from projects.tts_numbers.exceptions import InvalidInputException

COMMA_NAMES = [
    "hundred",
    "thousand",
    "million",
    "billion",
    "trillion",
]

WORDS = [
    ("", "ten", "",),
    ("one", "eleven", "",),
    ("two", "twelve", "twenty",),
    ("three", "thirteen", "thirty",),
    ("four", "fourteen", "forty",),
    ("five", "fifteen", "fifty",),
    ("six", "sixteen", "sixty",),
    ("seven", "seventeen", "seventy",),
    ("eight", "eighteen", "eighty",),
    ("nine", "nineteen", "ninety",),
]

MAX_DIGITS = len(COMMA_NAMES) * 3
INPUT_CONTAINS_LETTERS = "Invalid Input: Input contains letters."
INPUT_TOO_LONG = f"Input contains too many digits.  Current limit is {MAX_DIGITS}."


# This class is deprecated
def _split_into_list(input_value: str) -> List[str]:
    """
    Breaks the input string into a List[str] where each index holds a block of up to three numbers.
    Example: IN: '12345'    OUT: ['12', '345']
    Example Usage: ','.join(split_into_list('1234567')) outputs `1,234,567'

    :param input_value: A string representation of an integer to be split.
    :return: A List[str] containing the provided number broken into blocks such that joining on
        a comma would be a correct (for North American values of "correct") presentation of the number.
    """

    result = []
    value_as_int: int = int(input_value)
    while value_as_int > 100:
        result.append(value_as_int % 1000)
        value_as_int = int(value_as_int / 1000)
    if value_as_int != 0:
        result.append(value_as_int)

    # Using .append() adds the blocks in the reverse order, so we use [::-1] to reverse the list.
    # Alternatively: replace both instances of .append(foo) above with .insert(0, foo) and drop the [::-1]
    return [str(x) for x in result][::-1]


def _split_string(input_value: str) -> List[str]:
    """
    Exactly the same input and output as above, in a one-liner list comprehension.
    Also: A great example of when not to use comprehensions, but a fun exercise.
    Tip: If it takes more lines to explain the comprehension than it would to write it out another way,
        it's likely a bad time to use comprehensions.

    1. Reverse the input string,
    2. use re.findall to split it into as many groups of three digits as possible and save the rest,
    3. reverse the contents of each group to set them back in the right order,
    4. reverse the order of the groups to put them back in the right order.
    """

    return [group[::-1] for group in re.findall('.{1,3}', input_value[::-1])][::-1]


def _wordify(number: str) -> str:
    """
    Recursively converts the provided string into the word value of the number it represents.
    Example:  IN: '123' OUT: 'one hundred twenty three'

    :param number: A string representation of an integer containing three or fewer digits.
    :return: A string of the provided number spelled out longhand.  ie: 'one hundred twenty three'
    """

    # Pull off and convert the hundreds place if applicable and recursively process the remainder.
    if len(number) == 3:
        return (
            f'{WORDS[int(number[:1])][0]} ' 
            f'{"hundred" if int(number[:1]) != 0 else ""} ' 
            f'{_wordify(number[1:])}'
        ).strip()

    # Pull off and convert the tens place if applicable, then recursively process the remainder if needed.
    elif len(number) == 2:
        # If the tens place is a 1 it's an end-case for the recursion; convert it and start digging out.
        if int(number[:1]) == 1:
            return WORDS[int(number[-1])][1]
        # If the tens place is not a "teen" then get the "tens" value for that number and keep recursing.
        return f'{WORDS[int(number[:1])][2]} {_wordify(number[1:])}'.strip()

    # Convert the ones place and end the recursion.
    else:
        return WORDS[int(number)][0]


def pre_process(input_value: Union[str, int]) -> List[str]:
    """
    Validates and sanitizes input values then splits the provided string into a List[str].

    :param input_value: Sn integer or a string value representing an integer.
    :return: A List[str] containing the provided number broken into blocks such that joining on
        a comma would be a correct (for North American values of "correct") presentation of the number.
    """
    if re.findall("[a-zA-Z]", input_value):
        raise InvalidInputException(INPUT_CONTAINS_LETTERS)

    if re.findall("[^0-9,]", input_value):
        # Alternatively, we could throw an exception here if that is the preferred result.
        print("Input contains punctuation characters, they will be ignored.")

    # Remove any non-digit characters
    sanitized_value: str = re.sub("[^0-9]", "", str(input_value))

    if len(sanitized_value) > MAX_DIGITS:
        raise InvalidInputException(INPUT_TOO_LONG)

    # Split into a list of three-digits batches
    return _split_string(sanitized_value)


def _process(input_value: List[str], _comma_count: int = 0) -> str:
    """
    Converts a List[str] containing [0-3] digits per entry into the longform version of the number.
    Example: IN: ['1', '234']   OUT: 'one thousand,two hundred thirty four'

    :param input_value: A List[str] containing the provided number broken into blocks such that joining on
        a comma would be a correct (for North American values of "correct") presentation of the number.
    :param _comma_count: Used to get the correct unit (thousand, million, billion, etc)
    :return: A string of the provided list spelled out.
    """

    # TODO: The last part of this will append a comma if the current block isn't all zeros and the
    #       input is over a thousand, but I have not yet figured out how to not append a comma if
    #       all following blocks are "000" as well, for example 1000000 should not end in a comma.
    if len(input_value) > 0:
        end_section = input_value.pop()
        return (
            f'{_process(input_value, _comma_count + 1)} '
            f'{_wordify(end_section)} '
            f'{COMMA_NAMES[_comma_count] if _comma_count and int(end_section) else ""}'
            f'{"," if end_section != "000" and _comma_count else ""}'
        ).strip()
    return ""


def process(input_value: List[str]) -> str:
    """
    An ugly kludge to work around the errant trailing comma noted in _process() and
        for not accounting for zero in my initial design.
    """
    if input_value and all(int(group) == 0 for group in input_value):
        return "zero"
    result = _process(input_value)
    return result[:-1].strip() if result[-1:] == ',' else result


if __name__ == "__main__":
    user_input: str = ""

    while user_input.lower() != 'q':
        user_input = input("Enter a number to wordify or Q to quit: ")
        if user_input.lower() == 'q':
            break
        elif user_input == '':
            continue
        try:
            preprocessed = pre_process(user_input)
        except ValueError as e:
            print(e)
            continue
        print(f'Commafied: {",".join(preprocessed)}')
        processed = process(preprocessed)
        print(f'Processed: {processed}')
