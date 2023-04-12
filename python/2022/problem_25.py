"""
Day 25: Full of Hot Air

In this problem we are given fuel requirements that are written in the SNAFU format.
The numbers are in base-5 using the digits = (-2), - (-1), 0, 1, and 2.

In the first part we need to find the sum of all the SNAFU numbers. To do this we first
convert the numbers to decimal. We then compute the sum and convert back to SNAFU.

There is no part two for this problem.
"""

import aoc


def from_snafu(value: str) -> int:
    """Convert a SNAFU number to an integer."""

    # Generate a list of SNAFU digits.
    digits = list(value)

    # Convert the digits and multiply by powers of 5 to get the decimal values.
    digits.reverse()
    powers = [convert_digit(digit) * (5**i) for (i, digit) in enumerate(digits)]

    return sum(powers)


def convert_digit(digit: str) -> int:
    """Convert a SNAFU digit to an integer."""
    match digit:
        case "-":
            return -1
        case "=":
            return -2
        case _:
            return int(digit)


def reverse_digit(digit: int) -> str:
    """Convert an integer to a SNAFU digit."""
    match digit:
        case -2:
            return "="
        case -1:
            return "-"
        case _:
            return str(digit)


def to_snafu(digit: int) -> str:
    """Convert an integer value to a SNAFU number."""

    digits = []
    value = digit

    while value > 0:
        # To find the next digit we compute the remainder when dividing by 5 (since SNAFU
        # numbers are base-5).
        digit = value % 5

        # Divide the current value by the base (5).
        value = value // 5

        # Make sure the digit is within the range [-2, 2]
        if digit >= 3:
            # Subtract 5 to make sure the digit is within the valid range.
            digit -= 5
            # Add one to the current value to balance things out. Since we are working
            # with powers of five, the total numerical value is unchanged.
            value += 1

        digits.append(digit)

    # The digits were added from lowest to highest power so we need to reverse them.
    digits.reverse()
    return "".join(map(reverse_digit, digits))


@aoc.solution(part=1)
def part_one(input: str) -> str:
    """Calculate the sum and convert to SNAFU units."""

    # Read the SNAFU values from the puzzle data.
    fuel = input.split("\n")

    # Convert the numbers to decimal and sum.
    total = sum(map(from_snafu, fuel))

    # Return the total as a SNAFU number.
    return to_snafu(total)


if __name__ == "__main__":
    input = aoc.get_input(2022, 25)

    # Verify the solutions using the test data.
    part_one(input.test, expected="2=-1=0", test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected="2=0-2-1-0=20-01-2-20")
