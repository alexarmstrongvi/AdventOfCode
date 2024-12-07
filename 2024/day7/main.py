#!/usr/bin/env python
# Standard library
import logging
import time
from collections.abc import Callable, Iterable, Sequence
from functools import reduce
from itertools import product, starmap
from math import floor, log10
from operator import add, mul

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
    calibration_equations = [parse(line) for line in text.splitlines()]

    # Part 1
    start = time.perf_counter()
    total = sum(
        test_val for test_val, nums in calibration_equations
        if could_be_true(test_val, nums, ops = (add, mul))
    )
    elapsed = time.perf_counter() - start
    print(f'Part 1: {total} [t={elapsed*1000:.3f}ms]')

    # Part 2
    start = time.perf_counter()
    total = sum(
        test_val for test_val, nums in calibration_equations
        if could_be_true(test_val, nums, ops = (add, mul, int_concat))
    )
    elapsed = time.perf_counter() - start
    print(f'Part 2: {total} [t={elapsed:.3f}sec]')

################################################################################
BinaryIntOp = Callable[[int, int], int]
def could_be_true(
    test_val: int,
    nums    : Sequence[int],
    ops     : Iterable[BinaryIntOp],
) -> bool:
    # Option 1: Procedural - Brute Force
    # ops_permutations = product(ops, repeat=len(nums)-1)
    # for ops_permutation in ops_permutations:
    #     total = nums[0]
    #     for op, num in zip(ops_permutation, nums[1:]):
    #         total = op(total,num)
    #         # Early exit (negligable performance change)
    #         # if total > test_val:
    #         #     break
    #     if total == test_val:
    #         return True
    # return False

    # Option 2: Functional - Brute Force (2X slower than option 1)
    # ops_permutations = product(ops, repeat=len(nums)-1)
    # produces_test_val = lambda ops_permutation : test_val == star_reduce(
    #     func     = lambda acc, op, num : op(acc, num),
    #     iterable = zip(ops_permutation, nums[1:]),
    #     initial  = nums[0],
    # )
    # return any(map(produces_test_val, ops_permutations))

    # Option 3: Dynamic + Procedural (4-5X faster than option 1)
    # results = {nums[0]}
    # for n in nums[1:]:
    #     intermediate_results = set()
    #     for r, op in product(results, ops):
    #         x = op(r, n)
    #         # ASSUMPTION: All ops return a result larger than the inputs
    #         if x <= test_val:
    #             intermediate_results.add(x)
    #     results = intermediate_results

    # Option 4: Dynamic + Functional
    apply_all_ops = lambda acc, num : (
        # ASSUMPTION: All ops return a result larger than the inputs
        filter(lambda x : x <= test_val,
            starmap(lambda r, op : op(r, num),
                product(acc, ops)
    )))
    results = set(reduce(apply_all_ops, nums[1:], {nums[0]}))

    return test_val in results

def star_reduce(func, iterable, initial):
    return reduce(lambda acc, args : func(acc, *args), iterable, initial)

def int_concat(a: int, b: int) -> int:
    return a * (10**n_digits(b)) + b

def n_digits(x: int) -> int:
    return floor(log10(abs(x))) + 1 if x != 0 else 1

def parse(line: str) -> tuple[int, list[int]]:
    test_val, nums = line.split(':')
    test_val = int(test_val)
    nums = [int(x) for x in nums.split()]
    return test_val, nums


################################################################################
if __name__ == "__main__":
    main()
