#!/usr/bin/env python
import logging
import time
from functools import lru_cache, partial
from itertools import starmap

# 3rd party
import numpy as np

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
    lines = text.splitlines()
    arr = np.array(lines).view('U1').reshape(len(lines), -1)

    # Part 1
    start = time.perf_counter()
    n_xmas  = sum(starmap(partial(count_xmas, arr), zip(*np.where(arr=='X'))))
    elapsed = time.perf_counter() - start
    print(f'Part 1: {n_xmas} [t={elapsed*1000:.3f}ms]')

    # Part 2
    start = time.perf_counter()
    n_x_mas = sum(starmap(partial(is_x_mas, arr),   zip(*np.where(arr=='A'))))
    elapsed = time.perf_counter() - start
    print(f'Part 2: {n_x_mas} [t={elapsed*1000:.3f}ms]')

   ########################################
   # Alternate solution
   ########################################
   # Part 1 & 2: Procedural with single iteration
   # - No noticable speed improvement
    start = time.perf_counter()
    n_xmas_ = n_x_mas_ = 0
    for (i,j), c in np.ndenumerate(arr):
        if c == 'X':
            n_xmas_ += count_xmas(arr, i, j)
        if c == 'A':
            n_x_mas_ += is_x_mas(arr, i, j)
    elapsed = time.perf_counter() - start
    assert n_xmas_ == n_xmas
    assert n_x_mas_ == n_x_mas
    print(f'Part 1 & 2: [t={elapsed*1000:.3f}ms]')

################################################################################
def count_xmas(arr, i,j) -> int:
    rel_coords = generate_8compass_coords(len('XMAS'))
    return count_matches(arr, i, j, rel_coords, 'XMAS')

def is_x_mas(arr, i,j) -> int:
    rel_coords = generate_x_coords(len('MAS'))
    count = count_matches(arr, i, j, rel_coords, 'MAS')
    return count == 2

def count_matches(arr, i, j, rel_coords, s) -> int:
    assert rel_coords.shape[-1] == len(s)
    # Center coordinates to check around (i,j)
    i_idxs,j_idxs = rel_coords + np.array([i,j]).reshape(-1,1,1)
    # Select directions that do not extend beyond array bounds
    m,n  = arr.shape
    i_idxs, j_idxs = drop_out_of_bound_idxs(i_idxs, j_idxs, m, n)
    # Count matches to search string
    search_str = np.array(list(s))
    check_strs = arr[i_idxs, j_idxs]
    count = int((check_strs == search_str).all(axis=1).sum())
    return count

def drop_out_of_bound_idxs(i_idxs, j_idxs, m, n) -> tuple[np.ndarray, np.ndarray]:
    in_bounds = (
        ((0 <= i_idxs) & (i_idxs < m)).all(axis=1)
        &
        ((0 <= j_idxs) & (j_idxs < n)).all(axis=1)
    )
    return i_idxs[in_bounds], j_idxs[in_bounds]

@lru_cache(maxsize=1)
def generate_x_coords(size):
    assert size%2==1
    # i_idxs = [
    #     [-1, 0,  1], # Up   to the right
    #     [-1, 0,  1], # Down to the right
    #     [ 1, 0, -1], # Down to the left
    #     [ 1, 0, -1], # Up   to the left
    # ]
    a = np.arange(size) - (size//2) # Relative coords are centered
    i_coords = a * np.array([1,1,-1,-1]).reshape(-1,1)
    j_coords = np.roll(i_coords, 1, axis=0)
    return np.stack([i_coords, j_coords])

@lru_cache(maxsize=1)
def generate_8compass_coords(size):
    # i_idxs = [
    #     [0, -1, -2, -3], # Up
    #     [0, -1, -2, -3], # Right-Up
    #     [0,  0,  0,  0], # Right
    #     [0,  1,  2,  3], # Right-Down
    #     [0,  1,  2,  3], # Down
    #     [0,  1,  2,  3], # Left-Down
    #     [0,  0,  0,  0], # Left
    #     [0, -1, -2, -3], # Left-Up
    # ]
    a = np.arange(size)
    i_coords = a * np.array([-1,-1,0,1,1,1,0,-1]).reshape(-1,1)
    j_coords = np.roll(i_coords, 2, axis=0)
    return np.stack([i_coords, j_coords])

if __name__ == "__main__":
    main()
