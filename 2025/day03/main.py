#!/usr/bin/env python
"""Day 2: Gift Shop."""

# Standard library
import logging
import time

# 3rd party
import numpy as np
from numpy.typing import NDArray

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger("AoC")

# Type aliases
ArrU8 = NDArray[np.uint8]


################################################################################
def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)
    lines = text.splitlines()
    data = np.array(lines).view("U1").astype(np.int8).reshape(len(lines), -1)

    # Part 1
    start = time.perf_counter()
    total = get_max_joltage_pt1(data)
    elapsed = time.perf_counter() - start
    log.info("Part 1: %d [%.3fms]", total, elapsed * 1000)

    # Part 2
    start = time.perf_counter()
    total = sum(get_max_joltage_pt2(row, n=12) for row in data)
    elapsed = time.perf_counter() - start
    log.info("Part 2: %d [%.3fms]", total, elapsed * 1000)

    # Alternate approaches
    start = time.perf_counter()
    total = sum(get_max_joltage_pt2b(row) for row in data)
    elapsed = time.perf_counter() - start
    log.info("Part 2 (B): %d [%.3fms]", total, elapsed * 1000)


def get_max_joltage_pt1(data: NDArray[np.uint8]) -> int:
    argmax = data[:, :-1].argmax(axis=1)
    return sum(
        int(row[i]) * 10 + int(row[i + 1:].max())
        for i, row in zip(argmax, data, strict=True)
    )


def get_max_joltage_pt2(digits: NDArray[np.uint8], n: int) -> int:
    total = 0
    powers10 = np.power(10, np.arange(n))
    while 0 < n < len(digits):
        stop   = len(digits) - (n - 1 if n > 1 else 0)
        argmax = digits[:stop].argmax()
        total += digits[argmax] * powers10[n - 1]
        digits = digits[argmax + 1:]
        n -= 1
    if n > 0:
        total += np.sum(digits * powers10[:n][::-1])
    return total


# Stack-based approach that's probably faster in compiled languages.
# numba.njit gives ~8x speedup but numpy solution is still faster when also jit compiled.
def get_max_joltage_pt2b(digits: NDArray[np.uint8]) -> int:
    k = len(digits) - 12
    stack = []
    for d in digits:
        while stack and k > 0 and stack[-1] < d:
            stack.pop()
            k -= 1
        stack.append(d)
    result = stack[:12]
    return sum(int(x) * 10 ** (len(result) - i - 1) for i, x in enumerate(result))


################################################################################
if __name__ == "__main__":
    main()
