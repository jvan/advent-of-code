"""
Day 22: Monkey Map

In this problem we are provided with a map that contains open tiles and solid walls. We
are also given a path which consists of alternating numbers and letters. The letters can
be either R or L and indicate that we should turn 90 clockwise (R) or counterclockwise (L).
A number indicates the number of tiles that we should move in the direction we are
currently facing. For example, a path like 10R5 means

    - Go forward 10 tiles
    - Turn clockwise 90 degrees
    - Go forward 5 tiles

There are blank areas of the map which represent areas that are not on the board. If a
movement would take you off the map, you wrap around to the other side of the board and
continue in the same direction you were heading. If at any point you enconter a wall, you
stop moving and proceed to the next instruction in the path.

NOTE: If when wrapping around the board you encounter a wall as the first tile, your
    movement stops before you actually wrap around.

In part one, we need to follow the path and calculate the password from the final position
and heading.

    password = (1000 * row) + (4 * column) + facing

where the values for the facing are 0 for right, 1 for down, 2 for left, and 3 for up.

In the second part we are told that the map can be folded to form a cube. We again follow
the path, but this time instead of wrapping around the board we move to the adjacent face
on the cube.
"""

import re
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Callable, Tuple, Union

import aoc

# Describes a two-dimensional grid.
Map = list[list[str]]

# Describes a point on the grid.
Point = Tuple[int, int]


class Turn(Enum):
    RIGHT = 0
    LEFT = 1


class Direction(IntEnum):
    EAST = 0
    SOUTH = 1
    WEST = 2
    NORTH = 3


# Each step in the path consists of a forward movement (in the direction we are currently
# facing) followed by a turn.
Step = Tuple[int, Turn]

# A path is just a series of steps.
Path = list[Step]


def parse(input: str) -> Tuple[Map, Path]:
    """Generate a map and path from the puzzle data."""

    # The map and path are separated by an empty line.
    (map_data, path_data) = input.split("\n\n")

    return (parse_map(map_data), parse_path(path_data))


def parse_map(data: str) -> Map:
    """Generate a map from the grid data."""

    # Convert each row into a list of strings. Each value will be either an open tile (.),
    # a wall (#), or empty space ( ).
    rows = [list(row) for row in data.split("\n")]

    # Calculate the maximum number of columns in the grid. Some rows may have less
    # columns, in which case we pad the row with spaces (see below).
    max_width = max(len(row) for row in rows)

    map = []

    # Add columns as necessary so each row is the same length.
    for row in rows:
        for _ in range(max_width - len(row)):
            row.append(" ")
        map.append(row)

    return map


def parse_path(data: str):
    """Generate a path from the input data."""

    # Convert the input data into a list and initialize the path list.
    data, path = list(data), []

    while len(data):
        # Check the first character to see if it is a left or right turn.
        if data[0] == "L":
            path.append(Turn.LEFT)
            data.pop(0)

        elif data[0] == "R":
            path.append(Turn.RIGHT)
            data.pop(0)

        # Otherwise, it is a forward movement. We continue to pop characters off the list
        # as long as their are digits.
        else:
            n = ""
            while data and re.match(r"[0-9]", data[0]):
                n += data.pop(0)

            # Convert to an integer and add it to the path.
            path.append(int(n))

    return path


def find_start(map: Map) -> Point:
    """Find the starting location in the grd.

    We always start on the first open tile in the first row, facing right.
    """

    row = map[0]

    col = 0
    while row[col] != ".":
        col += 1

    return (col, 0)


def compute_password(pos: Point, dir: Direction) -> int:
    """Calculate the password from the given direction and direction."""

    (col, row) = pos
    return (1000 * (row + 1)) + (4 * (col + 1)) + dir


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Follow the path and compute the password."""

    # Generate the map and path from the puzzle input.
    (map, path) = parse(input)

    # Follow the path and return the password.
    (pos, dir) = follow_path(map, path)
    return compute_password(pos, dir)


def follow_path(map: Map, path: Path) -> Tuple[Point, Direction]:
    """Follow the path and return the final position and direction."""

    # Initialize the starting location and direction.
    pos, dir = find_start(map), Direction.EAST

    while path:
        # Get the next action in the path.
        action = path.pop(0)

        match action:
            # For left and right turns we simply need to update the direction.
            case Turn.RIGHT:
                dir = turn_right(dir)

            case Turn.LEFT:
                dir = turn_left(dir)

            # Otherwise, we move in the direction we are currently facing.
            case _:
                # The number of steps is given by the action itself.
                num_steps = action
                pos = move(map, pos, dir, num_steps)

    return (pos, dir)


def turn_right(dir: Direction) -> Direction:
    """Turn 90 degrees clockwise."""
    match dir:
        case Direction.NORTH:
            return Direction.EAST
        case Direction.SOUTH:
            return Direction.WEST
        case Direction.WEST:
            return Direction.NORTH
        case Direction.EAST:
            return Direction.SOUTH


def turn_left(dir: Direction) -> Direction:
    """Turn 90 degrees counterclockwise."""
    match dir:
        case Direction.NORTH:
            return Direction.WEST
        case Direction.SOUTH:
            return Direction.EAST
        case Direction.WEST:
            return Direction.SOUTH
        case Direction.EAST:
            return Direction.NORTH


def move(map: Map, pos: Point, dir: Direction, steps: int) -> Point:
    """Move the specified number of steps in the current direction.

    Args:
        map: The 2-dimensional board.
        pos: The current position on the board.
        steps: The number of steps remaining.
    """

    # Return the final position.
    if steps == 0:
        return pos

    # Compute the next step in the current direction. If the step would result is moving
    # off the board the position is wrapped around to the other side.
    (width, height) = (len(map[0]), len(map))
    (next_x, next_y) = step(pos, dir, width, height)

    # If the path is blocked by a wall return the current position.
    if map[next_y][next_x] == "#":
        return pos

    # If the next position is an empty space wrap around to find the next valid space.
    if map[next_y][next_x] == " ":
        (next_x, next_y) = wrap(map, (next_x, next_y), dir, width, height)

        # If position on the other side of the board is a wall we stay where we are.
        if map[next_y][next_x] == "#":
            return pos

        # Continue moving in the same direction on the other side.
        return move(map, (next_x, next_y), dir, steps - 1)

    # Continue moving in the current direction.
    return move(map, (next_x, next_y), dir, steps - 1)


def step(pos: Point, dir: Direction, width: int, height: int) -> Point:
    """Take a single step in the current direction."""

    (x, y) = pos

    match dir:
        case Direction.NORTH:
            (new_x, new_y) = (x, y - 1)
        case Direction.SOUTH:
            (new_x, new_y) = (x, y + 1)
        case Direction.WEST:
            (new_x, new_y) = (x - 1, y)
        case Direction.EAST:
            (new_x, new_y) = (x + 1, y)

    # Wrap around the board if necessary.
    return (new_x % width, new_y % height)


def wrap(map: Map, pos: Point, dir: Direction, width: int, height: int) -> Point:
    """Move through empty spaces until we get to an open tile or a wall."""

    (x, y) = pos

    match dir:
        case Direction.EAST:
            while map[y][x] == " ":
                x += 1
                x %= width

        case Direction.WEST:
            while map[y][x] == " ":
                x -= 1
                x %= width

        case Direction.NORTH:
            y = height - 1
            while map[y][x] == " ":
                y -= 1
                y %= height

        case Direction.SOUTH:
            while map[y][x] == " ":
                y += 1
                y %= height

    return (x, y)


# In part two we learn that the map depicts the faces of a cube. This means that when we
# move into an area that was considered empty space in part one, we are actually moving
# to aifferent face on the cube. This transiton may also mean that there is a change in
# our direction as well.
#
# The way the map folds into a cube is different for the test and puzzle data. To figure
# out the mappings I drew the patterns on a piece of paper and label each face. I then cut
# each pattern out and folded it into a cube. I used this to figure out the transitions
# from each face to its neighbors.
#
# The classes below are used to define these face transitions. It would be nice to handle
# this programatically, but this problem took enough time as it is. So for now at least,
# the configurations for the test and puzzle cubes are hard-coded below.


@dataclass
class Transition:
    """Describes the transition to another face on the cube."""

    face: int
    dir: Direction

    # When moving from one face to another we are basically mapping from points along one
    # edge on the original face, to points on a different edge on the new face. Sometimes
    # we map points on a vertical edge, to points on a horizontal edge, etc. The transform
    # function defines this mapping from one edge to another.
    transform: Callable


# Describes a mapping from face coordinates to a face ID. The face coordinates are defined
# by considering each face in the map as single cell in a 2-dimensional grid. For example,
# with the test data, the faces all lie in a 4x3 grid.
FaceMap = dict[Point, int]

# Describes a mapping from one face (and direction) to a transition object that includes a
# transform function for the new position.
NeighborMap = dict[Tuple[int, Direction], Transition]

# With these types defined we can now define a type for the cube and add configurations
# for the test and puzzle cubes.


@dataclass
class Cube:
    """Describes the configuration of faces on a cube."""

    size: int  # the width and height of each individual face
    faces: FaceMap  # mapping from face coords to face ID

    # Each cube has 24 transitions between faces.
    neighbors: NeighborMap

    def face_coords(self, face) -> Union[Point, None]:
        """Return the coordinates for the specified face ID."""

        for coords, i in self.faces.items():
            if i == face:
                return coords

        return None


# NOTE: I'm using black to automatically format the source files and while it does a
#   pretty good job most of the time, it really makes the following cube definitions
#   difficult to read. Overall I think the benefits of using a formatter far outweigh
#   the downsides, so I will just have to live with it.

# Configuration for the test cube.
CUBE_TEST = Cube(
    size=4,
    faces={(2, 0): 1, (0, 1): 2, (1, 1): 3, (2, 1): 4, (2, 2): 5, (3, 2): 6},
    neighbors={
        (1, Direction.NORTH): Transition(
            face=2,
            dir=Direction.SOUTH,
            transform=lambda size, p: (size - (p[0] + 1), 0),
        ),
        (1, Direction.SOUTH): Transition(
            face=4, dir=Direction.SOUTH, transform=lambda size, p: (p[0], 0)
        ),
        (1, Direction.EAST): Transition(
            face=6,
            dir=Direction.WEST,
            transform=lambda size, p: (size - 1, size - (p[1] + 1)),
        ),
        (1, Direction.WEST): Transition(
            face=3, dir=Direction.SOUTH, transform=lambda size, p: (p[1], 0)
        ),
        (2, Direction.NORTH): Transition(
            face=1,
            dir=Direction.SOUTH,
            transform=lambda size, p: (size - (p[0] + 1), 0),
        ),
        (2, Direction.SOUTH): Transition(
            face=5,
            dir=Direction.NORTH,
            transform=lambda size, p: (size - (p[0] + 1), size - 1),
        ),
        (2, Direction.EAST): Transition(
            face=3, dir=Direction.EAST, transform=lambda size, p: (0, p[1])
        ),
        (2, Direction.WEST): Transition(
            face=6,
            dir=Direction.NORTH,
            transform=lambda size, p: (size - (p[1] + 1), size - 1),
        ),
        (3, Direction.NORTH): Transition(
            face=1, dir=Direction.EAST, transform=lambda size, p: (0, p[0])
        ),
        (3, Direction.SOUTH): Transition(
            face=5, dir=Direction.EAST, transform=lambda size, p: (0, size - (p[0] + 1))
        ),
        (3, Direction.EAST): Transition(
            face=4, dir=Direction.EAST, transform=lambda size, p: (0, p[1])
        ),
        (3, Direction.WEST): Transition(
            face=2, dir=Direction.WEST, transform=lambda size, p: (size - 1, p[1])
        ),
        (4, Direction.NORTH): Transition(
            face=1, dir=Direction.NORTH, transform=lambda size, p: (p[0], size - 1)
        ),
        (4, Direction.SOUTH): Transition(
            face=5, dir=Direction.SOUTH, transform=lambda size, p: (p[0], 0)
        ),
        (4, Direction.EAST): Transition(
            face=6,
            dir=Direction.SOUTH,
            transform=lambda size, p: (size - (p[1] + 1), 0),
        ),
        (4, Direction.WEST): Transition(
            face=3, dir=Direction.WEST, transform=lambda size, p: (size - 1, p[1])
        ),
        (5, Direction.NORTH): Transition(
            face=4, dir=Direction.NORTH, transform=lambda size, p: (p[0], size - 1)
        ),
        (5, Direction.SOUTH): Transition(
            face=2,
            dir=Direction.NORTH,
            transform=lambda size, p: (size - (p[0] + 1), size - 1),
        ),
        (5, Direction.EAST): Transition(
            face=6, dir=Direction.EAST, transform=lambda size, p: (0, p[1])
        ),
        (5, Direction.WEST): Transition(
            face=3,
            dir=Direction.NORTH,
            transform=lambda size, p: (size - (p[1] + 1), size - 1),
        ),
        (6, Direction.NORTH): Transition(
            face=4,
            dir=Direction.WEST,
            transform=lambda size, p: (size - 1, size - (p[0] + 1)),
        ),
        (6, Direction.SOUTH): Transition(
            face=2, dir=Direction.EAST, transform=lambda size, p: (0, size - (p[0] + 1))
        ),
        (6, Direction.EAST): Transition(
            face=1,
            dir=Direction.WEST,
            transform=lambda size, p: (size - 1, size - (p[1] + 1)),
        ),
        (6, Direction.WEST): Transition(
            face=5, dir=Direction.WEST, transform=lambda size, p: (size - 1, p[1])
        ),
    },
)

# Configuration for the puzzle cube.
CUBE_PUZZLE = Cube(
    size=50,
    faces={(1, 0): 1, (2, 0): 2, (1, 1): 3, (0, 2): 4, (1, 2): 5, (0, 3): 6},
    neighbors={
        (1, Direction.NORTH): Transition(
            face=6, dir=Direction.EAST, transform=lambda size, p: (0, p[0])
        ),
        (1, Direction.SOUTH): Transition(
            face=3, dir=Direction.SOUTH, transform=lambda size, p: (p[0], 0)
        ),
        (1, Direction.EAST): Transition(
            face=2, dir=Direction.EAST, transform=lambda size, p: (0, p[1])
        ),
        (1, Direction.WEST): Transition(
            face=4, dir=Direction.EAST, transform=lambda size, p: (0, size - (p[1] + 1))
        ),
        (2, Direction.NORTH): Transition(
            face=6, dir=Direction.NORTH, transform=lambda size, p: (p[0], size - 1)
        ),
        (2, Direction.SOUTH): Transition(
            face=3, dir=Direction.WEST, transform=lambda size, p: (size - 1, p[0])
        ),
        (2, Direction.EAST): Transition(
            face=5,
            dir=Direction.WEST,
            transform=lambda size, p: (size - 1, size - (p[1] + 1)),
        ),
        (2, Direction.WEST): Transition(
            face=1, dir=Direction.WEST, transform=lambda size, p: (size - 1, p[1])
        ),
        (3, Direction.NORTH): Transition(
            face=1, dir=Direction.NORTH, transform=lambda size, p: (p[0], size - 1)
        ),
        (3, Direction.SOUTH): Transition(
            face=5, dir=Direction.SOUTH, transform=lambda size, p: (p[0], 0)
        ),
        (3, Direction.EAST): Transition(
            face=2, dir=Direction.NORTH, transform=lambda size, p: (p[1], size - 1)
        ),
        (3, Direction.WEST): Transition(
            face=4, dir=Direction.SOUTH, transform=lambda size, p: (p[1], 0)
        ),
        (4, Direction.NORTH): Transition(
            face=3, dir=Direction.EAST, transform=lambda size, p: (0, p[0])
        ),
        (4, Direction.SOUTH): Transition(
            face=6, dir=Direction.SOUTH, transform=lambda size, p: (p[0], 0)
        ),
        (4, Direction.EAST): Transition(
            face=5, dir=Direction.EAST, transform=lambda size, p: (0, p[1])
        ),
        (4, Direction.WEST): Transition(
            face=1, dir=Direction.EAST, transform=lambda size, p: (0, size - (p[1] + 1))
        ),
        (5, Direction.NORTH): Transition(
            face=3, dir=Direction.NORTH, transform=lambda size, p: (p[0], size - 1)
        ),
        (5, Direction.SOUTH): Transition(
            face=6, dir=Direction.WEST, transform=lambda size, p: (size - 1, p[0])
        ),
        (5, Direction.EAST): Transition(
            face=2,
            dir=Direction.WEST,
            transform=lambda size, p: (size - 1, size - (p[1] + 1)),
        ),
        (5, Direction.WEST): Transition(
            face=4, dir=Direction.WEST, transform=lambda size, p: (size - 1, p[1])
        ),
        (6, Direction.NORTH): Transition(
            face=4, dir=Direction.NORTH, transform=lambda size, p: (p[0], size - 1)
        ),
        (6, Direction.SOUTH): Transition(
            face=2, dir=Direction.SOUTH, transform=lambda size, p: (p[0], 0)
        ),
        (6, Direction.EAST): Transition(
            face=5, dir=Direction.NORTH, transform=lambda size, p: (p[1], size - 1)
        ),
        (6, Direction.WEST): Transition(
            face=1, dir=Direction.SOUTH, transform=lambda size, p: (p[1], 0)
        ),
    },
)


@aoc.solution(part=2)
def part_two(input: str, *, cube: Cube) -> int:
    """Follow the path on the cube and compute the password."""

    # Generate the map and path from the puzzle input.
    (map, path) = parse(input)

    # Initialize the starting location and direction.
    pos, dir = find_start(map), Direction.EAST

    while path:
        # Get the next action in the path.
        action = path.pop(0)

        match action:
            # Handle the turning cases.
            case Turn.RIGHT:
                dir = turn_right(dir)

            case Turn.LEFT:
                dir = turn_left(dir)

            case _:
                # Move forward by the specified number of steps.
                num_steps = action

                for _ in range(num_steps):
                    # In part two our direction can change as a result of transitioning
                    # from one face to another.
                    new_pos, new_dir = move_2(pos, dir, cube)
                    (new_x, new_y) = new_pos

                    # Stop if we hit a wall.
                    if map[new_y][new_x] == "#":
                        break

                    # Continue moving in the (possibly) new direction.
                    pos, dir = new_pos, new_dir

    return compute_password(pos, dir)


def move_2(pos: Point, dir: Direction, cube: Cube) -> Tuple[Point, Direction]:
    """Move one step in the specified direction."""

    (x, y) = pos
    size = cube.size

    # Get the indices for the cube face.
    (cube_x, cube_y) = (x // size, y // size)

    # Get the indices *within* the cube face.
    (face_x, face_y) = (x % size, y % size)

    # Check to see if the point is on a boundary.
    is_boundary = any(
        [
            (face_y == 0 and dir == Direction.NORTH),
            (face_y == size - 1 and dir == Direction.SOUTH),
            (face_x == 0 and dir == Direction.WEST),
            (face_x == size - 1 and dir == Direction.EAST),
        ]
    )

    # If the point is not on the boundary we can simply move in the current direction.
    if not is_boundary:
        return step_2(pos, dir), dir

    # Get the face and direction of the neighboring cube face.
    face = cube.faces[(cube_x, cube_y)]
    transition = cube.neighbors[(face, dir)]

    # Use the transform function to compute the transformed indices on the new face.
    # These indices correspond to the the indices within the new face.
    (dx, dy) = transition.transform(size, (face_x, face_y))

    # Get the face coordinates for the new face.
    (i, j) = cube.face_coords(transition.face)

    # Transform the new face coordinates (dx, dy) to global grid coordinates.
    (new_x, new_y) = (i * size + dx, j * size + dy)

    # Return the new position and direction.
    return (new_x, new_y), transition.dir


def step_2(pos: Point, dir: Direction) -> Point:
    """Take a single step in the current direction.

    This function is a slightly modified version of the previously defined `step()`
    function. Since we do not need to worry about wrapping around the cube, the dimensions
    are omitted and the mod operation is not used.
    """

    (x, y) = pos

    match dir:
        case Direction.NORTH:
            return (x, y - 1)
        case Direction.SOUTH:
            return (x, y + 1)
        case Direction.EAST:
            return (x + 1, y)
        case Direction.WEST:
            return (x - 1, y)


PROGRAM_ARGS = {"part_two": {"cube": CUBE_PUZZLE}}

if __name__ == "__main__":
    input = aoc.get_input(2022, 22)

    part_one(input.test, expected=6032, test=True)
    part_two(input.test, cube=CUBE_TEST, expected=5031, test=True)

    if data := input.puzzle:
        part_one(data, expected=165094)
        part_two(data, **PROGRAM_ARGS["part_two"], expected=95316)
