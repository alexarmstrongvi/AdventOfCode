#!/usr/bin/env python
# Standard library
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from itertools import product

# 3rd party
import numpy as np

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# Garden Groups
#
# Example input:
# RRRRIICCFF
# RRRRIICCCF
# VVRRRCCFFF
# VVRCCCJFFF
# VVVVCJJCFE
# VVIVCCJJEE
# VVIIICJJEE
# MIIIIIJJEE
# MIIISIJEEE
# MMMISSJEEE
#
# Part 1: $1930 fence cost
# Part 2: $1206 discounter fence cost

def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    lines  = text.splitlines()
    garden = np.array(lines).view('U1').reshape(len(lines), -1)

    # Part 1 & 2
    start = time.perf_counter()
    cost = discount_cost = 0
    m,n = garden.shape
    unmapped_locations = set(product(range(m), range(n)))
    while len(unmapped_locations) > 0:
        region = determine_region(garden, unmapped_locations.pop())
        cost += region.fence_cost()
        discount_cost += region.fence_cost(bulk_discount=True)
        unmapped_locations -= set(region.fences_per_plot.keys())

        # DEBUG
        context = get_context(garden, set(region.fences_per_plot.keys()))
        log.debug('Determined fences around region:\n%s', context)
        log.debug('%d fences and %d sides', region.perimeter, region.n_sides)
        log.info('%s', region)

    elapsed = time.perf_counter() - start
    print(f'Part 1: {cost} [t={elapsed*1000:.3f}ms]')
    print(f'Part 2: {discount_cost} [t=SAME]')

################################################################################
Location = tuple[int,int]

class Direction(Enum):
    UP    = (-1, 0)
    DOWN  = ( 1, 0)
    LEFT  = ( 0,-1)
    RIGHT = ( 0, 1)

    def __getitem__(self, idx: int) -> int:
        return self.value[idx]

    def __radd__(self, loc: Location) -> Location:
        if not isinstance(loc, tuple) and len(loc) == 2:
            raise TypeError(type(loc))
        return (loc[0]+self.value[0], loc[1]+self.value[1])

@dataclass
class Region:
    plant    : str
    fences_per_plot: dict[Location, set[Direction]] = field(default_factory=lambda : defaultdict(set))

    def fence_cost(self, bulk_discount: bool = False) -> int:
        if bulk_discount:
            return self.area * self.n_sides
        return self.area * self.perimeter

    @property
    def area(self) -> int:
        return len(self.fences_per_plot)

    @cached_property
    def perimeter(self) -> int:
        return sum(len(fences) for fences in self.fences_per_plot.values())

    @cached_property
    def n_sides(self) -> int:
        n_sides = self.perimeter
        for loc, fences in self.fences_per_plot.items():
            # Don't count fences above (below) if there is a plant in the region
            # to the right that also has a fence above (below)
            if (nloc := loc + Direction.RIGHT) in self.fences_per_plot:
                nfences = self.fences_per_plot[nloc]
                if Direction.DOWN in fences and Direction.DOWN in nfences:
                    n_sides -= 1
                if Direction.UP in fences and Direction.UP in nfences:
                    n_sides -= 1

            # Don't count fences to the right (left) if there is a plant in the region
            # below that also has a fence to the right (left)
            if (nloc := loc + Direction.DOWN) in self.fences_per_plot:
                nfences = self.fences_per_plot[nloc]
                if Direction.RIGHT in fences and Direction.RIGHT in nfences:
                    n_sides -= 1
                if Direction.LEFT in fences and Direction.LEFT in nfences:
                    n_sides -= 1
        return n_sides

    def __str__(self) -> str:
        return (
            f'A region of {self.plant} plants with price {self.area:d} * {self.perimeter:d} '
            f'= ${self.fence_cost():d} and discounted price {self.area:d} * '
            f'{self.n_sides:d} = ${self.fence_cost(bulk_discount=True)}'
        )

def determine_region(
    garden : np.ndarray,
    loc    : Location,
    region : Region | None = None,
) -> Region:
    if region is None:
        region = Region(garden[loc])
    m,n = garden.shape
    outside_garden = lambda l : not (0 <= l[0] < m and 0 <= l[1] < n)
    different_plant = lambda l : garden[l] != region.plant

    fences = region.fences_per_plot[loc]
    for direction in Direction:
        nloc = loc + direction
        if outside_garden(nloc) or different_plant(nloc):
            fences.add(direction)
        elif nloc not in region.fences_per_plot:
            determine_region(garden, nloc, region)

    # DEBUG
    context = get_context(garden, loc)
    log.debug('Determined fences around plant:\n%s', context)
    log.debug('Fences: %s', [s.name for s in fences])

    return region

################################################################################
# Debugging
def get_context(garden: np.ndarray, locations: Location | set[Location]) -> str:
    apply_mask = True
    if isinstance(locations, tuple) and isinstance(locations[0], int):
        apply_mask = False
        locations = set([locations])
    assert isinstance(locations, set)

    m,n = garden.shape
    imin = min(i for i,_ in locations)
    imax = max(i for i,_ in locations)
    jmin = min(j for _,j in locations)
    jmax = max(j for _,j in locations)
    islice = slice(max(0, imin-1), min(m, imax+2))
    jslice = slice(max(0, jmin-1), min(n, jmax+2))
    context = garden[islice, jslice]
    if apply_mask:
        context = context.copy()
        mask = np.ones_like(garden, dtype=bool)
        mask[*list(map(list,zip(*locations)))] = False
        mask = mask[islice, jslice]
        context[mask] = '.'
    context = '\n'.join(''.join(row) for row in context)

    return context

################################################################################
if __name__ == "__main__":
    main()
