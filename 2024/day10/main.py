#!/usr/bin/env python
# Standard library
import logging
import time
from collections import Counter
from collections.abc import Iterable
from functools import lru_cache, reduce
from operator import add

# 3rd party
import numpy as np

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# Example input:
# 89010123
# 78121874
# 87430965
# 96549874
# 45678903
# 32019012
# 01329801
# 10456732

Location = tuple[int,int]
def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    lines      = text.splitlines()
    topo_map   = np.array(lines).view('U1').astype('uint8').reshape(len(lines), -1)
    trailheads = tuple((int(i),int(j)) for i,j in zip(*np.where(topo_map == 0)))

    @lru_cache(maxsize=topo_map.size)
    def find_reachable_peaks(loc: Location) -> Counter[Location]:
        if topo_map[loc] == 9:
            return Counter((loc,))
        reachable_peaks = map(find_reachable_peaks, next_steps(topo_map, loc))
        return reduce(add, reachable_peaks, Counter())

    # Part 1 & 2
    start   = time.perf_counter()
    reachable_peaks = [find_reachable_peaks(t) for t in trailheads]
    score1   = sum(map(len, reachable_peaks))
    score2   = sum(map(lambda c : c.total(), reachable_peaks))
    elapsed = time.perf_counter() - start
    print(f'Part 1: {score1} [t={elapsed*1000:.3f}ms]')
    print(f'Part 2: {score2} [t={elapsed*1000:.3f}ms]')

def next_steps(topo_map: np.ndarray, loc: Location) -> Iterable[Location]:
    m,n = topo_map.shape
    for i,j in [(0,1),(1,0),(0,-1),(-1,0)]:
        next_loc = (loc[0]+i, loc[1]+j)
        if not (0 <= next_loc[0] < m and 0 <= next_loc[1] < n):
            continue
        elif topo_map[next_loc] == topo_map[loc]+1:
            yield next_loc

################################################################################
if __name__ == "__main__":
    main()
