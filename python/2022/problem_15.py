"""
Day 15: Beacon Exclusion Zone

In this problem we are given the locations of sensors and the closest beacon to the
sensor. Sensors can only lock onto a single beacon.

In the first part, we are given a particular row (y-position) and need to determine the
number of positions along it which could not contain a beacon.

For part two, we want to determine the location of a missing beacon, that is not being
detected by any sensor. We are given some bounds that can be used to limit the search.
"""

import re
from typing import Iterator, Tuple, Union

import aoc

# Describes a two-dimensional point.
Point = Tuple[int, int]


def distance(p1: Point, p2: Point) -> int:
    """Return the Manhattan distance between two points."""

    (x1, y1) = p1
    (x2, y2) = p2
    return abs(x1 - x2) + abs(y1 - y2)


class Sensor:
    def __init__(self, *, position, beacon):
        self.position = position
        self.beacon = beacon

        # Compute the range of the sensor.
        self.range = distance(position, beacon)


def bounding_box(sensors: list[Sensor]) -> Tuple[Point, Point]:
    """Return a pair of points defining the bounding box for the sensors."""

    beacons = [sensor.beacon for sensor in sensors]

    x_vals = [x for (x, _) in beacons]
    y_vals = [y for (_, y) in beacons]

    p1 = (min(x_vals), min(y_vals))
    p2 = (max(x_vals), max(y_vals))

    return (p1, p2)


def parse(input: str) -> list[Sensor]:
    """Generate a list of sensors and their nearest beacon."""

    lines = input.split("\n")

    # Create a regex to extract the sensor and beacon positions.
    pattern = re.compile(
        r"Sensor at x=([0-9-]+), y=([0-9-]+): closest beacon is at x=([0-9-]+), y=([0-9-]+)"
    )

    sensors = []

    for line in lines:
        (x1, y1, x2, y2) = map(int, pattern.search(line).groups())

        # Create and add a new sensor object.
        sensor = Sensor(position=(x1, y1), beacon=(x2, y2))
        sensors.append(sensor)

    return sensors


@aoc.solution(part=1)
def part_one(input: str, *, row: int) -> int:
    """Find the number of positions in the given row that cannot contain a beacon."""

    # Parse the puzzle and generate the list of beacons.
    sensors = parse(input)

    # Helper function to determine if a sensor is within range of the specified row. To
    # help speed up the calculation we only consider sensors which could possibly scan the
    # points in the row.
    in_range = (
        lambda s: s.position[1] + s.range >= row and s.position[1] - s.range <= row
    )

    # Determine the min and max x-values for the sensors' ranges.
    sensors = [sensor for sensor in sensors if in_range(sensor)]

    # NOTE: The min and max values are possibly less than (or greater than) necessary. To
    #   generate exact bounds for the row we would need to consider the y-offset of the
    #   sensor.
    x_min = min(sensor.position[0] - sensor.range for sensor in sensors)
    x_max = max(sensor.position[0] + sensor.range for sensor in sensors)

    # To find the positions which could not contain a becon we check each point
    # along the row and see if it is within range of one of the scanners. Since the
    # scanners automatically lock on to the closest beacon, we know that any point
    # within this range cannot contain a beacon (otherwise it would be the closest
    # becon and the sensor would have locked on to it).
    points = [
        (x, row) for x in range(x_min, x_max + 1) if is_scannable(sensors, (x, row))
    ]

    # Find any beacons which may lie on the row.
    beacons = set([sensor.beacon for sensor in sensors if sensor.beacon[1] == row])

    # Compute the total number of in-range positions that are not beacons.
    return len(points) - len(beacons)


def is_scannable(sensors: list[Sensor], point: Point) -> bool:
    """Check whether the position is within scanning range of any of the sensors."""

    for sensor in sensors:
        if distance(sensor.position, point) <= sensor.range:
            return True

    return False


def tuning_frequency(beacon: Point) -> int:
    """Calculate the tuning frequency for the beacon."""

    (x, y) = beacon
    freq = x * 4_000_000 + y
    return freq


@aoc.solution(part=2)
def part_two(input: str, *, max_coord: int) -> Union[int, None]:
    """Locate the position of the distress beacon."""

    # Parse the puzzle data and generate the list of sensors.
    sensors = parse(input)

    # We know that there is only one point where the distress beacon could be located. we
    # also know that it is outside the range of all our sensors (otherwise, we would know
    # its location). So to find the missing beacon we check the perimetor of all our
    # sensors (in this case the perimeter is all the points that lie one space beyond the
    # sensor's range). The beacon's position will then be the one, unique perimeter
    # position that is not within scanning range of any other beacon.
    for sensor in sensors:
        # Check the sensor's perimeter for an un-scannable posititon. Because the location
        # is unique we can return as soon as we find a solution.
        if point := check_sensor(sensors, sensor, max_coord=max_coord):
            return tuning_frequency(point)

    return None


def check_sensor(
    sensors: list[Sensor], target_sensor: Sensor, *, max_coord: int
) -> Union[Point, None]:
    """Check for a point along the sensor's perimeter that is not scannable by the other
    sensors.
    """

    for point in perimeter(target_sensor, max_coord):
        if not is_scannable(sensors, point):
            return point

    return None


def perimeter(sensor: Sensor, max_coord: int) -> Iterator[Point]:
    """Return a generator for points that lie along the (outer) perimeter of a sensor."""

    (x, y) = sensor.position

    is_valid = lambda p: 0 <= p[0] <= max_coord and 0 <= p[1] <= max_coord

    for i in range(sensor.range + 1):
        dx = sensor.range - i
        dy = i + 1

        points = [
            (x + dx, y + dy),
            (x - dx, y + dy),
            (x + dx, y - dy),
            (x - dx, y - dy),
        ]

        for point in points:
            if is_valid(point):
                yield point


PROGRAM_ARGS = {"part_one": {"row": 2_000_000}, "part_two": {"max_coord": 4_000_000}}

if __name__ == "__main__":
    input = aoc.get_input(2022, 15)

    # Verify the solutions using the test data.
    part_one(input.test, row=10, expected=26, test=True)
    part_two(input.test, max_coord=20, expected=56000011, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, **PROGRAM_ARGS["part_one"], expected=5832528)
        part_two(data, **PROGRAM_ARGS["part_two"], expected=13360899249595)
