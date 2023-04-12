"""
Day 8: Treetop Tree House

In this problem we are given a grid which contains the heights of trees.

In part one we want to compute the number of trees which are visible from outside the
grid.

In the second part we want to find the ideal location for a tree house by calculating the
scenic score, which is the product of the viewing distance in each direction.
"""

import aoc

# Describes the grid of trees. The grid value corresponds to the tree height.
Grid = list[list[int]]


def parse(input: str) -> Grid:
    # Helper function which converters a string of digits into a list of integers.
    to_heights = lambda s: [int(x) for x in list(s)]

    return [to_heights(line) for line in input.split("\n")]


def check_visibility(row: list[int], pos: int) -> bool:
    """Determine whether or not the specified position is visible from outside the grid.

    A tree is visible if all the trees on one side (or the other) have a height less than
    the tree being checked.

    Args:
      row: A list of tree heights. Row in this case simply refers to a line of trees and
        in practice can be either a horizontal row, or vertical column, in terms of the
        grid.

      pos: The index of the tree being checked for visibility.
    """

    # Split the row of trees at the given position.
    (left, right) = (row[:pos], row[pos + 1 :])

    height = row[pos]  # the height of the tree being checked

    # Helper function which checks that all heights are less than the tree height.
    is_visible = lambda l: all(x < height for x in l)

    # The tree is visible if it can be seen from either side.
    return is_visible(left) or is_visible(right)


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Calculate the number of trees that are visible from outside the grid."""

    trees = parse(input)

    (width, height) = (len(trees[0]), len(trees))  # the width and height of the grid
    visible = 0

    # Loop over all interior trees and determine which ones are visible. We can skip all
    # trees on the perimeter since these will always be visible.
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            # Get the grid row and column that contain the current tree position (x, y).
            row = trees[y]
            col = [trees[i][x] for i in range(height)]

            # Check if the tree is visible in any of the four directions.
            if check_visibility(row, x) or check_visibility(col, y):
                visible += 1

    # Calculate the number of trees in the perimetr. These are always visible.
    perimeter = 2 * len(trees[0]) + 2 * (len(trees) - 2)

    # Return the total number of visible trees.
    return visible + perimeter


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Find the maximum scenic score."""

    trees = parse(input)
    (width, height) = (len(trees[0]), len(trees))  # the width and height of the grid

    high_score = 0

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            # Get the grid row and column that contain the current tree position (x, y).
            row = trees[y]
            col = [trees[i][x] for i in range(height)]

            # Compute the scenic score for the tree and update the high scare as needed.
            score = scenic_score(row, x) * scenic_score(col, y)

            high_score = score if score > high_score else high_score

    return high_score


def scenic_score(row: list[int], pos: int) -> int:
    """Calculate the visibilty score for the specified position within the row."""

    # Split the row of trees at the given position.
    (left, right) = (row[:pos], row[pos + 1 :])

    height = row[pos]  # the height of the tree being scored

    # Helper function to compute the distance from the tree being scored to a tree that is
    # the same height, or higher.
    def view_distance(arr):
        for i, val in enumerate(arr, 1):
            if val >= height:
                return i

        # If no tree equal-height (or taller) tree is found simply return the current index
        # which is equal to the length of the list.
        return i

    # Compute the scenic score by multipling the viewing distances together. Since we are
    # searching from the tree position outward, the trees on the left (or top when computing
    # the score for a column) needs to be reversed.
    return view_distance(reversed(left)) * view_distance(right)


if __name__ == "__main__":
    input = aoc.get_input(2022, 8)

    # Verify the solutions using the test data.
    part_one(input.test, expected=21, test=True)
    part_two(input.test, expected=8, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=1681)
        part_two(data, expected=201684)
