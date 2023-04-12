"""
Day 23: Unstable Diffusion

In this problem we are given a two-dimensional grid with the positions of elves marked on
it. Each round the evlves all make proposals of where to move and move to that location if
they were the only one to propose that specific location.

In part one, we simulate 10 rounds and then compute the area of the bounding box that
contains all the elves.

In the second part we continue the simulation until no elf moves.
"""

from collections import Counter
from enum import Enum
from typing import Tuple

import aoc

# Describes a two-dimensional point.
Point = Tuple[int, int]


class Direction(Enum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4


def parse(input: str) -> set[Point]:
    """Generate a set of points containing the posititons of all the elves."""

    lines = input.split("\n")

    points = set()

    for y, row in enumerate(lines):
        for x, cell in enumerate(row):
            if cell == "#":
                point = (x, y)
                points.add(point)

    return points


def simulate(points: set[Point], *, round: int):
    """Simulate a round where the elves move to new locations (maybe)."""

    # Initialize two lists, one for elves that are able to move, and one for elves that
    # will not be moving this round.
    (active, inactive) = ([], [])

    # First, each elf looks at the eight positions adjacent to their current location. If
    # there are no other elves in any of these locations the elf is inactive and does not
    # move this round.
    for elf in points:
        for neighbor in get_neighbors(elf):
            if neighbor in points:
                # We only need a single neighboring elf in order to move this round.
                active.append(elf)
                break
        else:
            inactive.append(elf)

    # Each turn the elves look in each of four directions and then proposes moving in a
    # particular direction. Each round the order of the proposals changes with the current
    # proposal being moved to the back of the list. We can simulate this by just wrapping
    # the index (see below).
    #
    # The list below is composed of tuples with a function that returns the neighboring
    # positions that need to be checked for the proposal, along with the direction the elf
    # is proposing to move in if the criteria for the proposal are satisfied.
    proposals = [
        (adjacent_north, Direction.NORTH),
        (adjacent_south, Direction.SOUTH),
        (adjacent_west, Direction.WEST),
        (adjacent_east, Direction.EAST),
    ]

    proposed_moves = []

    for elf in active:
        # Each elf tests each of the four proposals to see if they are able to move in
        # any direction.
        for i in range(len(proposals)):
            # Get the index for the round, this value is wrapped to account for the
            # changing order of the proposals each round.
            index = (round + i) % len(proposals)
            (adjacent, dir) = proposals[index]

            # Check to see if there are any elves in the positions associated with the
            # proposal.
            occupied = [point for point in adjacent(elf) if point in points]

            # We only propose the move if there are no other elves in the adjacet
            # positions.
            if not occupied:
                next_point = move(elf, dir)
                proposed_moves.append((elf, next_point))
                # Each elf can only propose one move.
                break

        # If none of the proposals are available the elf does not move this turn.
        else:
            inactive.append(elf)

    # Count the number of elves who proposed each location.
    proposal_counts = Counter([point for _, point in proposed_moves])

    moved = []
    for elf, destination in proposed_moves:
        # A proposal is accepted if only a single elf proposed that position.
        if proposal_counts[destination] == 1:
            moved.append(destination)
        # Otherwise the elves that proposed this position do not move this turn.
        else:
            inactive.append(elf)

    # Return the new positions along with the postions of the elves that did not move.
    return moved + inactive


def move(point: Point, direction: Direction) -> Point:
    """Move one step in the specified direction."""

    (x, y) = point

    match direction:
        case Direction.NORTH:
            return (x, y - 1)

        case Direction.SOUTH:
            return (x, y + 1)

        case Direction.WEST:
            return (x - 1, y)

        case Direction.EAST:
            return (x + 1, y)


def adjacent_north(point: Point) -> list[Point]:
    """Generate a list of contaning the N, NE, and NW adjacent positions."""
    (x, y) = point
    return [
        (x - 1, y - 1),
        (x, y - 1),
        (x + 1, y - 1),
    ]


def adjacent_south(point: Point) -> list[Point]:
    """Generate a list of contaning the S, SE, and SW adjacent positions."""
    (x, y) = point
    return [
        (x - 1, y + 1),
        (x, y + 1),
        (x + 1, y + 1),
    ]


def adjacent_west(point: Point) -> list[Point]:
    """Generate a list of contaning the W, NW, and SW adjacent positions."""
    (x, y) = point
    return [
        (x - 1, y - 1),
        (x - 1, y),
        (x - 1, y + 1),
    ]


def adjacent_east(point: Point) -> list[Point]:
    """Generate a list of contaning the E, NE, and SE adjacent positions."""
    (x, y) = point
    return [
        (x + 1, y - 1),
        (x + 1, y),
        (x + 1, y + 1),
    ]


def get_neighbors(point: Point) -> list[Point]:
    """Generate a list of all nearest neighbor postions."""
    (x, y) = point
    return [
        # Top Row
        (x - 1, y - 1),
        (x, y - 1),
        (x + 1, y - 1),
        # Middle Row
        (x - 1, y),
        (x + 1, y),
        # Bottom Row
        (x - 1, y + 1),
        (x, y + 1),
        (x + 1, y + 1),
    ]


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Calculate the bounding box after 10 rounds."""

    # Generate the initial elf positions from the puzzle data.
    points = parse(input)

    num_rounds = 10
    for i in range(num_rounds):
        points = simulate(points, round=i)
        points = set(points)

    return empty_tiles(points)


def empty_tiles(points: set[Point]) -> int:
    """Calculate the number of empty tiles in the bounding box containing the elves."""

    # Construct the bounding box that contains all the points.
    x_vals = [x for (x, _) in points]
    y_vals = [y for (_, y) in points]

    (x_min, x_max) = (min(x_vals), max(x_vals))
    (y_min, y_max) = (min(y_vals), max(y_vals))

    (width, height) = (x_max - x_min, y_max - y_min)

    # Compute the number of empty tiles.
    area = (width + 1) * (height + 1)
    empty = area - len(points)

    return empty


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Find the first round where no elf moves."""

    # Generate the initial elf positions from the puzzle data.
    points = parse(input)

    prev_round = set()
    round = 0

    while True:
        # Simulate a round of movement.
        points = simulate(points, round=round)
        points = set(points)

        # If the points were the same as the last round return.
        if points == prev_round:
            return round + 1

        # Store the current round results and continue to the next round.
        prev_round = points
        round += 1


if __name__ == "__main__":
    input = aoc.get_input(2022, 23)

    # Verify the solutions using the test data.
    part_one(input.test, expected=110, test=True)
    part_two(input.test, expected=20, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=4070)
        part_two(data, expected=881)
