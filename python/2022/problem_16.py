"""
Day 16: Proboscidea Volcanium

In this problem we are given a network of pressure valves connected by pipes (and tunnels).
Each valve has a flow rate and is connected to one, or more, tunnels. Moving from one
tunnel to another takes one minute, and it takes another minute to open a single valve.
All of valves are initially closed.

In part one, we want to determine the maximum amount of pressure that can be released in
30 minutes.

In the second part, there are two people (technically one person and one elephant) working
independently. The goal is the same as in the first part, but we only have 26 minutes.
"""

import re
from copy import copy
from dataclasses import dataclass
from typing import Tuple

import aoc


@dataclass
class Valve:
    id: str
    flow_rate: int
    tunnels: list[str]


def parse(input: str) -> dict[str, Valve]:
    """Return a dictionary that maps the valve ID to the corresponding valve object."""

    lines = input.split("\n")

    valves = {}

    # Create a regex to extract the valve info from the the puzzle input.
    pattern = re.compile(
        r"Valve ([A-Z]*) has flow rate=([0-9]*); tunnels? leads? to valves? ([A-Z,\ ]*)"
    )

    for line in lines:
        search = pattern.search(line)
        (id, flow, tunnels) = search.groups()

        # Initialize a new valve object and add it to the dictionary.
        valve = Valve(id=id, flow_rate=int(flow), tunnels=tunnels.split(", "))
        valves.setdefault(valve.id, valve)

    return valves


# Define a type for mapping the distances between valves. The key is a tuple containing
# the starting and ending locations (valves) and maps to the distances between those two
# valves.
DistTable = dict[Tuple[str, str], int]


def compute_distances(
    valves: dict[str, Valve], active_valves, *, start: str
) -> DistTable:
    """Compute the distances between active valves."""

    table = {}

    for valve_id in active_valves:
        # Compute the distances from the current valve to all other valves.
        distances = paths_from_valve(valves, valve_id)

        for target_id, dist in distances.items():
            if target_id not in active_valves or target_id == valve_id:
                continue

            table.setdefault(valve_id, {}).setdefault(target_id, dist)

    # Add paths from the starting valve to all other active valves.
    distances = paths_from_valve(valves, start)

    for target_id, dist in distances.items():
        if target_id not in active_valves:
            continue

        table.setdefault(start, {}).setdefault(target_id, dist)

    return table


def paths_from_valve(valves: dict[str, Valve], start: str) -> dict[str, int]:
    """Compute the distance from the starting valve to all other valves in the network."""

    visited = set([start])
    paths = {start: 0}
    queue = [start]

    while len(queue):
        valve = queue.pop(0)

        # Get all connected valves which have not already been visited.
        tunnels = [tunnel for tunnel in valves[valve].tunnels if tunnel not in visited]

        # Add the connected valves to the queue and mark them as visited.
        queue.extend(tunnels)
        visited = visited.union(set(tunnels))

        # The distance between tunnels is always one, so the distance to each of the
        # neighboring valves is simply one more that the distance to the current valve.
        dist = paths[valve]  # distance to the current valve
        for tunnel in tunnels:
            paths[tunnel] = dist + 1

    return paths


# A path is represented by a list containing the IDs of the valves in the order they are
# visited.
Path = list[str]


def generate_paths(distances: DistTable, *, start: str, time: int) -> list[Path]:
    """Generate a list of all possible paths from the starting point in the given time."""

    # Crate a set of valves which need to be visited. Initially, this set includes all the
    # active valves.
    remaining = set(distances.keys())

    return generate_paths_help(distances, remaining, time, start, [], [])


def generate_paths_help(
    distances, remaining, time_left, current_valve, current_path, paths
):
    # Add the valve valve to the current path and remove it from the set of remaining
    # valves that need to be checked.
    current_path.append(current_valve)
    remaining.remove(current_valve)

    # Add this path to the total paths and remove the
    paths.append(current_path)

    # If there are two or less minutes left we can immediately return since there isn't
    # enough time to travel to a new valve and activate it.
    if time_left <= 2:
        return paths

    # Generate a list of all remainng valves that can be reached (and activated) in the
    # time left.
    connected = [
        (valve, dist)
        for valve in remaining
        if (dist := distances[current_valve][valve]) <= time_left - 2
    ]

    # Stop the search if there are no more valves that can be activated.
    if not connected:
        return paths

    # For each of the connected valves we recursively call this function to generate the
    # additional possible paths.
    for valve, dist in connected:
        generate_paths_help(
            distances,
            copy(remaining),
            time_left - (dist + 1),
            valve,
            copy(current_path),
            paths,
        )

    return paths


def total_pressure(valves, distances, path, *, time):
    """Calculate the total pressure released taking the specified path."""

    total = 0

    # Group the path into segments (pairs).
    for start, end in zip(path, path[1:]):
        dist = distances[start][end]
        pressure = valves[end].flow_rate

        # The total time that the valve will be open for is the current time, minus the
        # time required to travel to the valve, minus one more minute to open the valve.
        time -= dist + 1
        total += time * pressure  # total amount of pressure resleased from the valve

    return total


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Find the maximum amount of pressure that can be released."""

    # Parse the puzzle input and generate the network graph.
    valves = parse(input)

    # Find the valves which have a non-zero flow rate. When calculating the possible
    # paths we can ignore any valves with zero flow rate. We may need to travel through
    # theses rooms, but we will never stop and open the valve.
    active_valves = [id for (id, valve) in valves.items() if valve.flow_rate > 0]

    # Calculate the distances between the valves.
    distances = compute_distances(valves, active_valves, start="AA")

    # Find all paths that can be taken in 30 minutes.
    paths = generate_paths(distances, start="AA", time=30)

    # Calculate the pressure released for each path and return the maximum value.
    return max(total_pressure(valves, distances, path, time=30) for path in paths)


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Find the maximum pressure that can be released with two workers."""

    # Parse the puzzle input and generate the network graph.
    valves = parse(input)

    # Calculate the distances between active valves just as in part one.
    active_valves = [id for (id, valve) in valves.items() if valve.flow_rate > 0]
    distances = compute_distances(valves, active_valves, start="AA")

    # Find all the paths that can be reached in 26 minutes.
    paths = generate_paths(distances, start="AA", time=26)

    # Score each path by calculating the total pressure relased and then sort them from
    # highest to lowest score. We also convert each path to a set so we can compute the
    # intersection below.
    scores = [
        (total_pressure(valves, distances, path, time=26), set(path[1:]))
        for path in paths
    ]
    scores.sort(key=lambda x: x[0], reverse=True)  # sort base on score (total pressure)

    # To find the optimal solution we consider paths that don't overlap. We can check
    # this by calculating the intersection of the two sets (paths). If the intersection
    # is the empty set, then the two paths are unique.
    max_score = 0
    for i, (score_1, s1) in enumerate(scores):
        # Since our scores are sorted from highest to lowest, if we ever get to a score
        # that is less than half our current best, we can immediately stop the search.
        if score_1 * 2 < max_score:
            break

        # Check all other scores for non-intersecting paths and compute the total score
        # for the two paths.
        for score_2, s2 in scores[i + 1 :]:
            if not s1 & s2:
                max_score = max(max_score, score_1 + score_2)

    return max_score


if __name__ == "__main__":
    input = aoc.get_input(2022, 16)

    # Verify the solutions using the test data.
    part_one(input.test, expected=1651, test=True)
    part_two(input.test, expected=1707, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=2253)
        part_two(data, expected=2838)
