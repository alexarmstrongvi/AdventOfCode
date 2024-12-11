#!/usr/bin/env python
# Standard library
import logging
import time
from itertools import batched, groupby
from more_itertools import partition
from operator import itemgetter
from typing import Literal

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# Example input:
# 2333133121414131402
#
# Part 1: 1928
# Part 2: 2858

def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    disk_map = list(aoc.read_input(args.input).rstrip())

    # Solution
    # Part 1
    start       = time.perf_counter()
    block_map   = to_block_map(disk_map)
    compact_map = compactify_blocks(block_map)
    checksum    = compute_checksum(compact_map)
    elapsed     = time.perf_counter() - start
    print(f'Part 1: {checksum} [t={elapsed*1000:.3f}ms]')

    # Part 2
    start       = time.perf_counter()
    compact_map = compactify_files(block_map)
    checksum    = compute_checksum(compact_map)
    elapsed     = time.perf_counter() - start
    print(f'Part 2: {checksum} [t={elapsed*1000:.3f}ms]')

Block = int | Literal['.']
def to_block_map(disk_map: list[str]) -> list[Block]:
    block_map = []
    if len(disk_map) % 2 == 1:
        # even length list needed for batched()
        disk_map.append('0')
    for id_num, (n_files, n_free_space) in enumerate(batched(disk_map, 2)):
        block_map += [id_num]*int(n_files) + ['.']*int(n_free_space)
    return block_map

def compactify_blocks(block_map: list[Block]) -> list[Block]:
    cmap = block_map.copy()
    free_idxs = [i for i,x in enumerate(block_map) if x == '.']
    file_idxs = [i for i,x in enumerate(block_map) if x != '.']
    for free_idx, file_idx in zip(free_idxs, reversed(file_idxs)):
        if file_idx < free_idx:
            break
        cmap[free_idx], cmap[file_idx] = cmap[file_idx], cmap[free_idx]
    return cmap

def compactify_files(block_map: list[Block]) -> list[Block]:
    cmap = block_map.copy()
    group_idxs = groupby_idx(cmap)
    free_slices = [idxs for x,idxs in group_idxs if x == '.']
    file_slices = [idxs for x,idxs in group_idxs if x != '.']
    log.debug('CMap %s', to_str(cmap))
    for file_slice in reversed(file_slices):
        was_swapped = False
        for i, free_slice in enumerate(free_slices):
            if file_slice.start < free_slice.start:
                break
            if not file_fits(file_slice, free_slice):
                continue
            was_swapped = True
            file_size = file_slice.stop - file_slice.start

            free_slice_fill = slice(free_slice.start, free_slice.start + file_size)
            free_slice_rem = slice(free_slice.start + file_size, free_slice.stop)
            cmap[free_slice_fill], cmap[file_slice] = cmap[file_slice], cmap[free_slice_fill]
            break
        if was_swapped:
            free_slices[i] = free_slice_rem
    return cmap

def to_str(x):
    return ''.join(map(str,x))

def file_fits(file_slice: slice, free_slice: slice) -> bool:
    return (file_slice.stop - file_slice.start) <= (free_slice.stop - free_slice.start)

def groupby_idx(block_map: list[Block]) -> list[tuple[Block, slice]]:
    group_idxs = []
    for block, idxs in groupby(enumerate(block_map), itemgetter(1)):
        idxs = [idx for idx, _ in idxs]
        group_idxs.append((block, slice(idxs[0],idxs[-1]+1)))
    return group_idxs

def compute_checksum(block_map: list[Block]) -> int:
    return sum(i * int(x) for i,x in enumerate(block_map) if x != '.')

################################################################################
if __name__ == "__main__":
    main()
