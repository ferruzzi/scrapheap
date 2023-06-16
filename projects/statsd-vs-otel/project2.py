from __future__ import annotations

import re
from collections import namedtuple
from typing import List, Dict, Set

Expected = namedtuple('Expected', 'example pattern')

# GLOBALS
metrics_map: Dict[str, Metric] = {}
pattern_map: Dict[Expected, Set[Metric]] = {}
expected_metrics: Dict[str, Set[Expected]] = {}
expected_by_name: Dict[str, Expected] = {}
expected_by_pattern: Dict[str, Expected] = {}


def ppprint(header, data, print_len=False, indent=False, print_type=False):
    prefix = '\t'if indent else ''
    prefix += str(len(data))+' ' if print_len else ''
    print(f"{prefix}{header}")
    if isinstance(data, dict):
        for key in data.keys():
            ppprint(key, data[key], True, True, print_type)
    else:
        prefix = '\t\t' if indent else '\t'
        if print_type:
            data = {f'{type_from_name(entry).ljust(10)} : {entry}' for entry in data}
        print(prefix + f"\n{prefix}".join(sorted(data)) + "\n")


def type_from_name(name):
    return [i for i in expected_metrics if expected_by_name[name[8:]] in expected_metrics[i]][0]


class Metric:
    def __init__(self, name, instrument, source=None):
        self.name: str = name
        self.instrument_type: str = instrument
        self.is_in_otel: bool = False
        self.is_in_statsd: bool = False
        self.matches: List[str] = list()

        if source:
            self.update_source(source)

    def found_in_otel(self):
        self.is_in_otel = True

    def found_in_statsd(self):
        self.is_in_statsd = True

    def matched(self, pattern):
        self.matches.append(pattern)

    def update_source(self, found_in):
        getattr(self, f"found_in_{found_in}")()


def parse_logs(filename):
    with open(f'{filename}.txt', 'r') as file:
        for line in file:
            if line.startswith("# TYPE"):
                name, instrument = line.rstrip().split(" ")[-2:]
                if name.startswith('airflow'):
                    if name in metrics_map.keys():
                        metrics_map[name.lower()].update_source(filename)
                    else:
                        metrics_map[name.lower()] = Metric(name.lower(), instrument, filename)


def patternify(_item):
    item = _item
    for char in ['.', '-']:
        item = item.replace(char, '_')
    if "<" in item:
        substring = re.findall('(<.*?>)', item)
        for match in substring:
            item = item.replace(match, f'(?P{match}.*)')
    return f'^airflow_{item}$'


def parse_expected():
    global expected_by_name
    global expected_by_pattern

    def parse(filename) -> Set[Expected]:
        with open(f'expected_{filename}.txt', 'r') as file:
            return {Expected(line.rstrip(), patternify(line.rstrip())) for line in file}
            # return {line.rstrip() for line in file}

    expected_stats = dict()
    for instrument in ['counters', 'gauges', 'timers']:
        expected_stats[instrument] = parse(instrument)
        expected_by_name.update(
            {expected.example: Expected(expected.example, expected.pattern) for expected in expected_stats[instrument]}
        )
        expected_by_pattern.update(
            {expected.pattern: Expected(expected.example, expected.pattern) for expected in expected_stats[instrument]}
        )
    return expected_stats


def match_patterns(patterns):
    for key in patterns.keys():
        for pattern in {entry.pattern for entry in patterns[key]}:
            matched_names = {name for name in metrics_map.keys() if re.match(pattern, name)}
            for name in matched_names:
                metrics_map[name].matched(pattern)


def flattened(obj):
    flat = list()
    for key in obj.keys():
        flat += obj[key]
    return flat


def build_pattern_map():
    for _metric in metrics_map.values():
        for pattern in _metric.matches:
            metrics: Set = pattern_map.get(expected_by_pattern[pattern], set())
            metrics.add(_metric)
            pattern_tuple = [p for p in flattened(expected_metrics) if p.pattern == pattern][0]
            pattern_map[pattern_tuple] = metrics


if __name__ == '__main__':
    # SETUP
    for log in ['otel', 'statsd']:
        parse_logs(log)
    expected_metrics = parse_expected()
    match_patterns(expected_metrics)
    build_pattern_map()

    # Comparisons
    statsd_includes = sorted({metric.name for metric in metrics_map.values() if metric.is_in_statsd})
    statsd_missing = sorted({f'airflow_{expected.example}' for expected in flattened(expected_metrics) if not (expected in pattern_map.keys() and any({metrics_map[match.name].is_in_statsd for match in pattern_map[expected]}))})
    statsd_only = sorted({metric.name for metric in metrics_map.values() if metric.is_in_statsd and not metric.is_in_otel})

    otel_includes = sorted({metric.name for metric in metrics_map.values() if metric.is_in_otel})
    otel_missing = sorted({f'airflow_{expected.example}' for expected in flattened(expected_metrics) if not (expected in pattern_map.keys() and any({metrics_map[match.name].is_in_otel for match in pattern_map[expected]}))})
    otel_only = sorted({metric.name for metric in metrics_map.values() if metric.is_in_otel and not metric.is_in_statsd})

    only_missing_from_otel = sorted({missing for missing in otel_missing if missing not in statsd_missing})
    metrics_not_matching_a_pattern = sorted({metric.name for metric in metrics_map.values() if not metric.matches})

    not_in_either = set()
    for instrument in expected_metrics.keys():
        for target in expected_metrics[instrument]:
            if not any({target.pattern in metrics_map[metric].matches for metric in metrics_map}):
                not_in_either.add(f'airflow_{target.example}')
    not_in_either = sorted(not_in_either)

    if_cthulhu_wrote_not_in_either_when_he_was_grumpy = sorted([item for sublist in [[f'airflow_{target.example}' for target in expected_metrics[instrument] if not any({target.pattern in metrics_map[metric].matches for metric in metrics_map})] for instrument in expected_metrics.keys()] for item in sublist])
    assert if_cthulhu_wrote_not_in_either_when_he_was_grumpy == not_in_either

    only_in_statsd_but_too_long = sorted({metric for metric in statsd_only if len(metric) > 62})
    only_in_statsd_and_not_too_long = sorted({metric for metric in statsd_only if len(metric) <= 62})

    ppprint('Found in Otel', otel_includes, print_len=True)
    ppprint('Found in StatsD', statsd_includes, print_len=True)

    ppprint('Missing from OTel', otel_missing, print_len=True)
    ppprint('Missing from StatsD', statsd_missing, print_len=True)

    ppprint('Emitted but not matching a pattern', metrics_not_matching_a_pattern, print_len=True)
    ppprint('Patterns Generated', sorted(expected_by_pattern.keys()), print_len=True)

    ppprint('In StatsD but not in Otel',  only_missing_from_otel, print_type=True, print_len=True)
    ppprint('Not found in either output', not_in_either, print_len=True, print_type=True)

    ppprint('Only in StasD but too long', only_in_statsd_but_too_long, print_len=True)
    ppprint('Expected', sorted(expected_by_name.keys()), print_len=True)
    # import pdb ; pdb.set_trace()
