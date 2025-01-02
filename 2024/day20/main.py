#!/usr/bin/env python
# Standard library
import heapq
import logging
import time
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

# 3rd party
import numpy as np
from tqdm import tqdm

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# Race Condition
#
# Example input:
# ###############
# #...#...#.....#
# #.#.#.#.#.###.#
# #S#...#.#.#...#
# #######.#.#.###
# #######.#.#...#
# #######.#.###.#
# ###..E#...#...#
# ###.#######.###
# #...###...#...#
# #.#####.#.###.#
# #.#...#.#.#...#
# #.#.#.#.#.#.###
# #...#...#...###
# ###############
#
# Part 1: 44 cheats
# Part 2: 285 cheats saving 50 picoseconds

def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    lines = text.splitlines()
    racetrack  = np.array(lines).view('U1').reshape(len(lines),-1)

    time_savings_threshold_pt1 = time_savings_threshold_pt2 = 100
    if racetrack.shape == (15,15): # example
        time_savings_threshold_pt1 = 1
        time_savings_threshold_pt2 = 50

    start = time.perf_counter()
    race_path = find_best_path(racetrack)
    assert race_path is not None
    path = {p : i for i, p in enumerate(race_path)}
    elapsed_shared = time.perf_counter() - start

    # Part 1
    start = time.perf_counter()
    n_cheats = sum(
        time_saved >= time_savings_threshold_pt1
        for time_saved in find_cheats(path, max_picosec=2).values()
    )
    elapsed = time.perf_counter() - start
    print(f'Part 1: {n_cheats} [t={(elapsed_shared+elapsed)*1000:.3f}ms]')

    # Part 2
    start = time.perf_counter()
    n_cheats = sum(
        time_saved >= time_savings_threshold_pt2
        for time_saved in find_cheats(path, max_picosec=20).values()
    )
    elapsed = time.perf_counter() - start
    print(f'Part 2: {n_cheats} [t={(elapsed_shared+elapsed)*1000:.3f}ms]')

################################################################################
Position = tuple[int, int]

def find_cheats(
    path       : dict[Position, int],
    max_picosec: int
) -> dict[tuple[Position, Position], int]:
    cheats : dict[tuple[Position, Position], int]= {}
    for pos_start, i in tqdm(path.items()):
        for pos_final, j in get_reachable_positions(pos_start, path, max_picosec):
            if j <= i: # Ignore cheats that go backwards
                continue
            steps_saved = (j-i) - distance(pos_start, pos_final)
            cheats[(pos_start, pos_final)] = steps_saved
    return cheats

def get_reachable_positions(
    pos    : Position,
    path   : dict[Position, int],
    n_steps: int,
) -> Iterable[tuple[Position, int]]:
    for i_diff in range(-n_steps, n_steps+1):
        j_range = n_steps - abs(i_diff)
        for j_diff in range(-j_range, j_range+1):
            pos_final = (pos[0]+i_diff, pos[1]+j_diff)
            if (idx := path.get(pos_final)) is not None:
                yield pos_final, idx

def distance(p1: Position, p2: Position) -> int:
    '''2D manhattan distance'''
    return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])

class Direction(Enum):
    UP    = (-1, 0)
    DOWN  = ( 1, 0)
    LEFT  = ( 0,-1)
    RIGHT = ( 0, 1)

    def __radd__(self, loc: Position) -> Position:
        return (loc[0]+self.value[0], loc[1]+self.value[1])

    def turn_ccw(self) -> 'Direction':
        return Direction((-self.value[1], self.value[0]))

    def turn_cw(self) -> 'Direction':
        return Direction((self.value[1], -self.value[0]))

@dataclass(slots=True)
class RacePath:
    pos   : Position
    dir   : Direction
    path  : list[Position]

    def __lt__(self, other) -> bool:
        return len(self.path) < len(other.path)

def find_best_path(maze: np.ndarray) -> list[Position] | None:
    start     = get_coords(maze == 'S')[0]
    target    = get_coords(maze == 'E')[0]
    is_wall   = lambda p : maze[p] == '#'

    # Find starting direction
    start_dir = None
    for d in Direction:
        if not is_wall(start + d):
            start_dir = d
            break
    assert start_dir is not None

    paths_in_progress = [RacePath(start, start_dir, [start])]
    while len(paths_in_progress) > 0:
        path = heapq.heappop(paths_in_progress)
        for move in (path.dir, path.dir.turn_cw(), path.dir.turn_ccw()):
            next_pos  = path.pos + move
            if is_wall(next_pos):
                continue
            if next_pos == target:
                return path.path + [next_pos]
            path_new  = RacePath(
                pos  = next_pos,
                dir  = move,
                path = path.path + [next_pos],
            )
            heapq.heappush(paths_in_progress, path_new)
    return None

def get_coords(mask: np.ndarray) -> list[Position]:
    return [(int(x), int(y)) for x,y in zip(*np.where(mask))]

################################################################################
if __name__ == "__main__":
    main()
