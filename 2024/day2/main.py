#!/usr/bin/env python
# Standard library
from collections.abc import Sequence
from typing import Literal
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
    lines = aoc.read_input(args.input).splitlines()
    if args.max_lines is not None:
        lines = lines[:args.max_lines]

    statuses = [
        compute_safety_status(nums)
        for nums in map(lambda s : list(map(int, s.split())), lines)
    ]

    if log.isEnabledFor(logging.INFO):
        for status, line in zip(statuses, lines):
            s = f'S{status}' if status <= 1 else f'U{status}'
            log.info(f'%2s | %s', s, line)

    n_perfect_reports = sum(s == 0 for s in statuses)
    print('Part 1:', n_perfect_reports)
    n_safe_reports    = sum(s <= 1 for s in statuses)
    print('Part 2:', n_safe_reports)

SafetyStatus = Literal[0,1,2] # 0/1 = 0/1 bad level; 2 = 2+ bad levels
def compute_safety_status(nums: Sequence[int]) -> SafetyStatus:
    if len(nums) <= 1:
        return 0
    return min(
        _compute_safety_status_increasing(nums),
        _compute_safety_status_increasing(nums[::-1]),
    )

def _compute_safety_status_increasing(nums: Sequence[int]) -> SafetyStatus:
    '''
    Examples
    ========
    _compute_safety_status_increment([1,2,4,7]) == 0
    _compute_safety_status_increment([1,2,3,9]) == 1
    _compute_safety_status_increment([9,1,2,3]) == 2
    '''
    found_bad_level = False
    is_safe = lambda x, y: 1 <= y-x <= 3
    i = 0
    n_loop = 0
    log.debug('Checking %s', nums)
    while i+1 < len(nums):
        log.debug('i = %d', i)
        n_loop += 1
        if n_loop > 1_000:
            log.warning('Possible infinite loop. Exiting after 1M loops')
            break

        if is_safe(nums[i], nums[i+1]):
            log.debug('Safe level: %s -> %s', nums[i], nums[i+1])
            i += 1
            continue
        elif found_bad_level:
            return 2
        elif i+2 == len(nums):
            return 1
        log.debug('Unsafe level: %s -> %s', nums[i], nums[i+1])
        found_bad_level = True

        # Determine if i or i+1 should be dropped
        if is_safe(nums[i], nums[i+2]): # drop i+1
            log.debug('Safe level: %s -> %s', nums[i], nums[i+2])
            i += 2
            continue
        elif i == 0 and is_safe(nums[i+1], nums[i+2]): # drop i
            log.debug('Safe level: %s -> %s', nums[i-1], nums[i+1])
            i += 2
            continue
        elif i != 0 and is_safe(nums[i-1], nums[i+1]): # drop i
            log.debug('Safe level: %s -> %s', nums[i-1], nums[i+1])
            i += 1
            continue
        return 2
    return 1 if found_bad_level else 0

def has_no_bad_levels(nums: Sequence[int]) -> bool:
    return compute_safety_status(nums) == 0

# def has_no_bad_levels(nums: Sequence[int]) -> bool:
#     if len(nums) <= 1:
#         return True
#     is_increasing = nums[0] < nums[1]
#     for x,y in itertools.pairwise(nums):
#         diff = y-x
#         if not (1 <= abs(diff) <= 3):
#             return False
#         if (x<y) != is_increasing:
#             return False
#     return True

if __name__ == "__main__":
    main()
