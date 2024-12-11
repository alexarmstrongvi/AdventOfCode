#!/usr/bin/env python
# Standard library
import logging
import time
from math import log10, floor
from functools import lru_cache, reduce
from operator import add

# 3rd party
from tqdm import tqdm

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# Plutonian Pebbles
#
# Example input:
# 125 17
#
# Solutions
# Part 1: 55312 stones
# Part 2: 65601038650482 stones
################################################################################
def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    input_stones = [int(x) for x in text.split()]

    # Part 1
    stones   = input_stones.copy()
    start    = time.perf_counter()
    n_stones = count_after_blinks(stones, n_blinks = 25)
    elapsed  = time.perf_counter() - start
    print(f'Part 1: {n_stones} [t={elapsed*1000:.3f}ms]')

    # Part 2
    stones   = input_stones.copy()
    start    = time.perf_counter()
    n_stones = count_after_blinks(stones, n_blinks = 75)
    elapsed  = time.perf_counter() - start
    print(f'Part 2: {n_stones} [t={elapsed*1000:.3f}ms]')

################################################################################
def count_after_blinks(stones: list[int], n_blinks: int) -> int:
    return sum(map(lambda x : _count(x, n_blinks), stones))

@lru_cache(maxsize=2**32)
def _count(val: int, n_blinks: int) -> int:
    if n_blinks == 0:
        n_stones = 1
    elif val == 0:
        n_stones = _count(1, n_blinks-1)
    elif is_even(n_digits := count_digits(val)):
        nl, nr = split_int(val, n_digits)
        n_stones = _count(nr, n_blinks-1) + _count(nl, n_blinks-1)
    else:
        n_stones = _count(val * 2024, n_blinks-1)
    log.debug('%d blinks turns %d into %d stones', n_blinks, val, n_stones)
    return n_stones

def is_even(n: int) -> bool:
    return n % 2 == 0

def count_digits(x: int) -> int:
    return floor(log10(abs(x))) + 1 if x != 0 else 1

def split_int(x: int, n_digits: int) -> tuple[int, int]:
    return divmod(x, 10**(n_digits//2))
    
################################################################################
if __name__ == "__main__":
    main()
