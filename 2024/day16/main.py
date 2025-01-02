#!/usr/bin/env python
# Standard library
import heapq
import logging
import time
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from functools import reduce

# 3rd party
import numpy as np

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# Raindeer Maze
#
# Example input:
# ###############
# #.......#....E#
# #.#.###.#.###.#
# #.....#.#...#.#
# #.###.#####.#.#
# #.#.#.......#.#
# #.#.#####.###.#
# #...........#.#
# ###.#.#####.#.#
# #...#.....#.#.#
# #.#.#.###.#.#.#
# #.....#...#.#.#
# #.###.#.#.#.#.#
# #S..#.....#...#
# ###############
#
# Part 1: 7036 cost
# Part 2: 45 places to sit

def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    lines = text.splitlines()
    maze  = np.array(lines).view('U1').reshape(len(lines),-1)

    # Part 1 & 2
    start = time.perf_counter()
    tile_positions, cost = find_best_paths(maze)
    n_places_to_sit = len(tile_positions)
    elapsed = time.perf_counter() - start
    print(f'Part 1: {cost} [t={elapsed*1000:.3f}ms]')
    print(f'Part 2: {n_places_to_sit} [SAME]')

################################################################################
Position = tuple[int, int]

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
class ReindeerPath:
    pos   : Position
    dir   : Direction
    tiles : set[Position]
    cost  : int

    def __lt__(self, other) -> bool:
        return self.cost < other.cost

def find_best_paths(maze: np.ndarray) -> tuple[set[Position], int | None]:
    start     = get_coords(maze == 'S')[0]
    direction = Direction.RIGHT
    target    = get_coords(maze == 'E')[0]
    is_wall   = lambda p : maze[p] == '#'

    # Avoid exploring paths that...
    # 1) already have a cost greater than the min cost once that cost is known
    min_cost : int | None = None
    # 2) reach a spot already visited via another path but with a higher cost
    # than that other path (include direction to account for cost of turning)
    visited : dict[tuple[Position, Direction], int] = {}
    def is_non_optimal_path(path: ReindeerPath) -> bool:
        if min_cost is not None and path.cost > min_cost:
            return True
        state = (path.pos, path.dir)
        if state in visited and visited[state] < path.cost:
            return True
        return False

    successul_paths = []
    paths_in_progress = [ReindeerPath(start, direction, {start,}, 0)]
    while len(paths_in_progress) > 0:
        path = heapq.heappop(paths_in_progress)
        visited[(path.pos, path.dir)] = path.cost
        log.debug('Updating path at %s [cost = %d]', path.pos, path.cost)

        next_moves = (
            (1,    path.dir),
            (1001, path.dir.turn_ccw()),
            (1001, path.dir.turn_cw()),
        )
        for move_cost, move in next_moves:
            next_pos  = path.pos + move
            if is_wall(next_pos):
                continue
            path_new  = ReindeerPath(
                pos   = next_pos,
                dir   = move,
                tiles = path.tiles | {next_pos,},
                cost  = path.cost + move_cost
            )
            if is_non_optimal_path(path_new):
                continue
            if path_new.pos == target:
                assert min_cost is None or min_cost == path_new.cost
                min_cost = path_new.cost
                successul_paths.append(path_new)
            heapq.heappush(paths_in_progress, path_new)

    all_path_tiles = reduce(set.union, (p.tiles for p in successul_paths))
    return all_path_tiles, min_cost

def get_coords(mask: np.ndarray) -> list[Position]:
    return [(int(x), int(y)) for x,y in zip(*np.where(mask))]

################################################################################
if __name__ == "__main__":
    main()
