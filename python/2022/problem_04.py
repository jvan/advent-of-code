"""
Day 4: Camp Cleanup

In this problem we are given a list with pairs of ranges, which represent sections of the
camp that need to be cleaned up. Some of the section assignments (range pairs) overlap.

For the first part we need to find the total number of assignment pairs where one range
fully contains the other.

In the second part we want to find the number of assignment pairs that overlap at all.
"""

from typing import Tuple

import aoc

# Describes the camp section IDs that have been assigned to an elf.
Assignment = set[int]


def to_assignment(pair: str) -> Assignment:
    """Convert a range string to an assignment (set).

    Camp assignments are described as a range (for example, 2-4). This function converts
    the range notation into a set which contains the values in the range (inclusive).
    """

    (start, end) = pair.split("-")
    return set(range(int(start), int(end) + 1))


def parse(input: str) -> list[Tuple[Assignment, Assignment]]:
    """Parse the input data and generate a list of assignment pairs."""

    assignments = []

    for line in input.split("\n"):
        (a, b) = line.split(",")
        assignments.append((to_assignment(a), to_assignment(b)))

    return assignments


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Determine the number of pairs where one range fully contains the other."""

    assignments = parse(input)

    # To check whether on set completely contains the other we compute the differences
    # between the sets. If either difference is the empty set then one set is fully
    # contained in the other.
    is_contained = lambda s1, s2: not (s1 - s2) or not (s2 - s1)

    return len([True for (first, second) in assignments if is_contained(first, second)])


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Determine the number of pairs with any overlap at all."""

    assignments = parse(input)

    # This solution is even simpler than the previous one. Here, we only need to look at
    # the intersection of the two sets. If the intersection is not the empty set, there
    # is some overlap between the two sets.
    return len([True for (first, second) in assignments if (first & second)])


if __name__ == "__main__":
    input = aoc.get_input(2022, 4)

    # Verify the solutions using the test data.
    part_one(input.test, expected=2, test=True)
    part_two(input.test, expected=4, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=588)
        part_two(data, expected=911)
