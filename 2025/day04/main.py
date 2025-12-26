#!/usr/bin/env python

# Standard library
import logging
import time
from typing import Annotated

# 3rd party
import numpy as np
from numpy.typing import NDArray
from scipy.signal import convolve2d

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger("AoC")

# Type aliases
ArrStrU1 = Annotated[NDArray[np.str_], "U1"]


################################################################################
def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)

    # Get data
    text  = aoc.read_input(args.input)
    lines = text.splitlines()
    data  = np.array(lines).view("U1").reshape(len(lines), -1)

    # Part 1
    start = time.perf_counter()
    n_rolls = part01(data)
    elapsed = time.perf_counter() - start
    log.info("Part 1: %d [%.3fms]", n_rolls, elapsed * 1000)

    # Part 2
    start = time.perf_counter()
    n_rolls = part02(data)
    elapsed = time.perf_counter() - start
    log.info("Part 2: %d [%.3fms]", n_rolls, elapsed * 1000)


def part01(data: ArrStrU1) -> int:
    is_roll = data == "@"
    conv = np.array(
        [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ],
        dtype=np.uint8,
    )
    max_rolls = 4
    return np.sum(is_roll * convolve2d(is_roll, conv, mode="same") < max_rolls)


def part02(data: ArrStrU1) -> int:
    is_roll = data == "@"
    conv = np.array(
        [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ],
        dtype=np.uint8,
    )
    max_rolls = 4
    n_rolls = 0
    while True:
        is_accessible = is_roll * (convolve2d(is_roll, conv, mode="same") < max_rolls)
        n = is_accessible.sum()
        if n == 0:
            break
        n_rolls += n
        is_roll ^= is_accessible
    return n_rolls


################################################################################
if __name__ == "__main__":
    main()
