"""
Day 24: Blizzard Basin

In this problem we are given a map of a square valley with blizzards. Each blizzard has a
direction of motion and moves one unit in that direction each turn. When a blizzard
reaches the edge of the grid, a new blizzard is formed on the opposite side moving in the
same direction (or you can think of it as the blizzards wrapping around the grid).

In the first part, we need to find a path from our starting location (the only open space
in the first row) to final position (the only open space on the last row) without running
into any blizzards.

In part two, we need to chart a path to the end, back to the start, and then to the end
again.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple

from typing_extensions import Self

import aoc

# Describes a 2-dimensional point on the grid.
Point = Tuple[int, int]


class Dir(Enum):
    """Describes the motion of a blizzard."""

    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3

    @staticmethod
    def from_str(char: str) -> Self:
        match char:
            case "^":
                return Dir.NORTH
            case "v":
                return Dir.SOUTH
            case ">":
                return Dir.EAST
            case "<":
                return Dir.WEST
            case _:
                raise Exception("Invalid direction")


@dataclass
class Blizzard:
    """Each blizzard has a position and direction."""

    pos: Point
    dir: Dir

    def move(self, n, dims) -> Point:
        """Move the blizzard the specified number of  steps in its direction of movement.

        If the blizzard reaches the edge of the grid it wraps around to the other side.
        """

        (x, y) = self.pos
        (w, h) = dims

        match self.dir:
            case Dir.NORTH:
                return (x, (y - n) % h)

            case Dir.SOUTH:
                return (x, (y + n) % h)

            case Dir.EAST:
                return ((x + n) % w, y)

            case Dir.WEST:
                return ((x - n) % w, y)


@dataclass
class Map:
    dims: Point
    start: Point
    end: Point
    blizzards: list[Blizzard] = field(default_factory=list)

    def simulate(self, *, minute) -> set[Point]:
        """Return a set containing the positions of all the blizzards at the specified time."""

        points = set()
        for blizzard in self.blizzards:
            pos = blizzard.move(minute, self.dims)

            points.add(pos)

        return points


def parse(input: str) -> Map:
    """Generate a map from the puzzle data."""

    lines = input.split("\n")

    # When defining the grid we ignore the first and last lines. This makes it much easier
    # to calculate (wrap) the positions of the blizzards.
    (width, height) = (len(lines[0]) - 2, len(lines) - 2)

    # The start and end points are the only non-wall spaces on the first and last lines.
    (start, end) = (lines[0].find("."), lines[-1].find("."))

    # Initialize a map object with the dimensions and start/end points.
    map = Map(dims=(width, height), start=(start - 1, -1), end=(end - 1, height))

    # Add the positions of the blizzards. We ignore the walls when determining the
    # blizzard positions.
    for y, row in enumerate(lines[1:-1]):  # ignore first and last row
        for x, cell in enumerate(list(row)[1:-1]):  # ignore first and last column
            # Each cell in the grid is either an open space (.) or a blizzard.
            if cell != ".":
                blizzard = Blizzard(pos=(x, y), dir=Dir.from_str(cell))
                map.blizzards.append(blizzard)

    return map


@aoc.solution(part=1)
def part_one(input) -> int:
    """Find the shortest amount of time required to reach the destination."""

    # Generate the map with the blizzard locations from the puzzle data.
    map = parse(input)

    # Calculate the number of steps needed to get to the end location.
    return find_path(map, map.start, map.end)


def find_path(map: Map, start: Point, end: Point, *, step: int = 1) -> int:
    """Find a path through the map that avoids the blizzards.

    This is a basic path finding algorithm with the additional option to stay in our
    current location.
    """

    queue = set([start])

    while True:
        # Calculate the positions of the blizzards at the current time step.
        blizzards = map.simulate(minute=step)

        valid_moves = []

        for pos in queue:
            # Generate a list of possible moves. This list includes staying put in the
            # current spot.
            neighborhood = neighbors(pos, map)

            for neighbor in neighborhood:
                # Return the total number of steps once we've reached the target location.
                if neighbor == end:
                    return step

                # Otherwise, add all positions that do not coincide with a blizzard to the
                # list of possible positions for the next time step.
                if neighbor not in blizzards:
                    valid_moves.append(neighbor)

        queue = set(valid_moves)

        step += 1


def neighbors(pos: Point, map: Map) -> list[Point]:
    """Return a list of all possible moves from the specified location.

    Since staying in the same spot is a valid option, this list will also include the
    current location.
    """

    (x, y) = pos
    (w, h) = map.dims

    points = [(x, y), (x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]

    # Only return locations which are within the bounds of the map (or are the start/end
    # locations).
    return [
        (x, y)
        for (x, y) in points
        if (0 <= x < w and 0 <= y < h) or ((x, y) in [map.start, map.end])
    ]


@aoc.solution(part=2)
def part_two(input) -> int:
    """Find the shortest amount of time to make 3 trips."""

    # Generate the map with the blizzard locations from the puzzle data.
    map = parse(input)

    # To solve this part, we simply calculate the steps to get from the start to the end.
    first = find_path(map, map.start, map.end)
    # Then back to the start.
    second = find_path(map, map.end, map.start, step=first)
    # And finally to the end again.
    third = find_path(map, map.start, map.end, step=second)

    return third


if __name__ == "__main__":
    input = aoc.get_input(2022, 24)

    # Verify the solutions using the test data.
    part_one(input.test, expected=18, test=True)
    part_two(input.test, expected=54, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=279)
        part_two(data, expected=762)
