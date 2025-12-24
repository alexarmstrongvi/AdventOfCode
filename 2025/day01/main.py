#!/usr/bin/env python
"""
Day 1: Secret Entrance
"""

# Standard library
import logging
import time

# 1st party
import aoc_utils as aoc

log = logging.getLogger('AoC')

################################################################################
def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    DIAL_SIZE = 100
    DIAL_START = 50

    # Part 1
    start = time.perf_counter()
    dial = DIAL_START
    n_zeros = 0;
    for line in text.splitlines():
        dial += parse_num_clicks(line)
        n_zeros += (dial % DIAL_SIZE == 0)
        dial %= DIAL_SIZE 
    elapsed = time.perf_counter() - start
    print('Part 1:', n_zeros, f'[{elapsed*1000:.3f}ms]')

    # Part 2
    start = time.perf_counter()
    dial = DIAL_START
    n_zeros = 0;
    for line in text.splitlines():
        dial_start = dial 
        dial += parse_num_clicks(line)
        n_zeros += (
            (dial == 0) 
            + (dial_start > 0 > dial) 
            + (abs(dial) // DIAL_SIZE)
        )
        dial %= DIAL_SIZE
    elapsed = time.perf_counter() - start
    print('Part 2:', n_zeros, f'[{elapsed*1000:.3f}ms]')

################################################################################
def parse_num_clicks(line: str) -> int:
    direction =  line[0]
    mag       =  int(line[1:])
    sign      =  -1 if direction == "L" else 1
    return sign * mag

if __name__ == "__main__":
    main()
