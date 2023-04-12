"""
Day 10: Cathode-Ray Tube

In this problem we are given CPU instructions for a video system. There are only two
possible instructions:

    addx X - which adds the value X to the register
    noop - which has no effect

The addx instruction takes 2 cycles to complete, the noop only takes one cycle.

For the first part we need to calculate the signal strength during several different
cycles. The signal strength is defined as the register value multiplied by the cycle
number.

In the second part we reconstruct the image on the video display. For each cycle we check
to see if the current pixel lies within the position of a sprite. The sprite is three
pixels wide and its center is determined by the register value.
"""

from typing import Union

import aoc

# Describes the program operation. There are only two possible instructions: `addx` and
# `noop`. The `addx` operation increases the register value by an integer amount (can
# be negative). The `noop` operation has no effect and is modeled here by a `None` value.
Operation = Union[int, None]


def parse(input: str) -> list[Operation]:
    """Parse the input data and return a list of instructions for the program."""

    program = []

    for line in input.split("\n"):
        # Each line is either a `noop` or `addx` operation.
        if line == "noop":
            program.append(None)
        else:
            # The `addx` operation takes two cycles to complete. To account for this an
            # additional `noop` operation is added before the `addx`.
            (_, value) = line.split()
            program.extend([None, int(value)])

    return program


def run(program: list[Operation]) -> list[int]:
    """Run the program and return a list with the register value at each cycle."""

    register = 1  # the CPU has only a single register
    state = []  # stores the register values at the start of each cycle

    for step in program:
        # Record the current register value.
        state.append(register)

        # Update the register if the operation is an `addx`.
        if step:
            register += step

    return state


def signal_strength(state: list[int]) -> int:
    """Calculate the signal strength using the register history."""

    # The signal strength is computed by checking the register value during various
    # cycles.
    cycles = [20, 60, 100, 140, 180, 220]

    total = 0

    for cycle in cycles:
        # Multiply the register value by the cycle number and add it to the total.
        total += state[cycle - 1] * cycle

    # Return the total signal strength.
    return total


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Run the program and calculate the signal strength."""

    program = parse(input)
    state = run(program)

    return signal_strength(state)


@aoc.solution(part=2)
def part_two(input: str) -> str:
    """Run the program and construct the pixel image."""

    (screen_width, screen_height) = (40, 6)

    program = parse(input)
    state = run(program)

    pixels = "\n"
    for i in range(screen_width * screen_height):
        pixel = i % screen_width

        # If the current pixel is position within the 3-pixel wide sprite the pixel will
        # be lit. Othewise, the pixel is dark.
        if state[i] - 1 <= pixel <= state[i] + 1:
            pixels += "#"

        else:
            pixels += " "

        # Add a newline after rendering each row.
        if (pixel + 1) % screen_width == 0:
            pixels += "\n"

    return pixels


if __name__ == "__main__":
    input = aoc.get_input(2022, 10)

    # Verify the solutions using the test data.
    part_one(input.test, expected=13140, test=True)
    part_two(input.test, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=17020)
        part_two(data)
