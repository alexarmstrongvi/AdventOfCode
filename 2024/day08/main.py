#!/usr/bin/env python
# Standard library
import logging
import time
from functools import reduce
from itertools import combinations, count 

# 3rd party
import numpy as np

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    lines       = text.splitlines()
    map_arr     = np.array(lines).view('U1').reshape(len(lines),-1)
    frequencies = [str(x) for x in np.unique(map_arr) if x != '.']
    log.debug('Frequencies: %s', frequencies)

    # Part 1
    start   = time.perf_counter()
    find    = lambda freq : find_all_antinodes(map_arr, freq, harmonic = 1)
    total   = len(reduce(set.union, map(find, frequencies)))
    elapsed = time.perf_counter() - start
    print(f'Part 1: {total} [t={elapsed*1000:.3f}ms]')

    # Part 2
    start   = time.perf_counter()
    find    = lambda freq : find_all_antinodes(map_arr, freq)
    total   = len(reduce(set.union, map(find, frequencies)))
    elapsed = time.perf_counter() - start
    print(f'Part 2: {total} [t={elapsed*1000:.3f}ms]')

Coords = tuple[int, int]
def find_all_antinodes(
    map_arr   : np.ndarray,
    frequency : str,
    harmonic  : int | None = None
) -> set[Coords]:
    antennas      = np.stack(np.where(map_arr == frequency)).transpose()
    m, n          = map_arr.shape
    gen_harmonics = lambda : [harmonic] if harmonic is not None else count()
    within_bounds = lambda loc : (0 <= loc[0] < m) and (0 <= loc[1] < n)

    all_antinodes = set()
    for antenna1, antenna2 in combinations(antennas, 2):
        delta = antenna1 - antenna2 # vector from antenna 2 to 1
        for loc, sign in [(antenna1, +1), (antenna2, -1)]:
            all_antinodes |= (aoc.Chainable(gen_harmonics())
                .map(lambda h : loc + h*sign*delta)
                .takewhile(within_bounds)
                .map(to_tuple)
                .set()
                .collect()
            )
    return all_antinodes

def to_tuple(arr: np.ndarray) -> tuple[int, ...]:
    return tuple(int(x) for x in arr)


################################################################################
if __name__ == "__main__":
    main()
