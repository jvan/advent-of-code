import re
from functools import partial
from math import prod
from typing import Tuple, Union

import aoc


class Monkey:
    def __init__(self, id, items, op, test, if_true, if_false):
        self.id = id
        self.items = items
        self.op = op
        self.test = test
        self.if_true = if_true
        self.if_false = if_false
        self.count = 0

    def inspect(self, *, common_factor=None) -> Tuple[int, int]:
        """Inspect all items held by the monkey.

        Keyword Args:
            common_factor: If specified, this value will be used as the modulus to
                constrain the worry levels.

        Returns:
            A list of tuples containing the item (worry level) and the monkey to which the
            item should be thrown.
        """

        inspected = []

        # Keep track of the number of items inspected.
        self.count += len(self.items)

        while self.items:
            # Get the next item and calculate the new worry level.
            item = self.items.pop(0)
            item = self.op(item)

            # In the first part of the problem the worry level is divided by three (and
            # rounded down) after each monkey inspects an item. In the second part this
            # is no longer true and the worry levels will quickly grow too large to deal
            # with. However, we can avoid this by calculating a common factor from the
            # monkeys' (divisibilty) test values.
            if common_factor:
                # We can mod the worry level by the common factor without affecting the
                # divisiblity test below.
                item = item % common_factor
            else:
                item = item // 3

            # Determine which monkey to throw the item to next.
            if item % self.test == 0:
                inspected.append((item, self.if_true))
            else:
                inspected.append((item, self.if_false))

        return inspected


def parse(input: str) -> list[Monkey]:
    """Generate a list of monkeys from the puzzle input."""

    monkeys = []

    # Helper function for extracting a single regex match.
    def parse_line(pattern, line, *, convert_to=None):
        result = re.search(pattern, line).groups()[0]
        return convert_to(result) if convert_to else result

    for block in input.split("\n\n"):
        lines = block.split("\n")

        id = parse_line(r"Monkey (\d+)", lines[0], convert_to=int)
        items = parse_line(r"Starting items: (.*)", lines[1])
        op = parse_line(r"Operation: new = old (.*)", lines[2])
        test = parse_line(r"Test: divisible by (\d+)", lines[3], convert_to=int)
        if_true = parse_line(
            r"If true: throw to monkey (\d+)", lines[4], convert_to=int
        )
        if_false = parse_line(
            r"If false: throw to monkey (\d+)", lines[5], convert_to=int
        )

        # Convert the list of items to integers.
        items = [int(x) for x in items.split(",")]

        # Create the operation function for the monkey. This function modifies the worry
        # level when the monkey inspects an item. There are three possible cases.
        #
        #   1. The old worry level is multiplied by some value X (old * X)
        #   2. The old worry level is squared (old * old)
        #   3. The old worry level is increased  by some value X (old + X)
        (operator, value) = op.split()

        if operator == "*":
            # If multiplying, the old value is either multiplied by some number, or itself.
            # In the second case the integer conversion will fail.
            try:
                op_func = partial(lambda value, x: x * value, int(value))
            except ValueError:
                op_func = lambda x: x * x

        else:
            op_func = partial(lambda value, x: x + value, int(value))

        monkey = Monkey(id, items, op_func, test, if_true, if_false)
        monkeys.append(monkey)

    return monkeys


def do_round(monkeys: list[Monkey], *, common_factor: Union[int, None] = None):
    """Have each monkey inspect their items and then pass them to the next monkey."""

    for monkey in monkeys:
        items = monkey.inspect(common_factor=common_factor)

        # Add each item to the end of the monkey's item list.
        for item, target in items:
            monkeys[target].items.append(item)


def monkey_business(monkeys: list[Monkey]) -> int:
    """Multiply the inspection counts for the two most active monkeys."""

    counts = [monkey.count for monkey in monkeys]
    counts.sort(reverse=True)

    return prod(counts[:2])


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Calculate the level of monkey business after 20 rounds."""

    monkeys = parse(input)
    num_rounds = 20

    for _ in range(num_rounds):
        do_round(monkeys)

    return monkey_business(monkeys)


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Calculate the level of monkey business after 10,000 rounds."""

    monkeys = parse(input)
    num_rounds = 10_000

    # Calculate the common factor from all the divisibilty tests. These values are all
    # unique so we don't need to use a set to eliminate duplicates.
    factor = 1
    for monkey in monkeys:
        factor *= monkey.test

    for _ in range(num_rounds):
        do_round(monkeys, common_factor=factor)

    return monkey_business(monkeys)


if __name__ == "__main__":
    input = aoc.get_input(2022, 11)

    # Verify the solutions using the test data.
    part_one(input.test, expected=10605, test=True)
    part_two(input.test, expected=2713310158, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=88208)
        part_two(data, expected=21115867968)
