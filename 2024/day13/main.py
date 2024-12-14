#!/usr/bin/env python
# Standard library
import logging
import re
import time
from collections.abc import Iterable
from typing import NamedTuple

# 3rd party
import numpy as np

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# Claw Contraption
#
# Example input:
# Button A: X+94, Y+34
# Button B: X+22, Y+67
# Prize: X=8400, Y=5400
#
# Button A: X+26, Y+66
# Button B: X+67, Y+21
# Prize: X=12748, Y=12176
#
# Button A: X+17, Y+86
# Button B: X+84, Y+37
# Prize: X=7870, Y=6450
#
# Button A: X+69, Y+23
# Button B: X+27, Y+71
# Prize: X=18641, Y=10279
#
# Part 1: 480 
# Part 2: 875318608908

CONVERSION_FACTOR = 10**13
COST_A = 3
COST_B = 1

def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    machine_confs = [parse(lines) for lines in text.split('\n\n')]

    # Part 1
    start = time.perf_counter()
    n_tokens1 = sum(drop_none(compute_min_cost_to_win(c) for c in machine_confs))
    elapsed = time.perf_counter() - start
    print(f'Part 1: {n_tokens1} [t={elapsed*1000:.3f}ms]')

    # Part 2
    for conf in machine_confs:
        conf.prize_loc[:] = conf.prize_loc + CONVERSION_FACTOR
    start = time.perf_counter()
    n_tokens2 = sum(drop_none(compute_min_cost_to_win(c) for c in machine_confs))
    elapsed = time.perf_counter() - start
    print(f'Part 2: {n_tokens2} [t={elapsed*1000:.3f}ms]')

    ############################################################################# 
    # Alternate solutions
    ############################################################################# 
    # Vectorize to solve all configurations with one numpy call (20X faster)
    machine_confs = np.array(
        re.findall(r'[-+]?\d+', text), 
        dtype=np.int64
    ).reshape(-1,3,2).transpose(0,2,1)
    button_vec = machine_confs[:,:,:2]
    prize_loc  = machine_confs[:,:,2]

    start = time.perf_counter()
    n_tokens = compute_min_cost_to_win_vectorized(button_vec, prize_loc)
    elapsed = time.perf_counter() - start
    assert n_tokens == n_tokens1
    print(f'Part 1 [vec]: [t={elapsed*1000:.3f}ms]')

    prize_loc += CONVERSION_FACTOR
    start = time.perf_counter()
    n_tokens = compute_min_cost_to_win_vectorized(button_vec, prize_loc)
    elapsed = time.perf_counter() - start
    assert n_tokens == n_tokens2
    print(f'Part 2 [vec]: [t={elapsed*1000:.3f}ms]')

################################################################################
class MachineConf(NamedTuple):
    A_move    : np.ndarray
    B_move    : np.ndarray
    prize_loc : np.ndarray

def parse(lines: str) -> MachineConf:
    match = re.fullmatch(r'''
        Button\ A:\ X([-+]\d+),\ Y([-+]\d+)\n
        Button\ B:\ X([-+]\d+),\ Y([-+]\d+)\n
        Prize:\ X=(\d+),\ Y=(\d+)\n?
    ''', lines, re.VERBOSE)
    if match is None:
        raise ValueError('Failed to parse:\n%s', lines)
    nums = np.array(match.groups(), dtype=np.int64).reshape(3,2)
    return MachineConf(*nums)

def compute_min_cost_to_win(conf: MachineConf) -> int | None:
    # Linear Algebra
    button_vec = np.stack([conf.A_move, conf.B_move], axis=1)
    nA, nB = np.linalg.solve(button_vec, conf.prize_loc).round().astype(np.int64)
    nearest_loc = nA * conf.A_move + nB * conf.B_move 
    if not np.all(nearest_loc == conf.prize_loc):
        return None
    return COST_A * nA + COST_B * nB

def compute_min_cost_to_win_vectorized(
    button_vec : np.ndarray, 
    prize_loc  : np.ndarray,
) -> int:
    cost = np.array([COST_A, COST_B])
    n_presses = (
        np.linalg.solve(
            button_vec, 
            prize_loc[:,:,np.newaxis],
        )
        .round()
        .astype(np.int64)
        .squeeze()
    )
    nearest_loc = (button_vec * n_presses[:,np.newaxis,:]).sum(axis=2)
    prize_is_won = (prize_loc == nearest_loc).all(axis=1)
    n_tokens = int((n_presses[prize_is_won] * cost).sum())
    return n_tokens

def drop_none[T](iterable: Iterable[T | None]) -> Iterable[T]:
    return (x for x in iterable if x is not None)

################################################################################

################################################################################
if __name__ == "__main__":
    main()
