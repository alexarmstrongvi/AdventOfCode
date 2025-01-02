#!/usr/bin/env python
# Standard library
import logging
import time
from enum import Enum
from dataclasses import dataclass
import heapq
from functools import reduce
from itertools import chain

# 3rd party
import numpy as np
from tqdm import tqdm

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# RAM run
#
# Example input:
# 5,4
# 4,2
# 4,5
# 3,0
# 2,1
# 6,3
# 2,4
# 1,5
# 0,6
# 3,3
# 2,6
# 5,1
# 1,2
# 5,5
# 2,5
# 6,5
# 1,4
# 0,4
# 6,4
# 1,1
# 6,1
# 1,0
# 0,5
# 1,6
# 2,0
#
# Part 1: 22 steps
# Part 2: byte (6,1)


def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)
    
    # Solution
    byte_positions = list(map(parse, text.split()))
    ymax = max(p[0] for p in byte_positions)
    xmax = max(p[1] for p in byte_positions)
    target = (ymax, xmax)
    grid_shape = (ymax+1, xmax+1)
    if grid_shape == (7,7):
        n_fallen = 12
    elif grid_shape == (71,71) and len(byte_positions) == 3450:
        n_fallen = 1024
    else:
        n_fallen = None

    # Part 1
    start = time.perf_counter()
    best_paths, best_path_to, best_path_from = find_best_paths(byte_positions[:n_fallen], grid_shape)
    elapsed = time.perf_counter() - start
    assert len(best_paths) > 0
    n_steps = best_paths[0].n_steps
    print(f'Part 1: {n_steps} [t={elapsed*1000:.3f}ms]')

    # Part 2
    start = time.perf_counter()
    if n_fallen is None:
        n_fallen = -1
    it = range(n_fallen+1, len(byte_positions))
    if not log.isEnabledFor(logging.DEBUG):
        it = tqdm(it, desc='Finding paths', unit='byte', total=len(byte_positions), initial = n_fallen+1)
    for n_fallen in it:
        log.debug('Checking for path after %d bytes have fallen', n_fallen)
        best_paths, best_path_to, best_path_from = find_best_paths(
                byte_positions[:n_fallen], 
                grid_shape, 
                (best_paths, best_path_to, best_path_from),
            )
        if len(best_paths) == 0:
            y,x = byte_positions[n_fallen-1]
            break

    elapsed = time.perf_counter() - start
    print(f'Part 2: ({x},{y}) [t={elapsed*1000:.3f}ms]')


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

def parse(line: str) -> Position:
    x,y = line.split(',')
    return int(y), int(x)

@dataclass
class MemoryPath:
    pos   : Position
    dist_to_target: float
    path  : list[Position]

    @property
    def n_steps(self):
        return len(self.path)-1

    @property
    def rank(self) -> float:
        return self.n_steps + self.dist_to_target
    
    def __lt__(self, other: 'MemoryPath') -> bool:
        return self.rank < other.rank

def find_best_paths(
    byte_positions: list[Position], 
    grid_shape: tuple[int, int],
    warm_start = None,
):# -> dict[Position, MemoryPath]:
    m, n = grid_shape
    start = (0,0)
    target = (m-1,n-1)
    distance = lambda p,t : abs(t[0]-p[0]) + abs(t[1] - p[1])
    is_corrupted = lambda p : p in byte_positions
    out_of_bounds = lambda p : not ((0 <= p[0] < m) and (0 <= p[1] < n))

    # Avoid exploring paths that...
    # 1) already have a cost greater than the min cost once that cost is known
    min_steps : int | None = None
    # 2) reach a spot already visited via another path but with a higher cost
    # than that other path (include direction to account for cost of turning)
    best_path_to   : dict[Position, MemoryPath] = {}
    best_path_from : dict[Position, MemoryPath] = {}
    def is_non_optimal_path(path: MemoryPath) -> bool:
        if min_steps is not None and path.n_steps + path.dist_to_target > min_steps:
            return True
        if path.pos not in best_path_to:
            return False
        if best_path_to[path.pos].n_steps <= path.n_steps:
            return True
        # if min_steps is not None and best_path_to[path.pos].n_steps < path.n_steps:
        #     return True
        # if min_steps is None and best_path_to[path.pos].n_steps <= path.n_steps:
        #     return True
        return False

    paths_in_progress = [MemoryPath(start, distance(start, target), [start])]
    successful_paths = []

    # if warm_start is not None:
    #     log.debug('Preparing warm start')
    #     best_paths, paths_to, paths_from = warm_start
    #     del paths_to[target]
    #     byte_pos = set(byte_positions)
    #     for path in chain(best_paths, paths_to.values()):
    #         steps = path.path
    #         path_broken = False
    #         for i, p in enumerate(steps):
    #             if p in byte_pos:
    #                 path_broken = True
    #                 break
    #         if not path_broken:
    #             i = len(steps)
    #         steps_to   = steps[:i] 
    #         pos_to     = steps_to[-1]
    #         path_to    = MemoryPath(pos_to,  distance(pos_to,  target), steps_to)
    #         if path.pos == target or pos_to == target:
    #             paths_in_progress.append(path_to)
    #         if pos_to not in best_path_to:
    #             best_path_to[pos_to] = path_to
    #         if pos_to == target:
    #             min_steps = path_to.n_steps
    #             successful_paths.append(path_to)
    #     for path in paths_from.values():
    #         steps = path.path
    #         path_broken = False
    #         for i, p in enumerate(steps):
    #             if p in byte_pos:
    #                 path_broken = True
    #                 break
    #         if not path_broken:
    #             i = -1
    #         steps_from   = steps[i+1:]
    #         pos_from     = steps_from[0]
    #         path_from    = MemoryPath(pos_from, 0, steps_from)
    #         if pos_from not in best_path_from:
    #             best_path_from[pos_from] = path_from
    #     heapq.heapify(paths_in_progress)
    #     log.debug('Warm start grid')
    #     visualize_path(successful_paths, paths_in_progress, byte_pos,
    #                    grid_shape, best_path_to, best_path_from,
    #                    min_steps, None)
    #     if len(successful_paths) > 0:
    #         log.debug('Warm start has successful path')
    #         return successful_paths, best_path_to, best_path_from

    cnt = 0
    while len(paths_in_progress) > 0:
        cnt += 1
        path = heapq.heappop(paths_in_progress)
        log.debug('%d) Updating path at %s [steps = %d; rank= %d; n_paths = %d]', 
            cnt, path.pos, path.n_steps, path.rank, len(paths_in_progress) + len(successful_paths)
        )

        for move in [Direction.DOWN, Direction.RIGHT, Direction.LEFT, Direction.UP]:
            next_pos  = path.pos + move
            if is_corrupted(next_pos) or out_of_bounds(next_pos):
                continue
            # if cnt == 31:
            #     breakpoint()
            if next_pos in best_path_from:
                log.debug('Reached previous successful path: %s', move.name)
                path_new  = MemoryPath(
                    pos            = target,
                    dist_to_target = 0,
                    path           = path.path + best_path_from[next_pos].path
                )
            else:
                path_new  = MemoryPath(
                    pos            = next_pos,
                    dist_to_target = distance(next_pos, target),
                    path           = path.path + [next_pos]
                )
            if is_non_optimal_path(path_new):
                log.debug('Non-optimal path: %s', move.name)
                if path_new.pos not in best_path_to or best_path_to[path_new.pos].n_steps > path_new.n_steps:
                    best_path_to[path_new.pos] = path_new
                continue
            if path_new.pos not in best_path_to or best_path_to[path_new.pos].n_steps > path_new.n_steps:
                best_path_to[path_new.pos] = path_new
            # if cnt > 10000:
            #     breakpoint()
            if path_new.pos == target:
                log.debug('REACHED TARGET!: %s', move.name)
                if min_steps is None: 
                    min_steps = path_new.n_steps
                min_steps = min(min_steps, path_new.n_steps)
                successful_paths.append(path_new)
                for i, pos in enumerate(path_new.path):
                    if pos in best_path_from and len(path_new.path)-1 - i >= len(best_path_from[pos].path):
                        continue
                    best_path_from[pos] = MemoryPath(pos, 0, path_new.path[i:])
                visualize_path(successful_paths, paths_in_progress, byte_positions,
                               grid_shape, best_path_to, best_path_from,
                               min_steps, path_new)
                continue
            log.debug('Adding path: %s', move.name)
            heapq.heappush(paths_in_progress, path_new)

        
        successful_paths = [p for p in successful_paths if p.n_steps == min_steps]

        # DEBUG
        if cnt % 10000 == 0 or warm_start is not None:
            visualize_path(successful_paths, paths_in_progress, byte_positions,
                           grid_shape, best_path_to, best_path_from, min_steps, path)
    log.debug('n paths = %d', len(successful_paths))

    return successful_paths, best_path_to, best_path_from

################################################################################
# DEBUG
def visualize_path(
    successful_paths,
    paths_in_progress,
    byte_positions,
    grid_shape,
    best_path_to,
    best_path_from,
    min_steps,
    path = None,
):
    if not log.isEnabledFor(logging.DEBUG):
        return
    path_positions = reduce(set.union, (set(p.path) for p in successful_paths + paths_in_progress), set())
    dbg_grid = np.full(grid_shape, ' ')
    for p in byte_positions:
        dbg_grid[p] = '#'
    for p in best_path_to.keys():
        dbg_grid[p] = '.'
    for p in best_path_from.keys():
        dbg_grid[p] = '*'
    for p in path_positions:
        dbg_grid[p] = '+'
    for p in successful_paths + paths_in_progress:
        if min_steps is None:
            s = 'x'
        else:
            s = hex((p.n_steps + p.dist_to_target) - min_steps)[-1]
        dbg_grid[p.pos] = s
    if len(paths_in_progress) > 0 and path is not None:
        for p in path.path:
            dbg_grid[p] = 'v'
        dbg_grid[path.pos] = '@'
    log.info('\n'.join(''.join(row) for row in dbg_grid))
    # time.sleep(0.1)

################################################################################
if __name__ == "__main__":
    main()
