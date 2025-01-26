#!/usr/bin/env python
"""
Red-Nosed Reports
=================

# Example input:
7 6 4 2 1
1 2 7 8 9
9 7 6 2 1
1 3 2 4 5
8 6 4 4 1
1 3 6 7 9

Part 1: 2 safe reports
Part 2: 4 tolerable reports
"""
# Standard library
from collections.abc import Sequence
import itertools
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

    # Solution
    reports = [[int(n) for n in l.split()] for l in text.splitlines()]

    # Part 1
    start   = time.perf_counter()
    n       = sum(map(is_safe_report, reports))
    elapsed = time.perf_counter() - start
    print('Part 1:', n, f'[{elapsed*1000:.3f}ms]')

    # Part 2
    start   = time.perf_counter()
    n = sum(map(is_tolerable_report, reports))
    elapsed = time.perf_counter() - start
    print('Part 2:', n, f'[{elapsed*1000:.3f}ms]')

################################################################################
def is_safe_report(nums: Sequence[int]) -> bool:
    if len(nums) <= 1:
        return True
    is_increasing = nums[0] < nums[1]
    for x,y in itertools.pairwise(nums):
        if not (1 <= abs(y-x) <= 3):
            return False
        if (x<y) != is_increasing:
            return False
    return True

def is_tolerable_report(nums: Sequence[int]) -> bool:
    if len(nums) <= 2:
        return True
    return (
        _is_tolerable_report_increasing(nums)
        or
        _is_tolerable_report_increasing(nums[::-1])
    )

def _is_tolerable_report_increasing(nums: Sequence[int]) -> bool:
    '''
    Examples
    ========
    >>> _is_tolerable_report_increasing([1,2,4,7])
    True
    >>> _is_tolerable_report_increasing([1,2,3,9])
    True
    >>> _is_tolerable_report_increasing([9,1,2,3])
    True
    >>> _is_tolerable_report_increasing([9,1,2,9])
    False
    '''
    found_bad_level = False
    is_safe = lambda x, y: 1 <= y-x <= 3
    i = 0
    while i+1 < len(nums):
        if is_safe(nums[i], nums[i+1]):
            i += 1
            continue
        elif found_bad_level:
            return False
        elif i+2 == len(nums):
            return True
        found_bad_level = True

        # Determine if i or i+1 should be dropped
        if is_safe(nums[i], nums[i+2]): # drop i+1
            i += 2
            continue
        elif i == 0 and is_safe(nums[i+1], nums[i+2]): # drop i
            i += 2
            continue
        elif i != 0 and is_safe(nums[i-1], nums[i+1]): # drop i
            i += 1
            continue
        return False
    return True


if __name__ == "__main__":
    main()
