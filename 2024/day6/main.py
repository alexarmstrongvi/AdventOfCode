#!/usr/bin/env python
# Standard library
import logging
import multiprocessing as mp
import time

# 3rd party
import numpy as np
from tqdm import tqdm

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')
Location = tuple[int, int]

################################################################################
def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    lines      = text.splitlines()
    map        = np.array(lines).view('U1').reshape(len(lines),-1)
    start_pos  = np.hstack(np.where(map == '^'))
    start_step = np.array([-1,0])

    # Part 1
    start = time.perf_counter()
    positions, is_stuck = predict_guards_route(map, start_pos, start_step)
    assert not is_stuck
    elapsed = time.perf_counter() - start
    print(f'Part 1: {len(positions)} [t={elapsed*1000:.3f}ms]')

    # Part 2
    start = time.perf_counter()
    # Only test places the guard will eventually get to
    obstructions_to_test = positions - {to_loc(start_pos)}
    obstruction_positions = []
    for pos in tqdm(obstructions_to_test):
        is_stuck = test_new_obstruction(pos, map, start_pos, start_step)
        if not is_stuck:
            continue
        obstruction_positions.append(pos)
        if len(obstruction_positions) % 100 == 0:
            log.info('Obstruction %d found: %s', len(obstruction_positions), pos)

    n_obstructions = len(obstruction_positions)
    elapsed = time.perf_counter() - start
    print(f'Part 2: {len(obstruction_positions)} [t={elapsed*1000:.3f}ms]')

    ############################################################################
    # Alternate solutions
    ############################################################################
    # Part 2 Multiprocessing (5X improvement using 8-cores)
    start = time.perf_counter()
    obstructions_to_test = positions - {to_loc(start_pos)}
    obstruction_positions = []
    n_workers = mp.cpu_count() - 1 # Leave CPU for MainProcess
    with mp.Pool(
        processes   = n_workers,
        initializer = initializer,
        initargs    = (map, start_pos, start_step)
    ) as pool:
        iresults = pool.imap_unordered(
            func      = _test_new_obstruction_mp,
            iterable  = obstructions_to_test,
            # chunksize = 10, # No major performance impact
        )
        for pos, guard_is_stuck in tqdm(iresults, total=len(obstructions_to_test)):
            if not guard_is_stuck:
                continue
            obstruction_positions.append(pos)

    elapsed = time.perf_counter() - start
    assert len(obstruction_positions) == n_obstructions
    print(f'Part 2 [mp]: [t={elapsed*1000:.3f}ms]')

################################################################################
def predict_guards_route(map, start_pos, start_step) -> tuple[set[Location], bool]:
    m,n           = map.shape
    is_obstacle   = lambda p : map[p[0],p[1]] == '#'
    outside_area  = lambda p : not (0 <= p[0] < m and 0 <= p[1] < n)
    turn_right    = lambda p : np.array((p[1], -p[0]))
    to_state      = lambda p,s : (to_loc(p), to_loc(s))
    states        = {to_state(start_pos, start_step)}
    stuck_in_loop = lambda p,s : to_state(p,s) in states

    pos      = start_pos.copy() # Must copy since lambdas hold a reference
    step     = start_step.copy()
    is_stuck = False
    while True:
        next_pos = pos + step
        if outside_area(next_pos):
            log.debug('Guard left the area')
            break
        elif stuck_in_loop(next_pos, step):
            log.debug('Gaurd stuck in a loop')
            is_stuck = True
            break
        elif is_obstacle(next_pos):
            # log.debug('Turning to the right')
            step = turn_right(step)
            continue
        pos = next_pos
        states.add(to_state(pos, step))

    positions = {x[0] for x in states}
    return positions, is_stuck

def test_new_obstruction(
    obstruction_pos: tuple[int, int],
    map            : np.ndarray,
    start_pos      : np.ndarray,
    start_step     : np.ndarray,
) -> bool:
    i,j = obstruction_pos
    map[i, j] = '#' # Add obstacle
    _, is_stuck = predict_guards_route(map, start_pos, start_step)
    map[i, j] = '.' # Remove obstacle
    return is_stuck

_MAP = None
_START_POS = None
_START_STEP = None
def initializer(
    map        : np.ndarray,
    start_pos  : np.ndarray,
    start_step : np.ndarray,
) -> None:
    """Avoid these being copied for each worker task"""
    global _MAP, _START_POS, _START_STEP
    _MAP = map.copy()
    _START_POS = start_pos.copy()
    _START_STEP = start_step.copy()

def _test_new_obstruction_mp(
    obstruction_pos: tuple[int, int]
) -> tuple[tuple[int,int], bool]:
    # GLOBAL _MAP, _START_POS, _START_STEP
    assert _MAP is not None
    assert _START_POS is not None
    assert _START_STEP is not None
    return (
        obstruction_pos,
        test_new_obstruction(obstruction_pos, _MAP, _START_POS, _START_STEP)
    )

def to_loc(arr: np.ndarray) -> Location:
    return int(arr[0]), int(arr[1])
################################################################################
if __name__ == "__main__":
    main()
