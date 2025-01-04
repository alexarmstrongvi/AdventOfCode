#!/usr/bin/env python
"""
Historian Hysteria
==================

# Example input:
3   4
4   3
2   5
1   3
3   9
3   3

Part 1: 11
Part 2: 31
"""
# Standard library
from collections import Counter
import logging
import time

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
    pairs = [parse(line) for line in text.splitlines()]

    # Part 1
    start        = time.perf_counter()
    list1, list2 = list(zip(*pairs))
    diff         = lambda x : abs(x[0]-x[1])
    total_diff   = sum(map(diff, zip(sorted(list1), sorted(list2))))
    elapsed      = time.perf_counter() - start
    print('Part 1:', total_diff, f'[{elapsed*1000:.3f}ms]')

    # Part 2
    start   = time.perf_counter()
    cnts    = Counter(list2)
    score   = sum(x * cnts[x] for x in list1)
    elapsed = time.perf_counter() - start
    print('Part 2:', score, f'[{elapsed*1000:.3f}ms]')

################################################################################
def parse(line: str) -> tuple[int, int]:
    x,y = line.split()
    return int(x), int(y)

################################################################################
if __name__ == "__main__":
    main()
