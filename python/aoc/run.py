""" Runner for AOC problems.

This module can be used to run all problems for a given year. The results and times for
each day are displayed in a table.
"""

import importlib
import os
import re
from dataclasses import dataclass
from types import ModuleType
from typing import Tuple

import typer
from colored import attr, fg, stylize
from tabulate import tabulate
from tqdm import tqdm

import aoc

# Define a progress bar type for convenience.
ProgessBar = tqdm

# All AOC problem filenames must match this pattern.
FILE_PATTERN = re.compile("^problem_([\d]+).py$")


@dataclass
class Problem:
    year: int
    day: int

    @property
    def module(self) -> str:
        """Return the module name."""
        return f"{self.year}.problem_{self.day:02d}"


@dataclass
class Result:
    answer: any
    time: int


def find_problems(year: int) -> list[Problem]:
    """Find all problems for the specified year."""

    to_problem = lambda day: Problem(year=year, day=int(day))

    # Create a Problem object for each problem file in the directory.
    problems = [
        to_problem(search.groups()[0])
        for file in os.listdir(str(year))
        if (search := FILE_PATTERN.match(file))
    ]

    problems.sort(key=lambda problem: problem.day)
    return problems


def run_problems(problems: list[Problem]) -> Tuple[Problem, Result, Result]:
    """Run all problems and generate a list of results."""

    results = []

    # Initialize the progress bar.
    progress = tqdm(total=len(problems) * 2)

    for problem in problems:
        # Import the problem as a module.
        module = importlib.import_module(problem.module)

        # Get the input file(s) for the problem and initialize the program arguments.
        input = aoc.get_input(problem.year, problem.day)
        (args_1, args_2) = program_args(module)

        # Run each part of the problem and add the results to the list.
        part_1 = run_part(problem, module, "part_one", input.puzzle, args_1, progress)
        part_2 = run_part(problem, module, "part_two", input.puzzle, args_2, progress)

        results.append((problem, part_1, part_2))

    # Stop the progress bar.
    progress.close()

    return results


# Describes (optional) arguments that are passed to the solution functions.
ProgramArgs = dict[str, any]


def program_args(module: ModuleType) -> Tuple[ProgramArgs, ProgramArgs]:
    """Return the default and optional arguments for AOC solutions."""

    # The solution functions are always run in "quiet" mode to suppress the output.
    args = {"quiet": True}

    # Additionally, programs may define optional arguments that need to be passed to the
    # solution functions. These must be defined on a global PROGRAM_ARGS dict in the
    # problem module.
    try:
        # Merge the default and optional arguments.
        args_1 = args | module.PROGRAM_ARGS.get("part_one", {})
        args_2 = args | module.PROGRAM_ARGS.get("part_two", {})

    except AttributeError:
        args_1 = args
        args_2 = args

    return (args_1, args_2)


def run_part(
    problem: Problem,
    module: ModuleType,
    part: str,
    input: str,
    args: ProgramArgs,
    progress: ProgessBar,
) -> Result:
    """Return the results of an AOC solution."""

    # Set the progress bar description text. The day and the problem (part_one or
    # part_two) is displayed in the progress bar.
    progress.set_description(format_desc(problem.day, part))

    # Attempt to run the problem. The last day of each year only has a single part, so in
    # these cases we return an "empty" result.
    try:
        func = getattr(module, part)
        result = Result(*func(input, **args))

    except AttributeError:
        result = Result(answer="", time=0)

    # Update the progress bar.
    progress.update(1)

    return result


def format_answer(value: any, *, max_chars=32) -> str:
    """Truncate an answer if it exceeds the maximum character length."""

    if type(value) == str and len(value) > max_chars:
        return f"{value[:max_chars-3]}..."

    return str(value)


def format_time(time: int) -> str:
    """Highlight run times which exceed the various time limits."""

    time_min = 1.0  # ideally all problems should run under a second
    time_mid = 5.0  # under 5.0 seconds is acceptable
    time_max = 30.0  # anything over 30 seconds is considered slow

    if time >= time_max:
        return stylize(time, fg("red"))
    elif time >= time_mid:
        return stylize(time, fg("orange_1"))
    elif time >= time_min:
        return stylize(time, fg("light_yellow"))
    else:
        return str(time)


def format_desc(day: int, part: str) -> str:
    """Generate a description of the problem."""

    desc = ""
    desc += stylize(f"day {day}", fg("blue"))
    desc += stylize(f" [{part}]", fg("cyan"))
    return desc


def display_title(year: int):
    """Generate a title string."""

    title = ""
    title += stylize("aoc{", fg("dark_green"))
    title += stylize(year, fg("green") + attr("bold"))
    title += stylize("}", fg("dark_green"))
    print(title)


# Describes the results table data.
TableRow = Tuple[int, str, str, str, str]


def display_table(rows: list[TableRow]):
    """Format the results in a table."""

    headers = ["day", "part 1", "time 1 (s)", "part 2", "time 2 (s)"]
    table = tabulate(
        rows,
        headers=headers,
        tablefmt="rounded_outline",
        floatfmt=".4f",
        stralign="right",
        numalign="right",
    )
    print(table)


def display_total_time(time: float):
    """Format the total run time."""

    total = "Total time: "
    total += stylize(f"{time:.3f} (s)", fg("green") + attr("bold"))
    print(total)


app = typer.Typer()


@app.command()
def run_all(year: int):
    """Run all programs for the specified year."""

    # Generate a list of all problems for the year.
    problems = find_problems(year)

    # Run all problems and get the results.
    results = run_problems(problems)

    # Generate the table data from the results.
    rows = []
    total_time = 0

    for problem, part_1, part_2 in results:
        row = (
            problem.day,
            format_answer(part_1.answer),
            format_time(part_1.time),
            format_answer(part_2.answer),
            format_time(part_2.time),
        )
        rows.append(row)

        total_time += part_1.time + part_2.time

    # Display the results in a table.
    display_title(year)
    display_table(rows)
    display_total_time(total_time)


if __name__ == "__main__":
    app()
