"""
Day 18: Boiling Boulders

In this problem we are given a list containg the locations of cubes which make up lava
droplet.

In part one, we need to compute the surface area of the droplet.

In the second part, we repeat the calculation, but only consider surfaces that are in
contact with the outside air. There may be interior air pockets which are excluded from
the calculation.
"""

import sys
from dataclasses import dataclass
from typing import Tuple

import aoc

# Describes a 3-dimension point in space.
Cube = Tuple[int, int, int]


def parse(input: str) -> list[Cube]:
    """Generate a list of cubes from the puzzle input."""

    lines = input.split("\n")

    cubes = []

    for line in lines:
        (x, y, z) = map(int, line.split(","))
        cubes.append((x, y, z))

    return cubes


def nearest_neighbors(cube: Cube) -> list[Cube]:
    """Return a list of all neighboring cubes."""
    (x, y, z) = cube

    return [
        (x + 1, y, z),
        (x - 1, y, z),
        (x, y + 1, z),
        (x, y - 1, z),
        (x, y, z + 1),
        (x, y, z - 1),
    ]


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Calculate the surface area of the lava droplet."""

    # Parse the puzzle input and get the cubes that form the droplet.
    cubes = parse(input)

    total = 0  # the total suface are of the droplet

    for cube in cubes:
        neighbors = nearest_neighbors(cube)

        # Compute the number of exposed sides and add it to the surface area.
        exposed = [side for side in neighbors if side not in cubes]
        total += len(exposed)

    return total


@dataclass
class BoundingBox:
    x_range: Tuple[int, int]
    y_range: Tuple[int, int]
    z_range: Tuple[int, int]

    def contains(self, point: Cube) -> bool:
        """Check whether the point is contained within the bounding box."""

        (x, y, z) = point

        return all(
            [
                (self.x_range[0] <= x < self.x_range[1]),
                (self.y_range[0] <= y < self.y_range[1]),
                (self.z_range[0] <= z < self.z_range[1]),
            ]
        )


def init_bounding_box(cubes: list[Cube]) -> BoundingBox:
    """Construct a bounding box that contains all the given cubes."""

    x_vals = [x for (x, _, _) in cubes]
    y_vals = [y for (_, y, _) in cubes]
    z_vals = [z for (_, _, z) in cubes]

    (x_min, x_max) = (min(x_vals), max(x_vals))
    (y_min, y_max) = (min(y_vals), max(y_vals))
    (z_min, z_max) = (min(z_vals), max(z_vals))

    # Add some additional padding so we can generate paths around the cubes (droplet).
    box = BoundingBox(
        x_range=(x_min - 1, x_max + 2),
        y_range=(y_min - 1, y_max + 2),
        z_range=(z_min - 1, z_max + 2),
    )

    return box


def init_costs(box: BoundingBox, start: Cube) -> dict[Cube, int]:
    """Initialize the cost matrix for the search algorithm."""

    costs = {}

    for z in range(*box.z_range):
        for y in range(*box.y_range):
            for x in range(*box.x_range):
                costs.setdefault((x, y, z), sys.maxsize)

    costs[start] = 0

    return costs


def find_paths(cubes: list[Cube], box: BoundingBox, start: Cube) -> dict[Cube, int]:
    """Search for paths from the origin to all the cubes in the droplet.

    This function uses Dijkstra's path finding algorithm to compute the travel time to
    the cubes in the droplet. In this case we don't actually care about the time/distance
    travelled, we only want to know which cubes are actually reachable from outside the
    droplet. Once the paths have all been computed, any cube with a travel cost less than
    the maximum integer value is reachable from outside the droplet and therefore an
    exterior surface.
    """

    costs = init_costs(box, start)

    # Initialize the set of positions that have already been visited as well as a queue
    # containing the positions that still need to be processed.
    visited = set()
    queue = set([start])

    while queue:
        # Generate a list of all cubes in the droplet that have not already been visited
        # and sort them based on current best travel time.
        remaining = [cube for cube in list(queue) if not (cube in visited)]
        remaining.sort(key=lambda cube: costs[cube])

        current_cube = remaining[0]
        queue.remove(current_cube)

        # Get all the nearest neighbors to the current cube. Since we are travelling in
        # air, not through the droplet, the neighbors must be empty (and contained within
        # the bounding box).
        neighbors = [
            x
            for x in nearest_neighbors(current_cube)
            if box.contains(x)
            if not x in cubes
            if not x in visited
        ]

        current_cost = costs[current_cube]

        for neighbor in neighbors:
            cost = min(current_cost + 1, costs[neighbor])
            costs[neighbor] = cost

            queue.add(neighbor)

        visited.add(current_cube)

    return costs


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Calculate the exterior surface area of the lava droplet.."""

    # Parse the puzzle input and get the cubes that form the droplet.
    cubes = parse(input)

    # Compute the bounding box for the droplet.
    box = init_bounding_box(cubes)

    # Find all the possible paths from a position outside the dorplet to all the exterior
    # faces of the droplet.
    start = (0, 0, 0)  # the origin is excluded from the puzzle data
    paths = find_paths(cubes, box, start)

    total = 0  # total exterior surface area

    for cube in cubes:
        # We only consider neighboring spaces if there is a path from them to a position
        # outside the droplet (the origin).
        neighbors = [
            p
            for p in nearest_neighbors(cube)
            if p not in cubes
            if paths[p] != sys.maxsize
        ]
        total += len(neighbors)

    return total


if __name__ == "__main__":
    input = aoc.get_input(2022, 18)

    # Verify the solutions using the test data.
    part_one(input.test, expected=64, test=True)
    part_two(input.test, expected=58, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=4456)
        part_two(data, expected=2510)
