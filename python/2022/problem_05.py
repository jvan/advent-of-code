"""
Day 5: Supply Stacks

In this problem we are given an ASCII diagram showing the configuration of various stacks
of crates. We are also given instructions for moving crates from one stack to another.

In the first part we rearrange the crates by moving them one at a time. After all the
crates have been moved we generate the solution by reading the values of the crates
at the top of each stack.

For the second part we repeat the process, but this time we are able to move all the
crates at once.
"""

import re
from typing import Tuple

import aoc

# Defnine some custom types for conveninece. The Stack type describes a list of crates,
# where each crate is indentified by a letter.
Stack = list[str]

# The instruction type consists of three values: (1) the number of crates to be moved,
# (2) the stack ID where the crates are currently located, and (3) the stack ID where
# the crates are to be moved.
Instruction = Tuple[int, int, int]


def parse(input: str) -> Tuple[list[Stack], list[Instruction]]:
    """Parse the input data and return the stacks and list of instructions."""

    # The initial state of the stacks and the instructions are separated by a blank line.
    (stacks, instructions) = input.split("\n\n")
    return (init_stacks(stacks), init_instructions(instructions))


def init_stacks(input: str) -> list[Stack]:
    """Generate the initial state of the stacks from the ASCII diagram.

    The positions of the crates is given in a diagram that looks like this.

            [D]
        [N] [C]
        [Z] [M] [P]
        1   2   3

    This function processes the diagram above and returns a list of Stacks with the
    following form.

        [
          [ Z, N ],
          [ M, C, D ],
          [ P ]
        ]
    """

    lines = input.split("\n")

    # The label (ID) for each stack is given on the last line. By converting the labels to
    # integers we can determine the number of stacks in the diagram.
    num_stacks = max(int(x) for x in lines[-1].split())

    # Initialize an empty list for each of the stacks in the diagram.
    stacks = [[] for _ in range(num_stacks)]

    # Starting from the bottom row (excluding the labels) add crates to the corresponding
    # stack.
    for line in reversed(lines[:-1]):
        for i in range(num_stacks):
            # Compute the column position for the stack and use it to get the crate ID. If
            # there is no crate in the position an blank space will be added to the stack.
            # These will be removed before returning the result.
            pos = 4 * i + 1

            try:
                stacks[i].append(line[pos])

            # If the line ends before the column position this means that the stack (and
            #  all other stacks to the right of it) have already ended.
            except IndexError:
                break

    # We now filter each stack and remove any "empty" values.
    for i, stack in enumerate(stacks):
        stacks[i] = [x for x in stack if x != " "]

    return stacks


def init_instructions(input: str) -> list[Instruction]:
    """Generate the list of instructions from the puzzle data.

    Each instruction has the following form:
       Move {number of crates} from {source stack} to {target stack}
    """

    # Create a regular expression to capture the numbers from the instruction.
    pattern = re.compile(r"move (\d+) from (\d+) to (\d+)")

    instructions = []

    for line in input.strip().split("\n"):
        # Extract the numbers using the regex and convert to integers.
        (count, source, target) = map(int, pattern.match(line).groups())
        instructions.append((count, source, target))

    return instructions


def stack_tops(stacks: list[Stack]) -> str:
    """Return a string composed of the top crate from each stack."""

    return "".join(stack[-1] for stack in stacks)


@aoc.solution(part=1)
def part_one(input: str) -> str:
    """Rearrange the stacks according to the instructions and print out the top crates."""

    (stacks, instructions) = parse(input)

    for count, source, target in instructions:
        # Create a list of crates which need to be moved from the source stack.
        crates = stacks[source - 1][-count:]

        # Add the crates to the target stack. Since the crates are moved one at a time,
        # the order of the stacks on the target stack will be reversed.
        stacks[target - 1].extend(reversed(crates))

        # Remove the crates from the source stack.
        stacks[source - 1] = stacks[source - 1][:-count]

    return stack_tops(stacks)


@aoc.solution(part=2)
def part_two(input: str) -> str:
    """Rearrange the stacks by moving multiple crates at once.

    This solution is nearly identical to the solution for part one. The only difference is
    that the crates are moved in a single step, rather than one at a time.
    """

    (stacks, instructions) = parse(input)

    for count, source, target in instructions:
        # Get the list of crates that need to be moved from the source stack and add them
        # to the target stack. Since the crates are moved all at once, the order stays the
        # same and we do not need to reverse the list.
        crates = stacks[source - 1][-count:]
        stacks[target - 1].extend(crates)

        # Remove the crates from the source stack.
        stacks[source - 1] = stacks[source - 1][:-count]

    return stack_tops(stacks)


if __name__ == "__main__":
    input = aoc.get_input(2022, 5)

    # Verify the solutions using the test data.
    part_one(input.test, expected="CMZ", test=True)
    part_two(input.test, expected="MCD", test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected="SHQWSRBDL")
        part_two(data, expected="CDTQZHBRS")
