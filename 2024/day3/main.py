#!/usr/bin/env python
# Standard library
from collections.abc import Sequence
from typing import Literal
import itertools
import logging
import re

# 1st party
import aoc_utils as aoc

log = logging.getLogger('AoC')

################################################################################
def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)
    log.debug('%d chars read in', len(text))

    # Solution
    regex = re.compile(r"""
        (?:
             mul\((\d{1,3}),(\d{1,3})\)
             |(do\(\))
             |(don't\(\))
        )
    """, re.VERBOSE) 
    is_enabled = True
    total_pt1 = total_pt2 = 0
    for match in regex.finditer(text):
        x,y,do,dont = match.groups()
        if do:
            is_enabled = True
            continue
        elif dont:
            is_enabled = False
            continue

        result = int(x) * int(y)
        total_pt1 += result
        if is_enabled: 
            total_pt2 += result

    print('Part 1:', total_pt1)
    print('Part 2:', total_pt2)

if __name__ == "__main__":
    main()
