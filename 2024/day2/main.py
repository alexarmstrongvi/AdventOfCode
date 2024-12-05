#!/usr/bin/env python
# Standard library
from collections.abc import Sequence
import itertools
import logging

# 1st party
import aoc_utils as aoc

log = logging.getLogger('AoC')

################################################################################
def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Setup
    reports = [[int(n) for n in l.split()] for l in text.splitlines()]

    # Solution
    n = sum(map(is_safe_report, reports))
    print('Part 1:', n)

    n = sum(map(is_tolerable_report, reports))
    print('Part 2:', n)

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
