"""
Day 7: No Space Left On Device

In this problem we are given terminal output which includes commands and the results
returned from those commands. The commands are limited to changing directories and listing
the contents of the current directory. From the output we can reconstruct the file system
and determine the size of each directory (including all sub-directories).

If the first part we need to find all directories with a total size of at most 100,000.

In part two we need to find the smallest directory that can be deleted that will free up
the space required to run the update.
"""


import re
from dataclasses import dataclass, field
from typing import Callable, Tuple, Union

from typing_extensions import Self

import aoc


@dataclass
class File:
    name: str
    size: int


@dataclass
class Directory:
    """Describes a filesystem directory.

    The Directory dataclass is a recursive data structure that contains files and
    child, sub-directories.
    """

    name: str
    parent: Union[Self, None] = None
    files: list[File] = field(default_factory=list)
    children: list[Self] = field(default_factory=list)

    def size(self) -> int:
        """Return the total size of the directory, including sub-directories."""

        # The size of the directory is the sum of the size of all files in the directory and
        # the size of all child directories.
        total_files = sum(file.size for file in self.files)
        total_children = sum(dir.size() for dir in self.children)

        return total_files + total_children

    def get_subdir(self, name: str) -> Union[Self, None]:
        """Return the specified child, sub-directory if it exists."""

        for child in self.children:
            if child.name == name:
                return child

        return None


def parse(input: str) -> Directory:
    """Parse the terminal output and build the filesystem directory."""

    # Create the root directory for the filesystem.
    tree = Directory("/")
    current_dir = tree  # used to keep track of our current location in the filesystem

    # Split the terminal output into lines. We skip the first line which is always
    # changing into the root directory.
    lines = input.split("\n")[1:]

    # Continue until the entire terminal history has been processed.
    while lines:
        command = lines.pop(0)

        # There are only two commands found in the output: `ls` and `cd`. An `ls` command
        # will not be followed by any other arguments. The lines following an `ls` command
        # contain the files and sub-directories that are found in the current directory.
        if command == "$ ls":
            add_files(current_dir, lines)
            continue

        # Otherwise, we are dealing with a `cd` command which can be follewd by either of
        # the following arguments.
        #
        #   A ".." means change up one level to the directory that contains the current directory
        #   Any other name means change into the child, sub-directory with that name.
        #
        # Use a regex to extract the directory name argument.
        (dir_name,) = re.match(r"^\$ cd ([\w\.]+)$", command).groups()

        # If we are moving up a level, we simply need to change the current directory to
        # its parent.
        if dir_name == "..":
            current_dir = current_dir.parent

        else:
            # If the child directory has already been created, we simply update the
            # current directory.
            if child_dir := current_dir.get_subdir(dir_name):
                current_dir = child_dir

            # Otherwise, we create a new directory object and add it to the current
            # directory before updating.
            else:
                new_dir = Directory(name=dir_name, parent=current_dir)
                current_dir.children.append(new_dir)
                current_dir = new_dir

    # Return the root directory which contains the entire filesystem.
    return tree


def add_files(dir: Directory, lines: list[str]):
    """Add files to the specified directory.

    Following an `ls` command, all of the files and sub-directories that are found in the
    current directory are listed with one file/dir per line. This function processes each
    line and adds either a file, or directory, to the current dir, until it reaches the
    end of the list.
    """

    while lines:
        # Stop processing as soon as we reach a new command.
        if lines[0].startswith("$"):
            return

        # Sub-directories are dentoted by th string "dir", followed by the name of the
        # directory.
        elif lines[0].startswith("dir"):
            (_, dir_name) = lines.pop(0).split()

            # Create a new directory and add it to the current dir.
            new_dir = Directory(name=dir_name, parent=dir)
            dir.children.append(new_dir)

        # Otherwise, we are dealing with a file, which has a size, followed by the name.
        elif lines[0][0].isnumeric:
            (size, file_name) = lines.pop(0).split()

            # Create a new file and add it to the current dir.
            new_file = File(name=file_name, size=int(size))
            dir.files.append(new_file)


# We now define some types to help with the filesystem search.
#
# Describes the name and size of the directory.
DirStats = Tuple[str, int]

# Describes a function which is used to filter directories in the filesystem tree. This
# type is primarily to help make the function signatures more readable.
DirFilter = Callable[[Directory], bool]


def search_dirs(
    dir: Directory, acc: set[DirStats], *, filter: DirFilter
) -> set[DirStats]:
    """Recursively filter directories using a custom filter function."""

    # Check the current directory to see if it meets the filter criteria. If the directory
    # passes the filter check add the name and total size to the accumulator.
    if filter(dir):
        acc.add((dir.name, dir.size()))

    # Recursively search all child, sub-directories.
    for child in dir.children:
        acc = acc.union(search_dirs(child, acc, filter=filter))

    return acc


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Find all directories with a total size less than, or equal to, 100,000."""

    root = parse(input)

    # Define a filter function to select directories whose total size is at most 100,000.
    filter = lambda d: d.size() <= 100_000
    dirs = search_dirs(root, set(), filter=filter)

    # Sum up the size of all the directories that are at, or below, the size limit.
    return sum(size for _, size in dirs)


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Find the smallest directory that can be deleted to free up the required space."""

    root = parse(input)

    # Define the total amount of disk space and the amount of required free space.
    (total, required) = (70_000_000, 30_000_000)

    # Calculate the minimum amount of additional space that needs to be freed up.
    free = total - root.size()  # the current amount of free disk space
    needed = required - free  # the amount of space that must be deleted

    # We can now define a filter function to select directories that are greater than, or
    # equal to, the amount we need to free up.
    filter = lambda d: d.size() >= needed
    dirs = search_dirs(root, set(), filter=filter)

    # Find the smallest directory that can be deleted to free up the required disk space.
    min_dir_size = min(size for _, size in dirs)
    return min_dir_size


if __name__ == "__main__":
    # Verify the solutions using the test data.
    input = aoc.get_input(2022, 7)

    part_one(input.test, expected=95437, test=True)
    part_two(input.test, expected=24933642, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=1232307)
        part_two(data, expected=7268994)
