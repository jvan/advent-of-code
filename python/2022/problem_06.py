"""
Day 6: Tuning Trouble

In this problem we are given a datastream consisting of a list of characters.

For the first part we need to find the locaiton of start-of-packet marker in the
datastream. The marker is indicated by four characters which are all different.

In part two we need to find the start-of-message marker which is indicated by
14 distinct characters.
"""

import aoc


def find_marker(data: str, *, length: int) -> int:
    """Find the position of the marker in the data(stream).

    The signal start is identified by a unique string of characters. The length of the
    marker is given as a function argument.
    """

    for i in range(len(data)):
        # Get the next marker-sized sequence of characters.
        seq = data[i : i + length]

        # If all the characters in the sequence are unique, then the start of the signal
        # data is the current index plus an offset equal to the marker length.
        if len(set(seq)) == length:
            return i + length

    # Return a negative value if packet marker was found.
    return -1


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Find the position of the start-of-packet marker."""

    return find_marker(input, length=4)


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Find the position of the start-of-message marker."""

    return find_marker(input, length=14)


if __name__ == "__main__":
    # Verify the solutions using the test data.
    input = aoc.get_input(2022, 6)

    part_one(input.test, expected=7, test=True)
    part_two(input.test, expected=19, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=1794)
        part_two(data, expected=2851)
