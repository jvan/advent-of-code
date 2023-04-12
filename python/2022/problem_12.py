"""
Day 12: Hill Climbing Algorithm

In this probelm we are given a heightmap which gives the elevation for each point on a
grid. The height at each location is given by a lowercase letter a-z. The current,
starting location is marked `S`, and the final, target location is marked `E`.

In the first part, we need to find the shortest path to from the starting location to the
ending location.

In part two, we want to determine the shortest path to the ending location form any point
with elevation `a`.
"""

import sys
from typing import Callable, Tuple, Union

import aoc

# Describes a two-dimension grid.
Grid = list[list[int]]

# Describes an (x, y) position.
Pos = Tuple[int, int]


def grid_dims(grid: Grid) -> Tuple[int, int]:
    """Return the width and height of the grid."""

    (width, height) = (len(grid[0]), len(grid))
    return (width, height)


def grid_contains(grid: Grid, pos: Pos) -> bool:
    """Check if a position is within the grid boundaries."""

    (x, y) = pos
    (w, h) = grid_dims(grid)

    return (0 <= x < w) and (0 <= y < h)


def grid_find(grid: Grid, value: int) -> Union[Pos, None]:
    """Search the grid for the specified value."""

    (width, height) = grid_dims(grid)

    for y in range(height):
        for x in range(width):
            if grid[y][x] == value:
                return (x, y)

    return None


def grid_get(grid: Grid, pos: Pos) -> int:
    (x, y) = pos
    return grid[y][x]


def grid_set(grid: Grid, pos: Pos, value: int):
    (x, y) = pos
    grid[y][x] = value


def grid_neighbors(grid: Grid, pos: Pos) -> list[Pos]:
    """Generate a list of nearest neighbors to the specified position."""

    (x, y) = pos
    points = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

    # Only return points that are within the grid boundaries.
    return [x for x in points if grid_contains(grid, x)]


def parse(input: str) -> Grid:
    """Generate a grid of height values."""

    lines = input.split("\n")

    # Helper function which generates a row of integer height values.
    parse_row = lambda row: [to_height(x) for x in row]

    return [parse_row(row) for row in lines]


def to_height(chr: str) -> int:
    """Convert a heightmap symbol to an integer."""

    return ord(chr) - 96


def init_costs(grid: Grid, start: str) -> Grid:
    """Initialize the cost matrix for the search algorithm."""

    # Mark the initial cost for each position in the grid as the maximum integer value.
    (width, height) = grid_dims(grid)
    costs = [[sys.maxsize] * width for _ in range(height)]

    # Set the cost for starting position to zero.
    grid_set(costs, start, 0)

    return costs


ConstraintFunc = Callable[[Grid, Pos, int], bool]


def find_paths(grid: Grid, start: Pos, *, constraint: ConstraintFunc) -> Grid:
    """Find the travel costs (time) from the starting position to all points in the grid.

    This function used Djikstra's path finding algorithm to compute the travel times from
    the specified starting location.

    NOTE: usually we would also specify an end location and stop the search once that
        position has been reached. However, in part two, we need to compute the the travel
        time to all positions. Since the runtime for path one is good enough (TM), we
        won't define a separate function.

    Args:
        grid: A matrix containing the height at each position.
        start: The starting location for the path.

    Keyword Args:
        constraint: A function which is used to determine the neighboring cells which are
            reachable from the current location. For example, in our case, only neighbors
            whose hegiht is, at most, ore more than the current height.

            NOTE: This function is an argument because in part two we will be descending
                and constraint will different.

    Returns:
        The cost grid (matrix) which gives the time to travel from the starting position
        to each position on the grid.
    """

    costs = init_costs(grid, start)

    # Initialize a set of all positions that have already been visited as well as a queue
    # containing the positions that need to be processed.
    visited = set()
    queue = set([start])

    while queue:
        # Generate a list of positions in the queue that have not already been visited and
        # sort them based on the current past time to each position. This ensures that we
        # are always updating each position with the best possible time.
        remaining = [pos for pos in list(queue) if not (pos in visited)]
        remaining.sort(key=lambda pos: grid_get(costs, pos))

        # The current position is the one with the lowest travel time (cost).
        current_pos = remaining[0]
        queue.remove(current_pos)

        # Generate a list of neighbors that could possibly be visited from the current
        # location.
        current_height = grid_get(grid, current_pos)

        neighbors = [
            pos
            for pos in grid_neighbors(grid, current_pos)
            if not (pos in visited)
            if constraint(grid, pos, current_height)
        ]

        # Update the cost for each of the neighbors found above.
        current_cost = grid_get(costs, current_pos)

        for neighbor in neighbors:
            # The cost for the node is the best (lowest) value of either:
            #   - The current travel time (cost) associated with the position
            #   - One more than the travel time (cost) to the current position
            cost = min(current_cost + 1, grid_get(costs, neighbor))
            grid_set(costs, neighbor, cost)

            queue.add(neighbor)

        visited.add(current_pos)

    return costs


@aoc.solution(part=1)
def part_one(input: str):
    """Find the shortest path from the current position to the best signal location."""

    # Initialize the height grid.
    grid = parse(input)

    # Get the positions of the start and end points.
    start = grid_find(grid, to_height("S"))
    end = grid_find(grid, to_height("E"))

    # Set the elevations for the start and end points. The height values that are
    # initially for the start and end locations in the `parse()` function are negative
    # and need to be adjusted.
    grid_set(grid, start, 1)
    grid_set(grid, end, 26)

    # Define a constraint function for the path finding algorithm. In this case when
    # moving from one location to another, the destination height can be at most on higher
    # than the current elevation.
    check_height = lambda grid, pos, height: grid_get(grid, pos) <= height + 1

    # Compute the travel costs and return the travel time to the end point.
    costs = find_paths(grid, start, constraint=check_height)
    return grid_get(costs, end)


@aoc.solution(part=2)
def part_two(input: str):
    """Find the shortest path to the best signal location from any starting location with
    elevation `a'.
    """

    # Initialize the height grid.
    grid = parse(input)

    # Get the start and end positions and adjust the elevations.
    start = grid_find(grid, to_height("S"))
    end = grid_find(grid, to_height("E"))

    grid_set(grid, start, 1)
    grid_set(grid, end, 26)

    # This time we are going to start and the end position and compute the time required
    # to descend to the various starting locations. To account for this we simply need to
    # invert the constraint function that we used in part 1, we can only move to a
    # location that is at most one height lower than our current location.
    check_height = lambda grid, pos, height: grid_get(grid, pos) >= height - 1

    # Compute the travel costs from the end location to all grid locations.
    costs = find_paths(grid, end, constraint=check_height)

    # Generate a list of all grid positions with a height of 1. These represent our
    # possible starting locations.
    (width, height) = grid_dims(grid)
    starting_points = [
        (x, y) for y in range(height) for x in range(width) if grid[y][x] == 1
    ]

    # Using the travel costs computed above we can find the minimum travel time from
    # any of our possible starting locations to the end point.
    paths = [grid_get(costs, pos) for pos in starting_points]
    return min(paths)


if __name__ == "__main__":
    input = aoc.get_input(2022, 12)

    # Verify the solutions using the test data.
    part_one(input.test, expected=31, test=True)
    part_two(input.test, expected=29, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=481)
        part_two(data, expected=480)
