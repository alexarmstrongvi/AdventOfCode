#!/usr/bin/env python
# Standard library
import logging
import math
import re
import time
from collections.abc import Iterable
from functools import reduce
from typing import NamedTuple

# 3rd party
import numpy as np
import scipy.signal
from tqdm import tqdm

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# Restroom Reboot
#
# Example input:
# p=0,4 v=3,-3
# p=6,3 v=-1,-3
# p=10,3 v=-1,2
# p=2,0 v=2,-1
# p=0,0 v=1,3
# p=3,0 v=-2,-2
# p=7,6 v=-1,-3
# p=3,0 v=-1,-2
# p=9,3 v=2,3
# p=7,3 v=-1,2
# p=2,4 v=2,-3
# p=9,5 v=-3,-3
#
# Part 1:
# Part 2:

N_SECONDS = 100

def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    robots = [parse(l) for l in text.splitlines()]
    if len(robots) == 12:
        bathroom_shape = (11, 7)
    elif len(robots) == 500:
        bathroom_shape = (101, 103)
    else:
        raise NotImplementedError('Unexpected input data')

    # Part 1
    start         = time.perf_counter()
    pfinal        = simulate_robots(robots, N_SECONDS, bathroom_shape)
    safety_factor = compute_safety_factor(pfinal, bathroom_shape)
    elapsed       = time.perf_counter() - start
    print(f'Part 1: {safety_factor} [t={elapsed*1000:.3f}ms]')

    # Part 2
    start   = time.perf_counter()
    times   = guess_easter_egg_times(robots, bathroom_shape)
    elapsed = time.perf_counter() - start
    t_str   = ','.join(map(str,times))
    print(f'Part 2: {t_str} [t={elapsed*1000:.3f}ms]')
    # # Visually verify which time has the easter egg
    # if log.isEnabledFor(logging.DEBUG):
    #     for t in times:
    #         pfinal = simulate_robots(robots, t, bathroom_shape)
    #         log.debug('t = %dsec\n%s', t, visualize_robots(pfinal, bathroom_shape))

    ############################################################################
    # Alternate solutions
    ############################################################################
    # Vectorized solution
    # - negligable improvement for part 1
    # - 10x improvement for part 2 guess methods and negligable improvements for
    #   guaranteed method
    bathroom_shape = np.array(bathroom_shape)
    robots = np.array(re.findall(r'-?\d+', text), np.int32).reshape(-1,2,2)
    p = robots[:,0]
    v = robots[:,1]

    start   = time.perf_counter()
    pfinal  = simulate_robots_vec(p, v, N_SECONDS, bathroom_shape)
    ans     = compute_safety_factor_vec(pfinal, bathroom_shape)
    elapsed = time.perf_counter() - start
    assert ans == safety_factor
    print(f'Part 1 [vec]: [t={elapsed*1000:.3f}ms]')

    start      = time.perf_counter()
    cycle_time = np.lcm.reduce((np.lcm(v, bathroom_shape) // v).flatten())
    seconds    = np.arange(cycle_time).reshape(-1,1,1)
    pfinal     = simulate_robots_vec(p, v, seconds, bathroom_shape)
    # Lucky guess: Xmas tree occurs where variance is minimized
    # assert times[0] == pfinal.var(axis=1).max(axis=1).argmin()
    # Guaranteed
    bathroom    = np.zeros((cycle_time, *bathroom_shape[::-1]))
    t_idx       = np.broadcast_to(np.arange(cycle_time)[:,np.newaxis], (cycle_time, len(robots)))
    bathroom[t_idx, pfinal[:,:,1], pfinal[:,:,0]] = 1
    log.info('Kernel correlation over %d time steps. This takes 30-60sec.', cycle_time)
    correlation = scipy.ndimage.correlate(bathroom, TREE_KERNEL[np.newaxis,:,:])
    ans         = np.nonzero(correlation == TREE_KERNEL.sum())[0].tolist()
    elapsed     = time.perf_counter() - start
    assert len(set(ans) & set(times)) > 0 or len(ans) == 0
    print(f'Part 2 [vec]: [t={elapsed*1000:.3f}ms]')

################################################################################
Vector2D = tuple[int, int]
class Robot(NamedTuple):
    p : Vector2D
    v : Vector2D

def simulate_robots(
    robots: list[Robot],
    seconds: int,
    bathroom_shape : tuple[int, int]
) -> list[Vector2D]:
    return [
        (
            (r.p[0] + r.v[0] * seconds) % bathroom_shape[0],
            (r.p[1] + r.v[1] * seconds) % bathroom_shape[1],
        )
        for r in robots
    ]

def compute_safety_factor(positions: list[Vector2D], bathroom_shape: tuple[int, int]) -> int:
    quadrant_counts = [0,0,0,0]
    x_boundary, y_boundary = bathroom_shape[0]//2, bathroom_shape[1]//2
    for x,y in positions:
        if x < x_boundary:
            if y < y_boundary:
                quad = 0
            elif y > y_boundary:
                quad = 1
            else:
                continue
        elif x > x_boundary:
            if y < y_boundary:
                quad = 2
            elif y > y_boundary:
                quad = 3
            else:
                continue
        else:
            continue
        quadrant_counts[quad] += 1
    return math.prod(quadrant_counts)

def guess_easter_egg_times(
    robots: list[Robot],
    bathroom_shape: tuple[int, int]
) -> list[int]:
    # Determine time it takes for robots to return to starting position
    cycle_time = reduce(math.lcm,
        (math.lcm(
            math.lcm(abs(robot.v[0]), bathroom_shape[0]) // abs(robot.v[0]),
            math.lcm(abs(robot.v[1]), bathroom_shape[1]) // abs(robot.v[1]),
        ) for robot in robots)
    )

    min_var = float('inf')
    t_min_var = None
    t_no_overlap = []
    bathroom = np.zeros(bathroom_shape[::-1], dtype=np.uint32)
    kernal_match = TREE_KERNEL.sum()
    for t in tqdm(range(0, cycle_time+1)):
        pfinal = simulate_robots(robots, t, bathroom_shape)

        # Lucky guess 1: Xmas tree occurs where variance is minimized
        # var = max(
        #     statistics.variance(p[0] for p in pfinal),
        #     statistics.variance(p[1] for p in pfinal),
        # )
        # if var < min_var:
        #     min_var = var
        #     t_min_var = t

        # Lucky guess 2: Xmas tree occurs when no robots overlap
        # if len(robots) == len({r.p for r in robots}):
        #     t_no_overlap.append(t)

        # Guaranteed
        bathroom[:] = 0
        bathroom[to_index(pfinal)[::-1]] = 1
        correlation = scipy.signal.correlate2d(bathroom, TREE_KERNEL, mode='valid')
        if correlation.max() == kernal_match:
            return [t]

    possible_times = sorted(drop_none(set(t_no_overlap + [t_min_var])))
    return possible_times

def simulate_robots_vec(p, v, seconds, bathroom_shape):
    return (p + v * seconds) % bathroom_shape

def compute_safety_factor_vec(p: np.ndarray, bathroom_shape: np.ndarray) -> int:
    boundaries = bathroom_shape // 2
    masks = np.hstack([p < boundaries, p > boundaries])
    return int(((masks[:,[0,0,2,2]] & masks[:,[1,3,1,3]])).sum(axis=0).prod())

def parse(line: str) -> Robot:
    match = re.fullmatch(r'p=(-?\d+),(-?\d+) v=(-?\d+),(-?\d+)', line)
    if match is None:
        raise ValueError('Failed to parse: %s', line)
    px,py,vx,vy = match.groups()
    return Robot((int(px),int(py)), (int(vx),int(vy)))

def to_index(coords: list[tuple[int,...]]) -> tuple[list[int],...]:
    return tuple(list(x) for x in zip(*coords))

def drop_none[T](iterable : Iterable[T | None]) -> Iterable[T]:
    return (x for x in iterable if x is not None)

# Only know what this looks like after solving the problem with lucky guess
# methods
TREE_KERNEL=np.array([
    list('1111111111111111111111111111111'),
    list('1000000000000000000000000000001'),
    list('1000000000000000000000000000001'),
    list('1000000000000000000000000000001'),
    list('1000000000000000000000000000001'),
    list('1000000000000001000000000000001'),
    list('1000000000000011100000000000001'),
    list('1000000000000111110000000000001'),
    list('1000000000001111111000000000001'),
    list('1000000000011111111100000000001'),
    list('1000000000000111110000000000001'),
    list('1000000000001111111000000000001'),
    list('1000000000011111111100000000001'),
    list('1000000000111111111110000000001'),
    list('1000000001111111111111000000001'),
    list('1000000000011111111100000000001'),
    list('1000000000111111111110000000001'),
    list('1000000001111111111111000000001'),
    list('1000000011111111111111100000001'),
    list('1000000111111111111111110000001'),
    list('1000000001111111111111000000001'),
    list('1000000011111111111111100000001'),
    list('1000000111111111111111110000001'),
    list('1000001111111111111111111000001'),
    list('1000011111111111111111111100001'),
    list('1000000000000011100000000000001'),
    list('1000000000000011100000000000001'),
    list('1000000000000011100000000000001'),
    list('1000000000000000000000000000001'),
    list('1000000000000000000000000000001'),
    list('1000000000000000000000000000001'),
    list('1000000000000000000000000000001'),
    list('1111111111111111111111111111111'),
    ], dtype=np.uint32) # Need to use int because correlate() wont accept bool

################################################################################
# Debugging
def visualize_robots(positions: list[Vector2D], bathroom_shape: tuple[int, int]) -> str:
    arr = [['∙']*bathroom_shape[0] for _ in range(bathroom_shape[1])]
    for i,j in positions:
        arr[j][i] = '⍾'
    return '\n'.join(''.join(x) for x in arr)


################################################################################
if __name__ == "__main__":
    main()
