#!/usr/bin/env python
# Standard library
import logging
import re
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

    # Solution

    # Part 1
    start = time.perf_counter()
    regex = re.compile(r"mul\((\d{1,3}),(\d{1,3})\)")
    total = sum(int(x)*int(y) for x,y in regex.findall(text))
    elapsed = time.perf_counter() - start
    print(f'Part 1: {total} [t={elapsed*1000:.3f}ms]')

    # Part 2
    start = time.perf_counter()
    regex = re.compile(r"""
        (?:
             mul\((\d{1,3}),(\d{1,3})\)
             |(do\(\))
             |(don't\(\))
        )
    """, re.VERBOSE) 
    total = 0
    is_enabled = True
    for match in regex.finditer(text):
        x,y,do,dont = match.groups()
        if do:
            is_enabled = True
            continue
        elif dont:
            is_enabled = False
            continue
        if is_enabled: 
            total += int(x) * int(y)
    elapsed = time.perf_counter() - start
    print(f'Part 2: {total} [t={elapsed*1000:.3f}ms]')

if __name__ == "__main__":
    main()
