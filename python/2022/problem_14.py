"""
Day 14: Regolith Reservoir

In this problem we simulate falling sand forming a pile in two dimensions. Sand is added
one unit at a time and the next unit is not added until the previous one has come to rest.
Sand will always fall straight down unless it is block by an obstacle (rock or sand). If
the sand is block it will first try to move diagonally to the left, then diagonally to the
right. The sand will keep moving until all possible positions are blocked.

The puzzle input describes rock formations which will block the falling sand. Each rock
structure is defined as a line path (some examples are shown below).

    498,4 -> 498,6 -> 496,6
    503,4 -> 502,4 -> 502,9 -> 494,9

In the first part, we run the simulation until sand begins to fall off of the last
(lowest) rock formation. In this case we treat the cave as being a bottomless abyss.

In the second part, we treat the floor as being infinite (instead of an abyss) and run the
simulation until the sand reaches the source and blocks further sand from falling.
"""

from collections import namedtuple
from typing import Tuple

import aoc

# We use a named tuple to represent positions in the 2-dimensional space.
#
# NOTE: Initially, a dataclass was used to model the 2D points, but the performance was
#   terrible. Replacing it with a tuple reduced the overall runtime significantly.
Point = namedtuple("Point", ["x", "y"])

# Define the starting point for falling sand.
ORIGIN = Point(x=500, y=0)

Path = list[Point]


def parse(input: str) -> list[Path]:
    "Convert the puzzle input into a list of paths."

    # Each rock formation is defined on a separate line.
    lines = input.split("\n")

    paths = []

    for line in lines:
        path = []

        # Split line into coordinates and convert the values to integers.
        for point in line.split(" -> "):
            (x, y) = point.split(",")
            path.append(Point(x=int(x), y=int(y)))

        paths.append(path)

    return paths


def init_rocks(paths: list[Path]) -> set[Point]:
    """Generate a set of points with the locations of all rock formations."""

    rocks = set()

    for path in paths:
        # Iterate over all point pairs in the path.
        for prev_point, curr_point in zip(path, path[1:]):
            # Add all points along the vertical segment.
            if curr_point.y == prev_point.y:
                x_min = min([curr_point.x, prev_point.x])
                x_max = max([curr_point.x, prev_point.x])

                for x in range(x_min, x_max + 1):
                    rocks.add(Point(x=x, y=curr_point.y))

            # Add all points along the horizontal segment.
            else:
                y_min = min([curr_point.y, prev_point.y])
                y_max = max([curr_point.y, prev_point.y])

                for y in range(y_min, y_max + 1):
                    rocks.add(Point(x=curr_point.x, y=y))

    return rocks


def bounding_box(rocks: set[Point]) -> Tuple[Point, Point]:
    """Calculate the bounding box that contains all the rock formations."""
    x_vals = [rock.x for rock in rocks]
    y_vals = [rock.y for rock in rocks]

    box_min = Point(x=min(x_vals), y=min(y_vals))
    box_max = Point(x=max(x_vals), y=max(y_vals))

    return (box_min, box_max)


def run_simulation(bounds: Tuple[Point, Point], rocks: set[Point]) -> set[Point]:
    """Run the sand simulation."""

    occupied = set(rocks)

    # Continue to add sand until it overflows the bottom formation.
    while True:
        sand = add_sand(bounds, occupied, ORIGIN)

        # Return as soon as we are unable to add more sand.
        if not sand:
            return occupied

        occupied.add(sand)


def add_sand(bounds: Tuple[Point, Point], occupied: set[Point], sand: Point) -> Point:
    """Find the final, resting position of the sand."""

    # Each turn the sand falls one unit in the y-direction.
    new_y = sand.y + 1

    # If the sand has fallen off the bottom formation into the abyss we return None.
    (_, grid_max) = bounds
    if new_y > grid_max.y:
        return None

    else:
        # The sand will fall directly down if possible, otherwise it will try to fall to
        # the left (diagonally), and then the right (diagonally). If all three of these
        # positions are already occupied (by sand or rock), the sand will come to rest.
        if not (next := Point(x=sand.x, y=new_y)) in occupied:
            return add_sand(bounds, occupied, next)

        elif not (next := Point(x=sand.x - 1, y=new_y)) in occupied:
            return add_sand(bounds, occupied, next)

        elif not (next := Point(x=sand.x + 1, y=new_y)) in occupied:
            return add_sand(bounds, occupied, next)

        else:
            return sand


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Compute the total amount of sand that is added before it starts to overflow."""

    # Parse the puzzle input and generate the rock formations.
    paths = parse(input)
    rocks = init_rocks(paths)

    # Calculate the bounding box for the rock formations.
    bounds = bounding_box(rocks)

    # Run the simulation and calculate the amount of sand added. When computing this vaule
    # we need to make sure we subtract the occupied positions that are part of rock
    # formations.
    occupied = run_simulation(bounds, rocks)
    return len(occupied) - len(rocks)


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Compute the total amount of sand that is added before the source is blocked."""

    # Parse the puzzle input and generate the rock formations.
    paths = parse(input)
    rocks = init_rocks(paths)

    # Calculate the bounding box for the rock formations.
    #
    # Previously, this was used to determine when sand fell off into the abyss. This time
    # we use it to determine the floor which is equal to two plus the lowest rock formation
    # y-value.
    bounds = bounding_box(rocks)

    # Run the simulation and compute the total sand added.
    occupied = simulate_2(bounds, rocks)
    return len(occupied) - len(rocks)


def simulate_2(bounds: Tuple[Point, Point], rocks: set[Point]) -> set[Point]:
    """Run the sand simulation."""
    occupied = set(rocks)

    # Continue to add sand until it reaches the origin.
    while True:
        sand = add_sand_2(bounds, occupied, ORIGIN)
        occupied.add(sand)

        if sand == ORIGIN:
            return occupied


def add_sand_2(bounds: Tuple[Point, Point], occupied: set[Point], sand: Point) -> Point:
    """Find the final, resting position of the sand."""

    # Each turn the sand falls one unit in the y-direction.
    new_y = sand.y + 1

    # Stop if the sand comes to rest on the cave floor.
    (_, grid_max) = bounds
    if sand.y == grid_max.y + 1:
        return sand

    # The movement of the sand is identical to the original `add_sand()` function.
    else:
        if not (next := Point(x=sand.x, y=new_y)) in occupied:
            return add_sand_2(bounds, occupied, next)

        elif not (next := Point(x=sand.x - 1, y=new_y)) in occupied:
            return add_sand_2(bounds, occupied, next)

        elif not (next := Point(x=sand.x + 1, y=new_y)) in occupied:
            return add_sand_2(bounds, occupied, next)

        else:
            return sand


if __name__ == "__main__":
    input = aoc.get_input(2022, 14)

    # Verify the solutions using the test data.
    part_one(input.test, expected=24, test=True)
    part_two(input.test, expected=93, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=888)
        part_two(data, expected=26461)
