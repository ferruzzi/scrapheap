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
    metrics_with_no_match = sorted({metric.name for metric in metrics_map.values() if not metric.matches})
    only_in_statsd_but_too_long = sorted({metric for metric in statsd_only if len(metric) > 63})
    only_in_statsd_and_not_too_long = sorted({metric for metric in statsd_only if len(metric) <= 63})

    ppprint('In StatsD but not in Otel:',  only_missing_from_otel, print_len=True)
    import pdb ; pdb.set_trace()
