"""
Day 9: Rope Bridge

In this problem we simulate moving a rope with around a two-dimensional grid. The rope
contains two, or more, knots. The motion of the rope is constrained and when moving all
knots must move from one integer position to another. The puzzle input describes the
movement of the head of the rope.

In part one, we want to compute the number of unique locations that are visited by the
tail of the rope. For this part the rope has only two knots, one for the head, and one
for the tail.

In the second part we repeat the process, but this time with a rope that has 10 knots.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from typing_extensions import Self

import aoc


class Dir(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    @staticmethod
    def from_str(val: str):
        match val:
            case "U":
                return Dir.UP
            case "D":
                return Dir.DOWN
            case "L":
                return Dir.LEFT
            case "R":
                return Dir.RIGHT
            case _:
                raise Exception("Invalid direction")


# Describes the movement of the rope. The first value is the direction and the second
# value is the number of steps in that direction.
Step = Tuple[Dir, int]


def parse(input: str) -> list[Step]:
    """Generate a list of steps for the motion of the rope."""

    steps = []

    for line in input.split("\n"):
        (dir, num) = line.split()
        steps.append((Dir.from_str(dir), int(num)))

    return steps


@dataclass
class Pos:
    x: int
    y: int

    @staticmethod
    def origin() -> Self:
        return Pos(x=0, y=0)


class Rope:
    def __init__(self, *, knots: int):
        # Initially the head of the rope, and all the tail knots, are located at the
        # origin.
        self.head = Pos.origin()
        self.tail = [Pos.origin() for _ in range(knots)]

        # The visited set contains all the points that were touched by the last knot
        # of the tail.
        self.visited = set()

    def move(self, step: Step):
        # Get the direction and the number of steps that the rope should move.
        (dir, num_steps) = step

        # When moving the rope we have to process each step individually. First the head
        # is moved, then the tail. This process is repeated for as many steps as
        # necessary. If the head of the rope was move to the final position all at once,
        # the movement of the tail would be incorrect.
        for _ in range(num_steps):
            self._move_head(dir)
            self._move_tail()

            # Add the position of the last tail knot to the visited set.
            last_knot = self.tail[-1]
            self.visited.add((last_knot.x, last_knot.y))

    def _move_head(self, dir: Dir):
        match dir:
            case Dir.UP:
                self.head.y += 1
            case Dir.DOWN:
                self.head.y -= 1
            case Dir.RIGHT:
                self.head.x += 1
            case Dir.LEFT:
                self.head.x -= 1

    def _move_tail(self):
        # Each knot in the tail moves based on the pasition of the knot ahead of it. Since
        # the first knot bases its movement on the head, we add the head position to the
        # start of the list.
        knots = [self.head] + self.tail

        for i in range(1, len(knots)):
            # For each knot we determine the distance to the knot ahead of it.
            prev_knot = knots[i - 1]
            curr_knot = knots[i]

            dx = prev_knot.x - curr_knot.x
            dy = prev_knot.y - curr_knot.y

            # If the previous knot is in an ajancent space (including diagonally), the
            # current knot stays in its current possition.
            if abs(dx) + abs(dy) <= 1 or (abs(dx) == 1 and abs(dy) == 1):
                continue

            match (dx, dy):
                # Handle the cases where the previous knot is 2 spaces away, but in the
                # same row or column. When this occurs the current knot simply moves one
                # space in the direction of the previous knot.
                case (2, 0):
                    knots[i].x += 1
                case (-2, 0):
                    knots[i].x -= 1
                case (0, 2):
                    knots[i].y += 1
                case (0, -2):
                    knots[i].y -= 1
                case _:
                    # The most a knot can move in a single turn is one space in the x and
                    # y directions. We determine which quadrant to move in, and then move
                    # as far as possible.
                    match (dx > 0, dy > 0):
                        case (True, True):
                            knots[i].x += 1
                            knots[i].y += 1
                        case (False, True):
                            knots[i].x -= 1
                            knots[i].y += 1
                        case (False, False):
                            knots[i].x -= 1
                            knots[i].y -= 1
                        case (True, False):
                            knots[i].x += 1
                            knots[i].y -= 1

        # Update the rope tail positions. The first element is excluded because it
        # corresponds to the head of the rope.
        self.tail = knots[1:]


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Determine the number of unique positions visited by the tail."""

    steps = parse(input)

    # Initialize a rope with a single tail knot.
    rope = Rope(knots=1)

    # Move the rope and return the number of positions visited by the tail.
    for step in steps:
        rope.move(step)

    return len(rope.visited)


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Repeat the problem with a longer rope."""

    steps = parse(input)

    # Initialize a rope with 9 tail knots.
    rope = Rope(knots=9)

    # Move the rope and return the number of positions visited by the last knot of the
    # tail.
    for step in steps:
        rope.move(step)

    return len(rope.visited)


if __name__ == "__main__":
    input = aoc.get_input(2022, 9)

    # Verify the solutions using the test data.
    test = input.test.split("\n\n")

    part_one(test[0], expected=13, test=True)
    part_two(test[1], expected=36, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=6087)
        part_two(data, expected=2493)
