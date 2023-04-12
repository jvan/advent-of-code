"""
Day 2: Rock Paper Scissors

In this problem we need to simpulate a game of rock, paper, scissors.

For part one, we are given a strategy guide which tells us what our opponent will, and
what we should play in response. The format of the guide is shown below.

  A Y
  B X
  C Z

The first column denotes the opponent's shape (A=Rock, B=Paper, C=Scissors), and the
second column tells us what shape we should ploy (X=Rock, Y=Paper, Z=Scissors).

For the first part we need to simulate the tournament and determine the final score. The
score for each round is calculated as follows.

  score = shape + outcome

Where the shape values are 1 for Rock, 2 for Paper, and 3 for Scissors, and the outcome
is 0 for a loss, 3 for a draw, and 6 for a win.

In the second part, the meaning of the second column is changed and now represents the
outcome for that round (X=Lose, Y=Draw, Z=Win). Using this, along with the opponent's
shape we are able to determine what shape we should play. Again, we compute the total
score for the tournament.
"""


from enum import IntEnum
from typing import Callable, Tuple, Union

from typing_extensions import Self

import aoc

# We start by defining some enum types that represent the shape and round outcomes. By
# using an IntEnum we can assign the values that will be used when computing the score
# for the round.


class Shape(IntEnum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3

    @staticmethod
    def from_str(value: str) -> Self:
        """Convert a value from the strategy guide into a Shape.

        The opponent's shapes correspond to the values A, B, and C. The shapes that we
        should play are represented by X, Y, and Z.
        """

        if value in ["A", "X"]:
            return Shape.ROCK

        elif value in ["B", "Y"]:
            return Shape.PAPER

        elif value in ["C", "Z"]:
            return Shape.SCISSORS

        # All other values are invalid.
        else:
            raise Exception("Invalid shape value")


class Result(IntEnum):
    LOSS = 0
    DRAW = 3
    WIN = 6

    @staticmethod
    def from_str(value: str) -> Self:
        """Convert a value from the stategy guide into a Shape.

        In the second part of the problem, the meaning of the second column is changed, and
        now represents an outcome, rather than a shape.
        """

        match value:
            case "X":
                return Result.LOSS

            case "Y":
                return Result.DRAW

            case "Z":
                return Result.WIN

            # All other values are invalid.
            case _:
                raise Exception("Invalid result value")


def outcome(opponent: Shape, player: Shape) -> Result:
    """Determine the outcome for a round of Rock, Paper, Scissors."""

    match (opponent, player):
        case (Shape.ROCK, Shape.PAPER):
            return Result.WIN

        case (Shape.ROCK, Shape.SCISSORS):
            return Result.LOSS

        case (Shape.PAPER, Shape.ROCK):
            return Result.LOSS

        case (Shape.PAPER, Shape.SCISSORS):
            return Result.WIN

        case (Shape.SCISSORS, Shape.ROCK):
            return Result.WIN

        case (Shape.SCISSORS, Shape.PAPER):
            return Result.LOSS

        # In all other cases the shapes are the same and the round results in a draw.
        case _:
            return Result.DRAW


# Define a type that describes the result returned by the data parser below.
ShapeOrResult = Union[Shape, Result]


def parse(
    input: str, *, parser: Callable[[str], ShapeOrResult]
) -> list[Tuple[Shape, ShapeOrResult]]:
    """Generate a strategy guide from the puzzle data.

    Args:
      input: The strategy guide.
      parser: A parser function for the second column. This function must return either a
        a Shape or a Result.

    Returns:
      A list of tuples containing the opponent's shape and either a shape or a result,
      depending on the parser.
    """

    guide = []

    for line in input.split("\n"):
        # Split the line into two columns and convert the values to shapes/results. The first
        # column representing the opponent is always converted to a Shape. The player's value
        # will depend on the specified parser.
        (oppenent, player) = line.strip().split()
        guide.append((Shape.from_str(oppenent), parser(player)))

    return guide


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Simulate the Rock, Paper, Scissors tournment and determine the final score."""

    # Parse the strategy guide data. For this part the second column corresponds to the
    # shape that the player should play.
    guide = parse(input, parser=Shape.from_str)

    total = 0

    for opponent, player in guide:
        result = outcome(opponent, player)

        # The score is simply the sum of the result and the player's shape.
        total += result + player

    return total


def compute_shape(opponent: Shape, result: Result) -> Shape:
    """Determine which shape the player needs to play in order to obtain the desired result."""

    match (opponent, result):
        case (Shape.ROCK, Result.WIN):
            return Shape.PAPER

        case (Shape.ROCK, Result.LOSS):
            return Shape.SCISSORS

        case (Shape.PAPER, Result.WIN):
            return Shape.SCISSORS

        case (Shape.PAPER, Result.LOSS):
            return Shape.ROCK

        case (Shape.SCISSORS, Result.WIN):
            return Shape.ROCK

        case (Shape.SCISSORS, Result.LOSS):
            return Shape.PAPER

        # In all other cases we want to tie, so the player should play the same shape as the
        # opponent.
        case _:
            return opponent


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Simulate the Rock, Paper, Scissors tournament, but this time the second column in
    the strategy guide corresponds to the desired outcome for the round.
    """

    # Parse the stategy guide, but convert the second column to a result, rather than
    # a shape like we did in the first part.
    guide = parse(input, parser=Result.from_str)

    total = 0

    for opponent, result in guide:
        # In this case we know the outcome of the round, but we need to figure out which shape
        # we should play to get the desired result.
        player = compute_shape(opponent, result)

        # Compute the score in the same manner as in part one.
        total += result + player

    return total


if __name__ == "__main__":
    input = aoc.get_input(2022, 2)

    # Verify the solutions using the test data.
    part_one(input.test, expected=15, test=True)
    part_two(input.test, expected=12, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=13565)
        part_two(data, expected=12424)
