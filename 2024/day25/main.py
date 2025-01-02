#!/usr/bin/env python
# Standard library
import logging
import time

# 3rd party
import numpy as np

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# Code Chronicle
#
# Example input:
# #####
# ##.##
# .#.##
# ...##
# ...#.
# ...#.
# .....
# 
# .....
# #....
# #....
# #...#
# #.#.#
# #.###
# #####
#
# Part 1: 3

def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    locks = []
    keys  = []
    for is_lock, heights in map(parse, text.split('\n\n')):
        if is_lock:
            locks.append(heights)
        else:
            keys.append(heights)
    locks = np.array(locks)
    keys  = np.array(keys)

    # Part 1
    start     = time.perf_counter()
    n_pairs   = ((locks.reshape(-1,1,5) + keys) <= 5).all(axis=-1).sum()
    elapsed   = time.perf_counter() - start
    print(f'Part 1: {n_pairs} [t={(elapsed)*1000:.3f}ms]')

    # Part 2 - N/A

################################################################################
def parse(lines: str) -> tuple[bool, list[int]]:
    return (
        lines[0] == '#',
        [col.count('#')-1 for col in zip(*lines.split())],
    )

################################################################################
if __name__ == "__main__":
    main()
