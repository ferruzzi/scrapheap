"""
Write a method/function that assesses the bracket matching of a string. It should succeed in cases where brackets are balanced and matching.
Write this as production level code in a language of your choice
E.g. pass cases: "[]", "(banana)", "[{fish}(banana?)]", "[fish(banana[app.le])]"
E.g. fail cases: "[" , "][", "[{banana]", "{[}]"
"""

BRACKET_SETS = {
    ']': '[',
    '}': '{',
    ')': '(',
}


def process_string(string: str) -> bool:
    """
    Returns True if every opening bracket has a corresponding closing bracket in the correct order.
    """
    if len(string) < 1:
        return True

    brackets_found = []

    for character in string:
        if character in BRACKET_SETS.values():
            brackets_found.append(character)
        if character in BRACKET_SETS.keys():
            try:
                last_bracket = brackets_found.pop()
            except IndexError:
                return False
            if last_bracket != BRACKET_SETS[character]:
                return False
    return len(brackets_found) == 0


if __name__ == "__main__":
    inputs = [
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

    for i, expected in inputs:
        result = process_string(i)
        print(f'Input: {i} should be {expected} and returned {result}.')
        assert result == expected
