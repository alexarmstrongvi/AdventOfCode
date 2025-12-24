#!/usr/bin/env python
"""Day 2: Gift Shop."""

# Standard library
import logging
import math
import time
from typing import cast

# 1st party
import aoc_utils as aoc

log = logging.getLogger("AoC")


################################################################################
def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)
    id_ranges = [tuple(r.rstrip().split("-")[:2]) for r in text.split(",")]
    id_ranges = cast("list[tuple[str, str]]", id_ranges)

    # Part 1
    start = time.perf_counter()
    total = part01(id_ranges)
    elapsed = time.perf_counter() - start
    log.info("Part 1: %d [%.3fms]", total, elapsed * 1000)

    # Part 2
    start = time.perf_counter()
    total = part02(id_ranges)
    elapsed = time.perf_counter() - start
    log.info("Part 2: %d [%.3fms]", total, elapsed * 1000)

    ####################################
    # Part 1: Do everything with integer arithmetic
    start = time.perf_counter()
    total = part01_int(id_ranges)
    elapsed = time.perf_counter() - start
    log.info("Part 1 (int-only): %d [%.3fms]", total, elapsed * 1000)


def part01(id_ranges: list[tuple[str, str]]) -> int:
    total = 0
    for id_min, id_max in split_id_ranges(id_ranges):
        n_digits = len(id_min)
        if n_digits % 2 == 1:
            continue
        pattern_size = n_digits // 2
        pattern_i = id_min[:pattern_size]
        pattern_f = id_max[:pattern_size]

        # String comparisons work because they are the same length
        if pattern_i * 2 < id_min:
            pattern_i = str(int(pattern_i) + 1)
        if pattern_f * 2 > id_max:
            pattern_f = str(int(pattern_f) - 1)

        total += sum(
            int(str(pattern) * 2)
            for pattern in range(int(pattern_i), int(pattern_f) + 1)
        )
    return total


def part01_int(id_ranges: list[tuple[str, str]]) -> int:
    total = 0
    n_repeats = 2
    id_ranges_int = [(int(x), int(y)) for x, y in split_id_ranges(id_ranges)]
    for id_min, id_max in id_ranges_int:
        n_digits = math.floor(math.log10(id_min)) + 1
        if n_digits % n_repeats != 0:
            continue
        pattern_size = n_digits // n_repeats
        drop_pow = 10 ** (n_digits - pattern_size)
        repeat = (10**n_digits - 1) // (10**pattern_size - 1)
        pattern_i = id_min // drop_pow
        pattern_f = id_max // drop_pow

        if pattern_i * repeat < id_min:
            pattern_i += 1
        if pattern_f * repeat > id_max:
            pattern_f -= 1

        total += sum(pattern * repeat for pattern in range(pattern_i, pattern_f + 1))
    return total


def part02(id_ranges: list[tuple[str, str]]) -> int:
    invalid_ids: set[int] = set()
    for id_min, id_max in split_id_ranges(id_ranges):
        n_digits = len(id_min)
        if n_digits == 1:
            continue
        for n_repeats in [*get_prime_factors(n_digits), n_digits]:
            pattern_size = n_digits // n_repeats
            pattern_i = id_min[:pattern_size]
            pattern_f = id_max[:pattern_size]

            if pattern_i * n_repeats < id_min:
                pattern_i = str(int(pattern_i) + 1)
            if pattern_f * n_repeats > id_max:
                pattern_f = str(int(pattern_f) - 1)

            invalid_ids.update(
                {
                    int(str(pattern) * n_repeats)
                    for pattern in range(int(pattern_i), int(pattern_f) + 1)
                },
            )
    return sum(invalid_ids)


################################################################################
def split_id_ranges(id_ranges: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Split ranges that cover integers with different numbers of digits.

    Returns:
        ID ranges where all numbers have the same number of digits.

    """
    res = []
    for id_min, id_max in id_ranges:
        n_min = len(id_min)
        n_max = len(id_max)
        if n_min == n_max:
            res.append((id_min, id_max))
            continue
        res.extend(
            [
                (id_min, "9" * n_min),
                *[("1" + "0" * n, "9" * (n + 1)) for n in range(n_min + 1, n_max)],
                ("1" + "0" * (n_max - 1), id_max),
            ],
        )
    return res


def get_prime_factors(n: int) -> list[int]:
    return [x for x in range(2, n // 2 + 1) if n % x == 0]


################################################################################
if __name__ == "__main__":
    main()
