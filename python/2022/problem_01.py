"""
Day 1: Calorie Counting

In this problem we are given the calorie values for food items carried by the elves.

For part one, we simply need to compute the total number of calories carried by each elf
and determine which elf is carrying the most calories.

Part two is basically the same as part one except we need to calculate the calories
carried by the top three elves.
"""

import aoc

# Describes the contents (calories) carried in an elf's pack.
Calories = list[int]


def parse(input: str) -> list[Calories]:
    """Generate a list of calories for each elf in the puzzle data."""

    # The contents of the elves' packs are separated by a blank line.
    packs = input.split("\n\n")

    # Helper function which breaks the pack contents into lines and converts each value to
    # an integer.
    to_calories = lambda lines: [int(line.strip()) for line in lines.split("\n")]

    # Return a list containing the calories carried by each elf.
    return [to_calories(pack) for pack in packs]


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Find the elf that is carrying the most calories."""

    # Parse the input data.
    calories = parse(input)

    # Compute the total calories carried by each elf and return the maximum value.
    total_calories = map(sum, calories)
    return max(total_calories)


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Find the total calories carried by the top three elves."""

    # Parse the input data.
    calories = parse(input)

    # We again compute the total calories carried by each elf, but this time we sort the
    # list in order to rank the elves.
    total_calories = list(map(sum, calories))
    total_calories.sort(reverse=True)

    # To Solve this part we simply sum the top three values.
    return sum(total_calories[:3])


if __name__ == "__main__":
    input = aoc.get_input(2022, 1)

    # Verify the solutions using the test data.
    part_one(input.test, expected=24000, test=True)
    part_two(input.test, expected=45000, test=True)

    # Verify the solutions using the test data.
    if data := input.puzzle:
        part_one(data, expected=68467)
        part_two(data, expected=203420)
