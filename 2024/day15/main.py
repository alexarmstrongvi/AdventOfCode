#!/usr/bin/env python
# Standard library
import logging
import time
from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum

# 3rd party
import numpy as np
from tqdm import tqdm

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')
logging.getLogger('asyncio').setLevel(logging.WARNING)

################################################################################
# Restroom Reboot
#
# Example input:
# ##########
# #..O..O.O#
# #......O.#
# #.OO..O.O#
# #..O@..O.#
# #O#..O...#
# #O..O..O.#
# #.OO.O.OO#
# #....O...#
# ##########
#
# <vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
# vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
# ><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
# <<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
# ^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
# ^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
# >^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
# <><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
# ^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
# v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
#
# Part 1: 10092
# Part 2: 9021

def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    warehouse_text, movements_text = text.split('\n\n')

    movements = list(map(Direction.from_char, movements_text.replace('\n','')))
    to_gps_coord = lambda p : 100 * p[0] + p[1]

    # Part 1
    fish, boxes, walls, warehouse_shape = parse_warehouse(warehouse_text)

    start        = time.perf_counter()
    boxes_final  = simulate_lanternfish(fish, boxes, walls, movements, warehouse_shape)
    total        = sum(map(to_gps_coord, boxes_final))
    elapsed      = time.perf_counter() - start
    print(f'Part 1: {total} [t={elapsed*1000:.3f}ms]')

    # Part 2
    warehouse_wide_text = (warehouse_text
        .replace('.','..')
        .replace('#','##')
        .replace('O','[]')
        .replace('@','@.')
    )
    fish, boxes, walls, warehouse_shape = parse_warehouse(warehouse_wide_text)

    start       = time.perf_counter()
    boxes_final = simulate_lanternfish(fish, boxes, walls, movements, warehouse_shape)
    total       = sum(map(to_gps_coord, boxes_final))
    elapsed     = time.perf_counter() - start
    assert total != 1496283
    print(f'Part 2: {total} [t={elapsed*1000:.3f}ms]')

################################################################################
def parse_warehouse(warehouse_text: str):
    lines = warehouse_text.split('\n')
    warehouse = np.array(lines).view('U1').reshape(len(lines),-1)

    fish  = np.stack(np.where(warehouse == '@')).transpose().squeeze()
    walls = np.stack(np.where(warehouse == '#')).transpose()
    boxes = np.stack(np.where(warehouse == 'O')).transpose()
    if len(boxes) > 0:
        boxes = set(to_positions(boxes))
    else:
        boxes = np.stack([
            np.stack(np.where(warehouse == '[')).transpose(),
            np.stack(np.where(warehouse == ']')).transpose(),
        ], axis=1)
        boxes = BoxHandler.from_boxes(boxes.tolist())
    if len(boxes) == 0:
        raise RuntimeError

    fish  = to_position(fish)
    walls = set(to_positions(walls))
    return fish, boxes, walls, warehouse.shape


Position = tuple[int, int]
class Direction(Enum):
    UP    = (-1, 0)
    DOWN  = ( 1, 0)
    LEFT  = ( 0,-1)
    RIGHT = ( 0, 1)

    def __getitem__(self, idx: int) -> int:
        return self.value[idx]

    def __radd__(self, loc: Position) -> Position:
        if not isinstance(loc, tuple) and len(loc) == 2:
            raise TypeError(type(loc))
        return (loc[0]+self.value[0], loc[1]+self.value[1])

    @classmethod
    def from_char(cls, c : str):
        return {
            '^' : Direction.UP,
            'v' : Direction.DOWN,
            '<' : Direction.LEFT,
            '>' : Direction.RIGHT,
        }[c]

def simulate_lanternfish(
    fish      : Position,
    boxes     : 'set[Position] | BoxHandler',
    walls     : set[Position],
    movements : list[Direction],
    warehouse_shape : tuple[int, int] | None = None,
) -> set[Position]:
    if isinstance(boxes, set): # 1 cell boxes
        boxes = simulate_lanternfish_1cell(fish, boxes, walls, movements, warehouse_shape)
    elif isinstance(boxes, BoxHandler): # 2+ cell boxes
        box_handler = simulate_lanternfish_2cell(fish, boxes, walls, movements, warehouse_shape)
        boxes = box_handler.get_ref_positions()
    return boxes


def simulate_lanternfish_1cell(
    fish      : Position,
    boxes     : set[Position],
    walls     : set[Position],
    movements : list[Direction],
    warehouse_shape : tuple[int, int] | None = None,
) -> set[Position]:
    boxes  = boxes.copy()
    move_iter = movements
    if not log.isEnabledFor(logging.DEBUG):
        move_iter = tqdm(movements, desc='Simulating lanternfish', unit='moves')

    for move in move_iter:
        log.debug('Moving: %s', move.name)
        next_pos = fish + move
        if next_pos in walls:
            continue
        if next_pos in boxes:
            # Find end of boxes
            pos = next_pos
            while (pos := pos + move) in boxes:
                pass
            if pos in walls:
                continue
            # Moving all boxes is the same as moving first box to end
            boxes.remove(next_pos)
            boxes.add(pos)
        fish = next_pos

        if warehouse_shape is not None:
            log.debug(
                "After %s:\n%s",
                move.name,
                visualize_warehouse(fish, boxes, walls, warehouse_shape)
            )
    return boxes

def simulate_lanternfish_2cell(
    fish      : Position,
    boxes     : 'BoxHandler',
    walls     : set[Position],
    movements : list[Direction],
    warehouse_shape : tuple[int, int] | None = None,
) -> 'BoxHandler':
    boxes  = deepcopy(boxes)
    move_iter = movements
    if not log.isEnabledFor(logging.DEBUG):
        move_iter = tqdm(movements, desc='Simulating lanternfish', unit='moves')

    for move in move_iter:
        if warehouse_shape is not None:
            box_ref_pos = boxes.get_ref_positions()
            log.debug(
                "Next move %s:\n%s",
                move.name,
                visualize_warehouse(fish, box_ref_pos, walls, warehouse_shape, using_wide_boxes=True)
            )
        next_pos = fish + move
        if next_pos in walls:
            continue
        if next_pos in boxes:
            try:
                boxes.move(next_pos, move, walls)
            except BoxesCantBeMoved:
                continue
        fish = next_pos
    if warehouse_shape is not None:
        box_ref_pos = boxes.get_ref_positions()
        log.debug(
            "Final:\n%s",
            visualize_warehouse(fish, box_ref_pos, walls, warehouse_shape, using_wide_boxes=True)
        )
    return boxes

@dataclass
class BoxHandler:
    boxes   : list[set[Position]]
    box_idx : dict[Position, int]

    @classmethod
    def from_boxes(cls, boxes: Iterable[Iterable[Position]]):
        box_idx = {}
        _boxes = []
        for idx, box in enumerate(boxes):
            _box = set(map(tuple,box))
            _boxes.append(_box)
            for pos in _box:
                box_idx[pos] = idx
        return cls(_boxes, box_idx)

    def __len__(self) -> int:
        return len(self.boxes)

    def __contains__(self, pos: Position) -> bool:
        return pos in self.box_idx

    def move(self, box: Position, move: Direction, walls: set[Position]) -> None:
        # Get box positions
        curr_box_idx = self.box_idx[box]
        curr_box = self.boxes[curr_box_idx]
        # Breadth-first search of all positions to check they can be moved
        other_box_in_way = lambda p : p in self.box_idx and self.box_idx[p] != curr_box_idx
        moved_box = set()
        for pos in curr_box:
            moved_pos = pos + move
            log.debug('Checking if %s is free for box %s move', pos, move.name)
            if moved_pos in walls:
                log.debug('Wall preventing move')
                raise BoxesCantBeMoved
            if other_box_in_way(moved_pos):
                log.debug('Other box in way')
                self.move(moved_pos, move, walls)
            log.debug('Able to move %s', moved_pos)
            moved_box.add(moved_pos)

        log.debug('Moving box %s at %s', move.name, box)
        self._update_without_check(curr_box_idx, moved_box)

    def _update_without_check(self, box_idx: int, new_box: set[Position]) -> None:
        old_box = self.boxes[box_idx]
        # self.boxes and self.box_idx must be kept in sync
        self.boxes[box_idx] = new_box
        for pos in old_box - new_box:
            del self.box_idx[pos]
        for pos in new_box - old_box:
            self.box_idx[pos] = box_idx

    def get_ref_positions(self) -> set[Position]:
        return {next(iter(sorted(box))) for box in self.boxes}

class BoxesCantBeMoved(Exception):
    pass

def to_position(arr: np.ndarray) -> Position:
    return int(arr[0]), int(arr[1])

def to_positions(arr: np.ndarray) -> list[Position]:
    if arr.ndim == 2:
        return list(map(lambda p : (int(p[0]), int(p[1])), arr))
    raise NotImplementedError(arr.ndim)

################################################################################
# Debugging
def visualize_warehouse(fish, boxes, walls, warehouse_shape, using_wide_boxes = False) -> str:
    warehouse = np.full(warehouse_shape, '.', dtype='U1')
    warehouse[fish] = '@'
    idxs = tuple(map(list,zip(*boxes)))
    if using_wide_boxes:
        warehouse[idxs] = '['
        idxs = (idxs[0], [x+1 for x in idxs[1]])
        warehouse[idxs] = ']'
    else:
        warehouse[idxs] = 'O'
    idxs = tuple(map(list,zip(*walls)))
    warehouse[idxs] = '#'
    return '\n'.join(''.join(row) for row in warehouse)

################################################################################
if __name__ == "__main__":
    main()
