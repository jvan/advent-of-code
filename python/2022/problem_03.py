"""
Day 3: Rucksack Reorganization

In this problem we are given the contents of the elves rucksacks. The items in each
rucksack are given as a string of characters. Each rucksack has two compartments and each
item is identified by a single letter. Each compartment contains the same number of items.

For the first part we need to find the item that appears in both compartments of each
rucksack.

The second part is similar to the first, except we need to find the item that is common to
each group of elves. Each group contains three elves.

In both parts we calculate the priority of the items as follows
    Lowercase items a-z have priority 1-26
    Uppercase items A-Z have priority 27-52
"""


from typing import Tuple

import aoc

# Define a custom type that represents the contents of the rucksack. Each rucksack has
# two compartments which are represented by sets of strings, where each string is a single
# character and represents an item in the pack.
Rucksack = Tuple[set[str], set[str]]


def parse(input: str) -> list[Rucksack]:
    """Parse the input data and generate a list containing the contents of the rucksacks."""

    rucksacks = []

    for line in input.split("\n"):
        # Each compartment contains the exact same number of items so we can simply split each
        # line in half.
        middle = len(line) // 2
        (first, second) = (line[:middle], line[middle:])

        # Create a set of items for each compartment.
        rucksacks.append((set(first), set(second)))

    return rucksacks


def priority(item: str) -> int:
    """Calculate the priority for a rucksack item."""

    if item.isupper():
        return ord(item) - 64 + 26
    else:
        return ord(item) - 96


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Find the common items in each rucksack.

    The final answer is computed by summing the priority values for all the common items.
    """

    rucksacks = parse(input)

    total = 0

    for first, second in rucksacks:
        # To determine the common item we simply compute the union of the two sets. We
        # know that there is only a single item common to both sets.
        common = (first & second).pop()
        total += priority(common)

    return total


def group_by(lst: list[any], *, size: int) -> list[list[any]]:
    """Group items in a list by the specified size."""

    groups, current_group = [], []

    for item in lst:
        current_group.append(item)

        if len(current_group) == size:
            groups.append(current_group)
            current_group = []

    return groups


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Find the group badges."""

    # For this part we want to find the item that is common to each group of three. Since
    # the item can be in either compartment we don't need to split each line like we did
    # in part one above.
    rucksacks = [line.strip() for line in input.split("\n")]
    groups = group_by(rucksacks, size=3)

    total = 0

    for group in groups:
        # We determine the common item is a similar way as part one, but this time we
        # compute the union of all the rucksacks in the group.
        (s1, s2, s3) = [set(list(rucksack)) for rucksack in group]
        badge = (s1 & s2 & s3).pop()
        total += priority(badge)

    return total


if __name__ == "__main__":
    input = aoc.get_input(2022, 3)

    # Verify the solutitons using the test data.
    part_one(input.test, expected=157, test=True)
    part_two(input.test, expected=70, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=7917)
        part_two(data, expected=2585)
