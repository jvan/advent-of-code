"""
Day 17: Pyroclastic Flow

In this problem we simulate a simplified game of Tetris. There are five different block
shapes which always fall in the same order (once the end of the list is reached, the first
block is dropped again). The blocks cannot rotate, but they are moved left and right by
jets of hot gas. The pattern (left/right) of the jets is the puzzle input. The jet pattern
repeats just like the blocks.

In the first part we want to determine the height of the tower after 2022 blocks have been
dropped.

In part two, we need to find the height after 1000000000000 blocks have been dropped. This
number is obviously outside the realm of computability, so we need to find a repeating
pattern in order to solve this part of the problem.
"""

from enum import IntEnum
from typing import Tuple

import aoc

# Describes a two-dimensional point.
Point = Tuple[int, int]

# Describes an individual rock (Tetris) piece.
Rock = list[Point]


# Each step the current piece will be either blown left, or right, from the jet, or fall
# directrly down one unit.
class Action(IntEnum):
    MOVE_LEFT = 1
    MOVE_RIGHT = 2
    MOVE_DOWN = 3


def parse(input: str) -> list[Action]:
    """Generate a list of actions from the puzzle input."""

    actions = []

    # The puzzle data consists of left (<) and right (>) angle brackets which represent
    # the direction the block will be pushed. After each left/right movement the block
    # falls down one unit, so we add an additional action after each jet.
    for x in list(input):
        match x:
            case "<":
                actions.append(Action.MOVE_LEFT)
            case ">":
                actions.append(Action.MOVE_RIGHT)

        actions.append(Action.MOVE_DOWN)

    return actions


def generate_rock(id: int, floor: int) -> Rock:
    """Create a rock at the specified height.

    Each rock is initialized so that its left edge is two units away from the leftm wall
    and its bottom is three units above the highest rock in the room.
    """

    match id:
        case 0:
            return [(2, floor + 4), (3, floor + 4), (4, floor + 4), (5, floor + 4)]

        case 1:
            return [
                (3, floor + 6),
                (2, floor + 5),
                (3, floor + 5),
                (4, floor + 5),
                (3, floor + 4),
            ]

        case 2:
            return [
                (4, floor + 6),
                (4, floor + 5),
                (2, floor + 4),
                (3, floor + 4),
                (4, floor + 4),
            ]

        case 3:
            return [(2, floor + 7), (2, floor + 6), (2, floor + 5), (2, floor + 4)]

        case 4:
            return [(2, floor + 5), (3, floor + 5), (2, floor + 4), (3, floor + 4)]


# The cavern is 7 units wide.
(LEFT_WALL, RIGHT_WALL) = (0, 6)


def move_left(pile: set[Point], rock: Rock) -> Rock:
    """Move the rock one unit to the left, if possible."""

    # Find minimum x value in the rock shape.
    left_edge = min([x for (x, _) in rock])

    # Create a new rock shifted left by one unit.
    new_rock = [(x - 1, y) for (x, y) in rock]

    # Check for collisions with the left wall, or other rocks in the pile, and return the
    # new rock if the space is unoccupied.
    if left_edge > LEFT_WALL and not collision(pile, new_rock):
        return new_rock

    # Return the original position if the move was not possible.
    return rock


def move_right(pile: set[Point], rock: Rock) -> Rock:
    """Move the rock one unit to the right, if possible."""

    # Find the maximum x value in the rock shape.
    right_edge = max([x for (x, _) in rock])

    # Create a new rock shifted right by one unit.
    new_rock = [(x + 1, y) for (x, y) in rock]

    # Check for collisions with the right wall, or other rocks in the pile, and return the
    # new rock if the space is unoccupied.
    if right_edge < RIGHT_WALL and not collision(pile, new_rock):
        return new_rock

    # Return the original position if the move was not possible.
    return rock


def move_down(rock: Rock) -> Rock:
    """Move the rock down one unit."""

    new_rock = [(x, y - 1) for (x, y) in rock]
    return new_rock


def can_fall(pile: set[Rock], rock: Rock) -> bool:
    """Check to see if it is possible for the rock to move down one unit.

    The downward motion is broken up into two distict parts because we need to check if
    the rock comes to rest, unlike the move left/right cases above where the rock motion
    will always be followed by a (potential) downward movemement.
    """

    y_min = min([y for (_, y) in rock])

    new_rock = move_down(rock)
    return y_min > 0 and not collision(pile, new_rock)


def collision(pile: set[Point], rock: Rock) -> bool:
    """Check for a collision with any rock that has aleady fallen."""
    return any(point in pile for point in rock)


# The number of distinct rock shapes.
NUM_ROCKS = 5


@aoc.solution(part=1)
def part_one(input: str, *, max_rocks: int) -> int:
    """Simulate 2022 falling rocks and calculate the height."""

    # We need to track the number of rocks that have fallen and the clock count
    # separately. The clock cycle is used to determine our current position in
    # the actions array.
    num_rocks, clock = 0, 0
    max_height = -1

    # Initialize the list of actions from the puzzle input.
    actions = parse(input)
    pile = set()  # Store the positions of all blocks in the tower.

    # Run the simulation all the rocks have come to rest.
    while num_rocks < max_rocks:
        # Initialize the next rock to be dropped.
        rock_type = num_rocks % NUM_ROCKS
        rock = generate_rock(rock_type, max_height)

        # Run until the rock comes to rest.
        while True:
            # The position in the action array is determined by the clock cycle.
            action = actions[clock % len(actions)]

            match action:
                case Action.MOVE_LEFT:
                    rock = move_left(pile, rock)

                case Action.MOVE_RIGHT:
                    rock = move_right(pile, rock)

                case Action.MOVE_DOWN:
                    # If it is possible for the rock to fall, update the position and
                    # continue with the next action.
                    if can_fall(pile, rock):
                        rock = move_down(rock)

                    # Otherwise, the rock comes to rest in its current position.
                    else:
                        # The top of the shape may be lower than the current maximum
                        # height.
                        height = max([y for (_, y) in rock])
                        max_height = max(height, max_height)

                        # Add the rock to the pile so it will be included in future
                        # collision checks.
                        for point in rock:
                            pile.add(point)

                        # Move on to the next rock.
                        num_rocks += 1
                        clock += 1
                        break

            # Increment the clock cycle so the next action will be processed.
            clock += 1

    # Return the maximum height of the pile.
    return max_height + 1


@aoc.solution(part=2)
def part_two(input=str) -> int:
    """Determine the height of the pile after a LOT of rocks have been dropped.

    The number of rocks is so large that computing it directly, as we did in part one, is
    simply not feasible. The only way this problem is solvable is if there is a repeated
    pattern. If we can detect the pattern, we can calculate the number of times the pattern
    would repeat if we were to run the simulation. We then only need to account for the
    blocks before the pattern starts, and any remainder after the last pattern.
    """

    max_rocks = 1_000_000_000_000

    # Initialize the rock count and clock cycles just as in part one.
    num_rocks, clock = 0, 0
    max_height = -1

    # Initialize the actions and rock pile.
    actions = parse(input)
    pile = set()

    # To find the pattern we need to look for a repeated state. Specifically, we are going
    # to consider the (1) the rock type (shape), (2) the current action (jet stream), and
    # (3) the "height" of each column.
    #
    # NOTE: The term "height" here refers to the distance from the highest point in the
    #   column to the lowest point in any column.
    heights = [-1] * 7  # current max height of each column

    # For each unique state we store a list of tuples containing the number of rocks that
    # have fallen and the current, maximum height of the pile.
    states = {}

    while True:
        # Initialize the next rock to be dropped.
        rock_type = num_rocks % NUM_ROCKS
        rock = generate_rock(rock_type, max_height)

        # Get the next action.
        action_index = clock % len(actions)

        # Construct the current state.
        #
        # We determine the height difference for each column by subtracting the lowest
        # (maximum) column height from the current (maximum) height for that column.
        min_height = min(heights)  # lowest of all the max column heights
        deltas = [h - min_height for h in heights]

        # The state is defined by the height diffs computed above along with the rock type
        # and action (since we compute the state when a new rock is dropped the action
        # will always be a jet movement).
        state = "-".join(map(str, deltas + [rock_type, action_index]))

        # Store the rock count and max height for the state.
        states.setdefault(state, []).append((num_rocks, max(heights)))

        # If this is the third time we have seen state we have identified the pattern and
        # can stop the simulation. We could probably stop after the second occurence, but
        # we do one more just to be safe.
        if len(states[state]) == 3:
            break

        # The code below is nearly identitical to that in part one. The only difference is
        # the tracking of the column heights whenever a block comes to rest.
        while True:
            action = actions[clock % len(actions)]

            match action:
                case Action.MOVE_LEFT:
                    rock = move_left(pile, rock)

                case Action.MOVE_RIGHT:
                    rock = move_right(pile, rock)

                case Action.MOVE_DOWN:
                    if can_fall(pile, rock):
                        rock = move_down(rock)

                    else:
                        height = max([y for (_, y) in rock])
                        max_height = max(height, max_height)

                        for point in rock:
                            pile.add(point)

                            # Update the max column heights for each column.
                            (x, y) = point
                            if y > heights[x]:
                                heights[x] = y

                        num_rocks += 1
                        clock += 1
                        break

            clock += 1

    # The repeated pattern is associated with the state when we stopped the simulation.
    pattern = states[state]

    # Calculate the number of rocks and the height of the pattern.
    repeated_rocks = pattern[1][0] - pattern[0][0]
    repeated_height = pattern[1][1] - pattern[0][1]

    # The number of rocks for the first item represents the number of rocks fall before
    # the pattern begins.
    offset = pattern[0][0]

    # We can now calculate the number of times the pattern repeats as well as the number
    # of rocks rocks that are remaining after the last time the pattern repeats (in full).
    num_repeats = (max_rocks - offset) // repeated_rocks
    remaining = (max_rocks - offset) % repeated_rocks

    # The total height (minus the remainder) can now be calculated.
    total = (num_repeats * repeated_height) + pattern[0][1]

    # The last step is to calculate the height of the remainder. Do do this we can simply
    # run the simulation exactly as we did in part one. We simulate up throught the first
    # complete pattern, plus the remainder and then subtract the height after the first
    # pattern completes.
    (extra, _) = part_one(input, max_rocks=(pattern[0][0] + remaining), quiet=True)
    total += extra - pattern[0][1]

    return total


PROGRAM_ARGS = {"part_one": {"max_rocks": 2022}}

if __name__ == "__main__":
    input = aoc.get_input(2022, 17)

    # Verify the solutions using the test data.
    part_one(input.test, max_rocks=2022, expected=3068, test=True)
    part_two(input.test, expected=1514285714288, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, **PROGRAM_ARGS["part_one"], expected=3215)
        part_two(data, expected=1575811209487)
