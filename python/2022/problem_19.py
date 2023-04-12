"""
Day 19: Not Enough Minerals

In this problem we are given a list of blueprints that describe the costs associated with
building various robots. Each robot is associated with a particular material and will
generate one of that material each minute.

In the first part, we want to determine the maximum nuber of geodes that can be obtained
in 24 minutes.

In part two, the time limit is increased to 32 minutes, but we only need to consider the
first three blueprints.
"""

import re
from copy import copy
from dataclasses import dataclass
from enum import IntEnum
from math import prod

from typing_extensions import Self

import aoc


class Material(IntEnum):
    ORE = 0
    CLAY = 1
    OBSIDIAN = 2
    GEODE = 3

    @staticmethod
    def from_str(value: str) -> Self:
        match value:
            case "ore":
                return Material.ORE
            case "clay":
                return Material.CLAY
            case "obsidian":
                return Material.OBSIDIAN
            case "geode":
                return Material.GEODE
            case _:
                raise Exception("invalid material: %s", value)


# List of all possible materials.
MATERIALS = [
    Material.ORE,
    Material.CLAY,
    Material.OBSIDIAN,
    Material.GEODE,
]


@dataclass(init=False)
class Blueprint:
    id: int

    # Costs for building a robot for a particular material.
    costs: dict[Material, dict[Material, int]]

    # The maximum number of robots required for each material.
    max_required: dict[Material, int]

    def __init__(self, id: int, costs: dict[Material, dict[Material, int]]):
        self.id = id
        self.costs = costs

        self._compute_max_required()

    def _compute_max_required(self) -> int:
        """Determine the maximum number of robots required."""
        self.max_required = {}

        # For each material we determine the maximum amount of material required to build
        # the various robots. Once we are able to build a new robot each turn it is no
        # longer necessary to harvest more of that material.
        max_cost = lambda mat, bots: max(self.costs[bot][mat] for bot in bots)

        self.max_required.setdefault(Material.ORE, max_cost(Material.ORE, MATERIALS))

        self.max_required.setdefault(
            Material.CLAY, max_cost(Material.CLAY, [Material.OBSIDIAN])
        )

        self.max_required.setdefault(
            Material.OBSIDIAN, max_cost(Material.OBSIDIAN, [Material.GEODE])
        )

        # We want to collect as many geodes as possible so we will always build more geode
        # robots if possible.
        self.max_required.setdefault(Material.GEODE, 2**32)


def parse(input: str) -> list[Blueprint]:
    """Generate a list of blueprints from the puzzle data."""

    # Each blueprint is on a single, separet line.
    lines = input.split("\n")

    blueprints = []

    for line in lines:
        # Extract the blueprint ID and the rest of the line containing the robot costs.
        id, robots = re.match("^Blueprint ([0-9]+): (.*)\.$", line).groups()

        blueprint_costs = {}

        # Split the line into the individual robot parts.
        for line in robots.split(". "):
            # Extract the robot (material) name
            material = re.match("^Each ([a-z]+) robot", line).groups()[0]

            # Remove the first part of the line. This leaves just the material names and
            # costs for the robot.
            line = line.replace(f"Each {material} robot costs ", "")

            # Initialize the costs dictionary for the robot.
            costs = blueprint_costs.setdefault(Material.from_str(material), {})

            # Add all the materials and counts to the costs dictionary.
            for cost in line.split(" and "):
                (count, material) = cost.split(" ")

                count = int(count)
                material = Material.from_str(material)

                costs.setdefault(material, count)

        # Create the blueprint and add it to the list.
        blueprint = Blueprint(int(id), blueprint_costs)
        blueprints.append(blueprint)

    return blueprints


# Pre-compute the sum of geometric series up to the maximum time value.
#
# These values are used below to calculate the maximum possible number of geodes that
# could be opened, in order to limit the number of states that need to be checked. The
# runtime for this problem is the longest of the entire year (by quite a margin), and
# every possible optimization helps.
GeoSeries = {n: sum(range(n)) for n in range(1, 33)}


@dataclass(slots=True)
class State:
    """Describes a possible state obtained by simulating a blueprint."""

    time: int
    robots: dict[Material, int]  # the number of each type of robot
    inventory: dict[Material, int]  # the amount of each material collected

    @staticmethod
    def init_robots():
        return {
            Material.ORE: 1,
            Material.CLAY: 0,
            Material.OBSIDIAN: 0,
            Material.GEODE: 0,
        }

    @staticmethod
    def init_inventory():
        return {
            Material.ORE: 0,
            Material.CLAY: 0,
            Material.OBSIDIAN: 0,
            Material.GEODE: 0,
        }

    def to_tuple(self):
        """Serialize the state so it can be stored in a set."""
        return (self.time, *self.robots.values(), *self.inventory.values())

    def can_build(self, costs: dict[Material, int]) -> bool:
        """Determine if it is possible to build a robot with the current inventory."""

        for material, required in costs.items():
            if self.inventory[material] < required:
                return False

        return True

    def build(self, robot: Material, costs: dict[Material, int]):
        """Build a robot with the specified cost."""

        for material, required in costs.items():
            self.inventory[material] -= required

        self.robots[robot] += 1

    def max_possible(self, time_limit: int) -> int:
        """The max number of geodes that could theoretically be collected in the time left."""

        time_remaining = (time_limit - self.time) + 1

        # Start with the number of geodes we have already collected.
        total = self.inventory[Material.GEODE]
        # Add the geodes that will be collected by the robots that we have already built.
        total += self.robots[Material.GEODE] * time_remaining
        # Finally, include the number we would get if we built a new geode robot each turn
        # for the rest of the time remaining.
        total += GeoSeries[time_remaining]
        return total

    def mine(self):
        """Collect materials from all robots."""

        for material, num_robots in self.robots.items():
            self.inventory[material] += num_robots


def max_geodes(blueprint: Blueprint, *, time_limit: int):
    """Return the maximum number of geodes that can be collected in the specified time."""

    max_geodes = 0
    visited = set()  # store all states that have already been explored

    # We always start with one ore collecting robot.
    queue = [
        State(time=1, robots=State.init_robots(), inventory=State.init_inventory())
    ]

    # We continue until all possible states have been explored.
    while queue:
        # Get the next state in the queue and mark it as visited.
        state = queue.pop()
        visited.add(state.to_tuple())

        # If we've reached the time limit, compute the total number of geodes collected
        # and update the maximum count.
        if state.time == time_limit:
            state.mine()

            max_geodes = max(max_geodes, state.inventory[Material.GEODE])

            # Prune the queue by removing any states which could not possibly do better
            # than the current best.
            queue = [
                state for state in queue if state.max_possible(time_limit) > max_geodes
            ]

            # Sort the queue based on time and geode count. This helps us get to the
            # better outcomes sooner, which enables us to reduce the number of possible
            # states.
            queue.sort(key=lambda s: s.time * (s.inventory[Material.GEODE] + 1))

            continue

        # Check the blueprint costs to see if we can build any robots with the currenty
        # inventory.
        new_states = []
        for robot in MATERIALS:
            # Skip if we have already built the maximum number of required robots for
            # this material.
            if state.robots[robot] >= blueprint.max_required[robot]:
                continue

            cost = blueprint.costs[robot]

            if state.can_build(cost):
                # Create a new state from the current one and mine resources for this turn.
                #
                # Since it takes a full turn for the robot to be built, we mine first and then
                # build. Otherwise, the new robot would be included in this turn, which would
                # throw off the inventory.
                new_state = State(
                    time=state.time + 1,
                    robots=copy(state.robots),
                    inventory=copy(state.inventory),
                )

                new_state.mine()
                new_state.build(robot, cost)

                # Ignare this state if it has already been explored, or if it is impossible
                # for it to beat our current best.
                if (
                    new_state.to_tuple() in visited
                    or new_state.max_possible(time_limit) <= max_geodes
                ):
                    continue

                # Add the new state to the processing queue.
                new_states.append(new_state)

        # We also need to account for the scenario where we don't build any robots. In this
        # case we simply mine for materials and then increment the time value.
        state.mine()
        state.time += 1

        if (
            state.to_tuple() not in visited
            and state.max_possible(time_limit) > max_geodes
        ):
            new_states = [state] + new_states

        # Add the new states to the proccessing queue. Since we are popping values from
        # the end, these will be processed first. This helps us get to an end result more
        # quickly, which in turn, prunes the queue and helps with the runtime.
        queue.extend(new_states)

    return max_geodes


@aoc.solution(part=1)
def part_one(input: str) -> int:
    """Determine the maximum number of geodes possible for each blueprint."""

    # Generate the blueprints from the puzzle input.
    blueprints = parse(input)

    total = 0  # total quality level
    for blueprint in blueprints:
        # Compute the quality level for the blueprint. This is just the blueprint's ID
        # multiplied by the number of geodes.
        total += blueprint.id * max_geodes(blueprint, time_limit=24)

    return total


@aoc.solution(part=2)
def part_two(input: str) -> int:
    """Find the number of geodes opened in 32 minutes."""

    # Generate the blueprints from the puzzle input.
    blueprints = parse(input)

    # Find the maximum geodes opened for the first three blueprints.
    geodes = [max_geodes(blueprint, time_limit=32) for blueprint in blueprints[:3]]

    return prod(geodes)


if __name__ == "__main__":
    input = aoc.get_input(2022, 19)

    # Verify the solutions using the test data.
    lines = []
    for blueprints in input.test.split("\n\n"):
        lines.append(" ".join(line.strip() for line in blueprints.split("\n")))

    test = "\n".join(lines)

    part_one(test, expected=33, test=True)
    part_two(test, expected=3472, test=True)

    # Solve the problem using the puzzle data.
    if data := input.puzzle:
        part_one(data, expected=1958)
        part_two(data, expected=4257)
