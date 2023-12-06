import os
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt

BASE_PATH = os.path.dirname(__file__)
REGIONS_PATH = "regions/"
ROADS_PATH = "roads/"
LANDMARKS_PATH = "landmarks.csv"

ANNOTATE_OFFSET = 15

x_type = int
y_type = int
description_type = str

RegionInputLineFormat = Tuple[x_type, y_type]
RoadInputLineFormat = Tuple[x_type, y_type]
LandmarkInputLineFormat = Tuple[x_type, y_type, description_type]

LEGEND_DEFAULTS = {
    "shadow": True,
    "facecolor": "#D3D3D3",
}


def style_legend_title(title) -> None:
    # title.set_color("red")
    title.set_fontsize(15)
    title.set_weight("bold")


def snake_to_title(string) -> str:
    return string.replace('_', ' ').title()


def file_path_to_region(file_path) -> str:
    filename = os.path.basename(file_path)
    raw_region_name = os.path.splitext(filename)[0]
    return snake_to_title(raw_region_name)


def parse_file(path) -> list:
    result = []
    with open(path) as f:
        for line in f:
            data = line.split(",")
            try:
                point = (x_type(data[0]), y_type(data[1]))
                if len(data) == 3:
                    point += (data[2].strip(),)
                result.append(point)
            except ValueError as ex:
                # Ignore a blank line
                if "invalid literal for int() with base 10: '\\n'" in ex.args[0]:
                    continue
                else:
                    print(f"Skipping data point, values are not valid coordinates: {line}")

    return result


def parse_dir(dir_path) -> Dict[str, list]:
    result: Dict[str, list] = {}

    dir = os.path.join(BASE_PATH, dir_path)
    for file in os.listdir(dir):
        file_path = os.path.join(dir, file)
        if os.path.isfile(file_path):
            entry = file_path_to_region(file_path)
            print(f"Loading data for {entry} from {file}")
            result[entry] = parse_file(file_path)

    return result


def get_landmarks() -> List[LandmarkInputLineFormat]:
    landmark_path = os.path.join(BASE_PATH, LANDMARKS_PATH)
    return parse_file(landmark_path)


def plot_regions(entries) -> None:
    for entry in entries:
        plt.fill(
            "x",
            entry,
            data={
                "x": [point[0] for point in entries[entry]],
                entry: [point[1] for point in entries[entry]],
            },
        )

        legend = plt.legend(loc=2, title="Regions", **LEGEND_DEFAULTS)
        style_legend_title(plt.gca().get_legend().get_title())

        plt.gca().add_artist(legend)


def plot_roads(entries) -> None:
    for entry in entries:
        plt.plot(
            [point[0] for point in entries[entry]], [point[1] for point in entries[entry]],
            label=entry,
            linewidth=2
        )

    lines = plt.gca().get_lines()
    legend = plt.legend(
        [lines[i] for i in range(len(lines))], [lines[i].get_label() for i in range(len(lines))],
        loc=1,
        title="Roads and Rails",
        **LEGEND_DEFAULTS
    )
    style_legend_title(plt.gca().get_legend().get_title())

    plt.gca().add_artist(legend)


def plot_landmarks(landmarks) -> None:
    points = {snake_to_title(point[2]): [point[0], point[1]] for point in landmarks}

    for point in points:
        x = points[point][0]
        y = points[point][1]
        plt.scatter(x=x, y=y, c="black", label=point)
        plt.annotate(point, (x, y), (x + ANNOTATE_OFFSET, y + ANNOTATE_OFFSET))


if __name__ == "__main__":
    plt.figure(figsize=(20,10))

    regions: Dict[str, list] = parse_dir(REGIONS_PATH)
    roads = parse_dir(ROADS_PATH)
    landmarks = get_landmarks()

    plot_regions(regions)
    plot_roads(roads)
    plot_landmarks(landmarks)

    # Minecraft uses an odd coordinate system (X, Z, -Y) which requires Y to be inverted
    plt.subplot().invert_yaxis()

    plt.show()
