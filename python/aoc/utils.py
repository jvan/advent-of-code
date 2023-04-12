""" Utility classes and functions for AOC problems."""

import os.path
from dataclasses import dataclass
from time import time
from typing import Union

from colored import attr, fg, stylize

DATA_DIR = "../data/"

STYLES = {
    "success": fg("green") + attr("bold"),
    "error": fg("red") + attr("bold"),
}


@dataclass
class Input:
    """Test and puzzle data for AOC problems."""

    year: int
    day: int

    def _get_file(self, *, data_type: str) -> str:
        """Return the contents of the test (or puzzle) data file.

        The test and puzzle data files are stored in the separate directories in the root
        data directory. Within each directory the files are stored by year.
        """

        # Construct the path to the data file.
        filename = os.path.join(
            DATA_DIR, data_type, str(self.year), f"day-{self.day:02d}.txt"
        )

        # Read the file contents and strip off any trailing empty lines.
        with open(filename) as file:
            return file.read().rstrip()

    @property
    def test(self) -> str:
        """Return the test data."""

        return self._get_file(data_type="test")

    @property
    def puzzle(self) -> Union[str, None]:
        """Return the puzzle data."""

        # Since the puzzle data is not checked into the code repository, its possible that
        # the puzzle file does not exist.
        try:
            return self._get_file(data_type="puzzle")

        except FileNotFoundError:
            return None


def get_input(year: int, day: int) -> Input:
    return Input(year, day)


def solution(*, part):
    """Decorator for AOC solutions.

    The decorated function accepts the following additional keyword args:

        expected: If defined, the result returned from the function will be compared to
            this value and the result will be displayed.

        test: Used to mark test data results. If True, the test label will be used when
            displaying the results.

        quiet: If True, the results will not be displayed. This is useful if a decorated
            solution function needs to be called by another function.

    The decorated function returns a tuple containing the answer along with the program's
    runtime.
    """

    def decorator(f):
        def wrapper(*args, expected=None, test=False, quiet=False, **kwargs):
            # Call the wrapped function with the original arguments and calculate the
            # total runtime.
            start = time()
            answer = f(*args, **kwargs)
            elapsed = time() - start

            label = "test" if test else "part"
            status = ""

            # Verify the answer if an expected result was given.
            if expected:
                if answer == expected:
                    status = stylize("[ok]", STYLES["success"])
                else:
                    status = stylize(f"[err]: expected {expected}", STYLES["error"])

            if not quiet:
                print(f"[{label} {part}]: {answer} {status}\t({elapsed:.3f} s)")

            # Return the answer and the runtime.
            return (answer, elapsed)

        return wrapper

    return decorator
