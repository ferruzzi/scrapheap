from enum import Enum
import yaml


class MetricType(Enum):
    counter = 'counter'
    up_down_counter = 'up_down_counter'
    gauge = 'gauge'
    timer = 'timer'


input = {}


def create(name):
    metric_data = dict()
    try:
        metric_data = input[name]
    except KeyError:
        print(f"No entry for {name}.")
        return
    metric_type = MetricType[metric_data['type']]
    if metric_type == MetricType.gauge:
        print(f'{name} is a gauge!')
    elif metric_type == MetricType.counter:
        is_monotonic = 'monotonic' if metric_data['is_monotonic'] else 'non-monotonic'
        print(f'{name} is a {is_monotonic} counter.')
    else:
        print(f'Can not create unknonwn metric type {metric_type}.')


if __name__ == "__main__":
    with open("input.yaml", "r") as stream:
        input = yaml.safe_load(stream)
        metric_names = [*list(input.keys()), 'garbage']
        for name in metric_names:
            create(name)
    #     print(metrics)
    #     print(metrics['apples']['unit'])
    #
    # for metric in metrics.values():
    #     print(metric['description'])

