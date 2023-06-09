from typing import Set, Dict, List
import re


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


def flatten(obj):
    if isinstance(obj, list):
        return obj
    ret = list()
    for entry in obj:
        ret += obj[entry]
    return ret


def logs_to_dict(filename) -> Dict[str, List[str]]:
    ret = dict()
    with open(f'{filename}.txt', 'r') as file:
        for line in file:
            line = line.rstrip()
            if line.startswith("# TYPE"):
                metric = line.split(" ")
                if metric[-2].startswith('airflow'):
                    name = metric[-2]
                    typ = metric[-1]
                    ret[typ] = ret.get(typ, []) + [name]
    return ret


def parse_expected(filename) -> Set[str]:
    with open(f'expected_{filename}.txt', 'r') as file:
        return {metric.rstrip() for metric in file}


def expected_to_dict():
    _expected = dict()
    _expected_list = []
    for typ in ['counters', 'gauges', 'timers']:
        _expected[typ] = parse_expected(typ)
        _expected_list += _expected[typ]
    return _expected, _expected_list


def list_to_regex(obj):
    ret = list()
    for item in obj:
        for char in ['.', '-']:
            item = item.replace(char, '_')
        if "<" in item:
            substring = re.findall('(<.*?>)', item)
            for match in substring:
                item = item.replace(match, f'(?P{match}.*)')
        item = f'^airflow_{item}$'
        ret.append(re.compile(item))
    return ret


def find_missing(found, expected):
    # for each pattern
    #   if that pattern does not match any stat
    #       log that stat
    missing = set()
    for pattern in expected:
        if not any(matches := [re.match(pattern, stat) for stat in flatten(found)]):
            missing.add(pattern.pattern[1:-1])
    return missing


def ss(obj):
    return set(sorted(obj))


def back_to_dict(obj, master):
    ret = {}
    for stat in obj:
        typ = [typ for typ in master.keys() if stat in master[typ]][0]
        ret[typ] = ret.get(typ, []) + [stat]
    for typ in ret:
        ret[typ].sort()
    return ret


if __name__ == '__main__':
    otel = logs_to_dict('otel')
    statsd = logs_to_dict('statsd')
    expected_dict, expected_list = expected_to_dict()
    expected_pattern_dict = {}

    expected_patterns = list_to_regex(expected_list)
    for typ in expected_dict:
        expected_pattern_dict[typ] = {pattern.pattern[1:-1] for pattern in list_to_regex(set(expected_dict[typ]))}

    otel_missing: Set = ss(find_missing(otel, expected_patterns))
    statsd_missing: Set = ss(find_missing(statsd, expected_patterns))

    both_missing = back_to_dict(otel_missing.intersection(statsd_missing), expected_pattern_dict)
    only_otel_missing = back_to_dict(otel_missing - statsd_missing, expected_pattern_dict)
    only_statsd_missing = back_to_dict(statsd_missing - otel_missing, expected_pattern_dict)

    # pprint('Otel Missing', otel_missing)
    # pprint('Statsd Missing', statsd_missing)
    ppprint('Listed on the Airflow metrics page but not found in either output', both_missing)
    ppprint('Missing from OTel but found in StatsD', only_otel_missing)
    ppprint('Missing from StatsD but found in OTel', only_statsd_missing)


    ppprint('Found in OTel', otel)
    ppprint('Found in StatsD', statsd)