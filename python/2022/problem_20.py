"""
Day 20: Grove Positioning System

In this problem we are given a sequence of numbers representing an encrypted file. In
order to decrypt the data, the sequence needs to be mixed by moving each number forward
(or backward) in the file a number of positions equal to the value of the number being
moved. For example, the number `1` would be moved forword one position in the list, and
the number `-2` would be moved backward two positions.

For the first part we need to mix the file and then determine the grove coordinates by
summing the 1000th, 2000th, and 3000th numbers after the value `0`. The list is circular
and wraps around as necessary.

For part two we first multiply each number in the sequence by a decryption key and then
mix the numbers 10 times.
"""

from dataclasses import dataclass

from typing_extensions import Self

import aoc


@dataclass
class Item:
    """Describes an item in a circular list.

    Each item has a value and a refrence to the items immediately before and immediately
    after it in the list.
    """

    value: int
    prev: Self = None
    next: Self = None


# Describes the circular list.
Sequence = list[Item]


def parse(input: str) -> Sequence:
    """Generate a circular list with the sequence values."""

    # Convert the input data to integers.
    data = list(map(int, input.split("\n")))

    # Generate a list of items from the input values.
    seq = [Item(value) for value in data]

    # Assign the previous and next attributes for items in the sequence.
    for a, b in zip(seq, seq[1:]):
        a.next = b
        b.prev = a

    # Wrap the list around
    seq[0].prev = seq[-1]  # the first item points to the last
    seq[-1].next = seq[0]  # the list item points to the first

    return seq


def to_list(seq: Sequence) -> list[int]:
    """Convert a circular sequence to a list."""

    # Assign the start and end nodes.
    node = seq[0]
    end = node.prev

    values = []
    while True:
        # Add the current node value to the list.
        values.append(node.value)

        # Terminate the loop once we've reached the "end" of the list.
        if node == end:
            break

        # Move to the next item in the sequence.
        node = node.next

    return values


def mix(seq: Sequence):
    """Move all items in the sequence according to their value."""

    for node in seq:
        # Remove the current node from the list.
        node.prev.next = node.next
        node.next.prev = node.prev

        # Determine the final position of the item.
        num_steps = node.value % (len(seq) - 1)

        # Iterate through the list until we get to the target position.
        prev = node.prev
        next = node.next

        for _ in range(num_steps):
            prev = prev.next
            next = next.next

        # Insert the node into the list between the prev and next items.
        prev.next = node
        node.prev = prev

        next.prev = node
        node.next = next


def grove_coordinates(sequence: Sequence) -> int:
    """Calculate the grove coordinates for the sequence."""

    # Convert the sequence to a list of integers and find the index of the zero value.
    numbers = to_list(sequence)
    start = numbers.index(0)

    total = 0

    # Find the values at the various indices (offset from the zero position)
    offsets = [1000, 2000, 3000]
    for offset in offsets:
        index = start + offset
        index %= len(numbers)

        total += numbers[index]

    return total


@aoc.solution(part=1)
def part_one(input):
    """Mix the sequence and compute the grove coordinates."""

    sequence = parse(input)
    mix(sequence)

    return grove_coordinates(sequence)


@aoc.solution(part=2)
def part_two(input):
    sequence = parse(input)

    # Multiply all the items in the sequence by the decryption key.
    key = 811589153
    for node in sequence:
        node.value *= key

    # Mix the sequence 10 times.
    for _ in range(10):
        mix(sequence)

    return grove_coordinates(sequence)


if __name__ == "__main__":
    input = aoc.get_input(2022, 20)

    # Verify the solutions using the test data.
    part_one(input.test, expected=3, test=True)
    part_two(input.test, expected=1623178306, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=17490)
        part_two(data, expected=1632917375836)
