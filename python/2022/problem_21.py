"""
Day 21: Monkey Math

In this problem we are given a list of monkeys and the job that each of them performs.
The job can be one of two things: either yelling a specific number or yelling the result
of a math operation. In the first case, the monkeys know then number they need to yell
from the start, but for the math operations they need to wait for the other monkeys to
yell a number, and those monkeys may need to wait on other monkeys, ond so on.

In the first part, we need to determine the number yelled by the root monkey.

In part two, we want to determine the number `humn` should yell so the numbers that the
root monkey depends on are equal.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Union

import aoc


class Op(Enum):
    """Describes a mathematical operation."""

    ADD = 1
    SUBTRACT = 2
    MULTIPLY = 3
    DIVIDE = 4


@dataclass
class Job:
    op: Op
    left: str
    right: str


# Each monkey returns either a number or the result of a math operation.
Monkey = Union[int, Job]


def parse(input: str) -> dict[str, Monkey]:
    """Return a dictionary containing the monkeys defined in the input file."""

    # Each monkey is on a single, separate line.
    lines = input.split("\n")

    monkeys = {}

    for line in lines:
        # Get the monkey name (ID) and their job.
        (monkey_id, job) = line.split(": ")

        # Check for math symbol in the job and create job with the corresponding
        # operation.
        if "+" in job:
            (left, right) = job.split(" + ")
            monkey = Job(op=Op.ADD, left=left, right=right)

        elif "-" in job:
            (left, right) = job.split(" - ")
            monkey = Job(op=Op.SUBTRACT, left=left, right=right)

        elif "*" in job:
            (left, right) = job.split(" * ")
            monkey = Job(op=Op.MULTIPLY, left=left, right=right)

        elif "/" in job:
            (left, right) = job.split(" / ")
            monkey = Job(op=Op.DIVIDE, left=left, right=right)

        # Otherwise the monkey just yells a number.
        else:
            monkey = int(job)

        monkeys.setdefault(monkey_id, monkey)

    return monkeys


def compute(monkeys: dict[str, Monkey], id: str) -> int:
    """Return the job result for the specified monkey."""

    monkey = monkeys[id]

    # If the monkey type is an integer, we simply return that value.
    if type(monkey) == int:
        return monkey

    # Otherwise we recursively call the function on the left and right monkeys and then
    # perform the mathematical operation.
    else:
        (left, right) = (compute(monkeys, monkey.left), compute(monkeys, monkey.right))

        match monkey.op:
            case Op.ADD:
                return left + right

            case Op.SUBTRACT:
                return left - right

            case Op.MULTIPLY:
                return left * right

            case Op.DIVIDE:
                return left // right


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Calculate the value returned by the root monkey."""

    # Generate the dictionary of monkeys from the puzzle input.
    monkeys = parse(input)

    return compute(monkeys, "root")


def search_monkey(monkeys: dict[str, Monkey], id: str, target: str) -> bool:
    """Recursively search the tree for the specified target monkey.

    Args:
      monkeys: Tree structure containing the all monkeys.
      id: The node used for the start of the search.
      target: The id of the monkey we are searching for.

    Returns:
      True if the target monkey was found somewhere in the tree.
    """

    monkey = monkeys[id]

    # The search fails if we reach a leaf node.
    if type(monkey) == int:
        return False

    # Check to see if the monkey is either the left or right child of the current monkey.
    (left, right) = (monkey.left, monkey.right)

    if left == target or right == target:
        return True

    # Otherwise, recursively search the left and right sub-trees.
    return search_monkey(monkeys, left, target) or search_monkey(monkeys, right, target)


def balance(monkeys: dict[str, Monkey], id: str, total: int) -> int:
    """Recursively search the sub-tree to find the value needed to balance the tree."""

    monkey = monkeys[id]

    (op, left, right) = (monkey.op, monkey.left, monkey.right)

    # This function is called recursively until we reach the humn node, at which point
    # we invert the operation to determine the starting value.
    #
    # NOTE: We need to handle the cases where the humn node is on the left/right
    #   separately since the subtraction and division operations are order-dependent.
    if left == "humn":
        sub_tree = compute(monkeys, right)
        return invert_operation(op, total, sub_tree, is_left=True)

    if right == "humn":
        sub_tree = compute(monkeys, left)
        return invert_operation(op, total, sub_tree, is_left=False)

    # If neither of the child nodes are the humn, determine which branch contains the humn
    # node and calculate the total for the other sub-tree. For example, if the humn node
    # is found in the left sub-tree, we compute the total of the right sub-tree.
    if search_monkey(monkeys, left, "humn"):
        (branch, sub_tree) = (left, compute(monkeys, right))

    else:
        (branch, sub_tree) = (right, compute(monkeys, left))

    # Calculate the new target value by inverting the current operation and then
    # recursively call this function on the sub-tree that contains the humn node.
    new_target = invert_operation(op, total, sub_tree, is_left=branch == left)
    return balance(monkeys, branch, new_target)


def invert_operation(
    operation: str, total: int, sub_tree: int, *, is_left: bool
) -> int:
    """Calculate the node value that results in the specified total."""

    # For each operation and desired outcome, compute the value that is will make the
    # inverse operation true. For example, if the operation is addition, the total is 32,
    # and the sub-tree total is 30, we would find the inverse like so
    #
    #   x + sub_tree = total
    #   x = total - sub_tree
    #
    # NOTE: When subtracting or dividing the order of the values needs to be taken into
    #   account.
    match operation:
        case Op.ADD:
            return total - sub_tree

        case Op.SUBTRACT:
            if is_left:
                return total + sub_tree
            else:
                return sub_tree - total

        case Op.MULTIPLY:
            return total // sub_tree

        case Op.DIVIDE:
            if is_left:
                return total * sub_tree
            else:
                return sub_tree // total


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Find the value for the humn node so the top-level sub-trees are equal."""

    # Generate the dictionary of monkeys from the puzzle input and get the root monkey.
    monkeys = parse(input)
    root = monkeys["root"]

    # Figure out if the humn node is in the left or right sub-tree and calculate the value
    # of the other sub-tree.
    if search_monkey(monkeys, root.left, "humn"):
        (branch, target_value) = (root.left, compute(monkeys, root.right))

    else:
        (branch, target_value) = (root.right, compute(monkeys, root.left))

    # Find the value which results in the sub-trees being equal.
    return balance(monkeys, branch, target_value)


if __name__ == "__main__":
    input = aoc.get_input(2022, 21)

    # Verify the solutions using the test data.
    part_one(input.test, expected=152)
    part_two(input.test, expected=301)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=286698846151845)
        part_two(data, expected=3759566892641)
