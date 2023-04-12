"""
Day 13: Distress Signal

In this problem we are give packet data that consists of lists and integers. Here are some
examples of packets.

    [1,1,5,1,1]
    [[1],[2,3,4]]
    [[1],4]
    [9]
    [[8,7,6]]

We are given the following rules for comparing packets.
    - If both values are integers the lower integer should be in the left packet
    - If both values are lists, compare each item in the list, if the left list runs out
        of items first, the inputs are in the right order.
    - If exactly one value is an integer, convert it to a list and continue.

In part one, we simply need to compare each pair of packets and determine which pairs are
in the correct order.

In the second part, we sort all the packets using the comparision function from part one,
and find the indices of two divider packets.
"""

import functools
from typing import Tuple, Union

from typing_extensions import Self

import aoc

# Packet data consists of lists and integers.
PacketData = Union[int, list[int]]

# Packets are defined as a recursive data structure.
Packet = list[Self]


def parse(input: str) -> list[Tuple[Packet, Packet]]:
    """Generate a list of packet pairs."""

    # The packet pairs are separated by empty lines.
    blocks = input.split("\n\n")

    pairs = []
    for block in blocks:
        lines = block.split("\n")
        # We can simply use `eval()` to convert each line into a python list.
        pairs.append((eval(lines[0]), eval(lines[1])))

    return pairs


def compare_packets(left: Packet, right: Packet) -> int:
    """Compare two packets.

    Returns:
        An integer represting the order of the packets.
            - zero means that the packets are equal
            - a negative one means that the left packet is less than the right packet
            - a positive one means that the left packet is greater than the right packet
    """

    # If both values are integers, the lower integer should come first.
    if type(left) == int and type(right) == int:
        if left < right:
            return -1
        elif right < left:
            return 1
        else:
            return 0

    # If both values are lists, we can compare them directly.
    elif type(left) == list and type(right) == list:
        return compare_lists(left, right)

    # If one of the values is an integer, convert it to a list and then compare the lists
    # as in the case above.
    elif type(left) == int and type(right) == list:
        return compare_lists([left], right)

    elif type(left) == list and type(right) == int:
        return compare_lists(left, [right])

    else:
        raise Exception("Invalid packet")


def compare_lists(left: list[Packet], right: list[Packet]) -> int:
    """Compare two lists of packet data.

    Packets lists are compare one item at a time. If the left packet (list) runs out of
    items first it is considered to be less than the right packet.
    """

    # Both lists are empty.
    if len(left) == 0 and len(right) == 0:
        return 0

    # If the left list runs out of items first, the lists are in order.
    if len(left) == 0:
        return -1

    # If the right list runs out of items first, the lists are out of order.
    if len(right) == 0:
        return 1

    # Otherwise, we compare the first item of each list.
    (a, b) = (left[0], right[0])

    # If the items are equal, we continue checking the remaining items in the list.
    # Otherwise we simply return the comparison result.
    if (result := compare_packets(a, b)) == 0:
        return compare_lists(left[1:], right[1:])
    else:
        return result


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Find the indices of all correctly ordered pairs."""

    pairs = parse(input)

    # Sum the indices of all pairs that are correctly ordered (the indicies start at 1).
    indices = [i for i, (a, b) in enumerate(pairs, 1) if compare_packets(a, b) == -1]
    return sum(indices)


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Sort the packets to find the decoder key.

    The decoder key is simply the product of the indices of the two divider packets.
    """

    pairs = parse(input)

    # Flatten the pairs into a single list.
    packets = []
    for a, b in pairs:
        packets.append(a)
        packets.append(b)

    # Add two additional divider packets.
    divider_1 = [[2]]
    divider_2 = [[6]]

    packets.append(divider_1)
    packets.append(divider_2)

    # Sort the packets and find the indices of the two divider packets.
    packets.sort(key=functools.cmp_to_key(compare_packets))

    index_1 = packets.index(divider_1)
    index_2 = packets.index(divider_2)

    decoder_key = (index_1 + 1) * (index_2 + 1)
    return decoder_key


if __name__ == "__main__":
    # Verify the solutions using the test data.
    input = aoc.get_input(2022, 13)

    part_one(input.test, expected=13, test=True)
    part_two(input.test, expected=140, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=4821)
        part_two(data, expected=21890)
