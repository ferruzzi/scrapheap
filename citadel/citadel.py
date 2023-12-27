import json
import os
import re
from typing import Dict, List, Set

pattern = re.compile(r'(?P<family>.*): (?P<type>.*): (?P<color>.*?) \(')
SCRAPE_LOCATION = 'scrapes'

paint_by_family: Dict[str, Set[str]] = {}
paint_by_type: Dict[str, Set[str]] = {}
family_by_paint: Dict[str, str] = {}
color_names: Set = set()


def ppprint(header, data, print_len=False, indent=False):
    prefix = '\t'if indent else ''
    prefix += str(len(data))+' ' if print_len else ''
    print(f"{prefix}{header}")
    if isinstance(data, dict):
        for key in data.keys():
            ppprint(key, data[key], True, True)
    else:
        prefix = '\t\t' if indent else '\t'
        print(prefix + f"\n{prefix}".join(data) + "\n")


def pprint(data):
    keys = sorted(list(data.keys()))
    prefix = '\n'
    for key in keys:
        value = data[key] if isinstance(data[key], str) else prefix.join(data[key])
        print(f"{key}\t{value}")


def get_families():
    files = list(os.walk(SCRAPE_LOCATION))[0][2]
    return [_file.split('.')[0] for _file in files]


def verify():
    _families = get_families()
    assert len(_families) == len(paint_by_family)
    for family in _families:
        assert family in [fam.lower() for fam in paint_by_family.keys()]


def format_name(color, entry):
    raw_name = entry['attributes']['product.displayName'][0]
    formatted_name = raw_name.replace("Spray UK/ROW ", "").replace("Citadel ", "")
    return f"{color.capitalize()}: {formatted_name}"


def parse_files():
    ret = []
    for color in families:
        try:
            with open(f'{SCRAPE_LOCATION}/{color}.json', 'r') as file:
                contents = json.load(file)['contents'][0]['records']
                for entry in contents:
                    format_name(color, entry)
                names = [format_name(color, entry) for entry in contents]

                ret += names

        except FileNotFoundError:
            print(f"JSON file not found for color '{color}'.")
    print(f'Found {len(ret)} colors in {len(families)} color families.')
    return ret


def parse_data():
    global color_names

    for line in raw_colors:
        try:
            (_family, _type, _name) = re.findall(pattern, line)[0]
            paint_by_type[_type] = {*paint_by_type.get(_type, {}), _name}
            paint_by_family[_family] = {*paint_by_family.get(_family, {}), _name.rstrip()}
            family_by_paint[_name] = _family
            color_names.add(_name)
        except IndexError:
            print(f'Error parsing `{line}`.  Skipping.')

    color_names = sorted(color_names)


if __name__ == "__main__":
    families = get_families()
    raw_colors = parse_files()
    parse_data()
    verify()

    print()
    # ppprint("Paint By Type", paint_by_type)
    # pprint(paint_by_family)

    pprint(family_by_paint)
