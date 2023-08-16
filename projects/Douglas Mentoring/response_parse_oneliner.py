from result import result

MODEL_LINE_PREFIX: str = "Vendor Name"
SPEED_LINE_PREFIX: str = "Administrative Speed"

"""
These two lines have the same result as the _parse_response_data() method in day1_rewrite.py.
Instead of getting the data from send_command(), I'm importing it from result.py so you can 
actually run it and see that it's not just gibberish. :P  The `data = ` line is what is called a 
"dictionary comprehension".  Super powerful, and often super confusing.  Don't use this kind of 
thing when someone else may need to read your code, but once you learn them they are really fun 
to play with.

Line 29 does all the following in one command:

create a new dictionary named data
for each line in result:
    if the line starts with MODEL_LINE_PREFIX or SPEED_LINE_PREFIX:
        add an entry to the dictionary with the matching PREFIX as key and the rest of the line as the value


Then line 30 pulls those two values out of the dictionary and returns them as a tuple. 

Of course, when it takes more lines to explain it than to do it, you are likely something it wrong.
"""


def _parse():
    data = {line.split(":")[0].strip() : line.split(":")[1].strip() for line in result.splitlines() if line.startswith((MODEL_LINE_PREFIX, SPEED_LINE_PREFIX))}
    return data[MODEL_LINE_PREFIX], data[SPEED_LINE_PREFIX]


model, speed = _parse()
print(f'Model: {model}')
print(f'Speed: {speed}')
