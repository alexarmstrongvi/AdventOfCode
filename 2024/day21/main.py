#!/usr/bin/env python
# Standard library
import logging
import time
from collections.abc import Callable, Iterable
from functools import lru_cache, partial
from itertools import pairwise, permutations, starmap
from typing import Literal

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# Keypad Conundrum
#
# 029A
# 980A
# 179A
# 456A
# 379A
#
# Part 1: 126384
# Part 2: 154115708116294

def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    codes = text.splitlines()
    parse_num = lambda code : int(code[:-1])

    # Part 1
    start = time.perf_counter()
    total_complexity = sum(
        parse_num(code) * find_min_presses_keypad(code, n_dirpads=3)
        for code in codes
    )
    elapsed = time.perf_counter() - start
    print(f'Part 1: {total_complexity} [t={(elapsed)*1000:.3f}ms]')

    # Part 2
    start = time.perf_counter()
    total_complexity = sum(
        parse_num(code) * find_min_presses_keypad(code, n_dirpads=26)
        for code in codes
    )
    elapsed = time.perf_counter() - start
    print(f'Part 2: {total_complexity} [t={(elapsed)*1000:.3f}ms]')

################################################################################

def find_min_presses_keypad(code: str, n_dirpads: int) -> int:
    return _find_min_presses(code, n_dirpads, generate_possible_presses_numpad)

@lru_cache(maxsize=2**16) # BIG speedup from memoizing
def find_min_presses_dirpad(dirpad_seq: str, n_dirpads: int) -> int:
    return _find_min_presses(dirpad_seq, n_dirpads, generate_possible_presses_dirpad)

def _find_min_presses(
    dirpad_seq: str,
    n_dirpads: int,
    gen_possible_presses: Callable[[str, str],list[str]],
) -> int:
    '''Find the minimum number of button presses required by the last of
    `n_dirpads` robots and people typing into directional keypads to cause the
    robot on the first directional keypad to enter `dirpad_seq` where
    `gen_possible_presses` will generate all possible button presses that robot
    N can make to get robot N-1 to move between any two buttons (e.g. numeric or
    directional keypad)
    '''
    if n_dirpads == 0:
        return len(dirpad_seq)
    moves    = pairwise('A'+dirpad_seq)
    find_min = partial(find_min_presses_dirpad, n_dirpads = n_dirpads-1)
    return sum(
        min(map(find_min, possible_presses))
        for possible_presses in starmap(gen_possible_presses, moves)
    )

NumpadButton = Literal['A','0','1','2','3','4','5','6','7','8','9']
NUMPAD = {
    '7' : (0,0), '8' : (0,1), '9' : (0,2),
    '4' : (1,0), '5' : (1,1), '6' : (1,2),
    '1' : (2,0), '2' : (2,1), '3' : (2,2),
                 '0' : (3,1), 'A' : (3,2),
}
def generate_possible_presses_numpad(b0: NumpadButton, b1: NumpadButton) -> list[str]:
    paths = generate_all_button_paths(NUMPAD[b0], NUMPAD[b1])
    return [seq for (seq, positions) in paths if (3,0) not in positions]

DirpadButton = Literal['A','^','v','<','>']
DIRPAD = {
                 '^' : (0,1), 'A' : (0,2),
    '<' : (1,0), 'v' : (1,1), '>' : (1,2),
}
@lru_cache(maxsize=len(DIRPAD)**2)
def generate_possible_presses_dirpad(b0: DirpadButton, b1: DirpadButton) -> list[str]:
    paths = generate_all_button_paths(DIRPAD[b0], DIRPAD[b1])
    return [seq for (seq, positions) in paths if (0,0) not in positions]

Position = tuple[int,int]
def generate_all_button_paths(p0, p1) -> list[tuple[str, list[Position]]]:
    diff = p1[0]-p0[0], p1[1]-p0[1]
    ud = ('v' if diff[0] >= 0 else '^') * abs(diff[0])
    lr = ('>' if diff[1] >= 0 else '<') * abs(diff[1])
    return [
        (f'{"".join(seq)}A', get_positions(p0, seq))
        for seq in set(permutations(ud+lr))
    ]
def move_robot(c: DirpadButton, p: Position) -> Position:
    if   c == '^' : return (p[0]-1, p[1])
    elif c == '<' : return (p[0],   p[1]-1)
    elif c == 'v' : return (p[0]+1, p[1])
    elif c == '>' : return (p[0],   p[1]+1)
    raise ValueError(c)

def get_positions(start: Position, moves: Iterable[DirpadButton]) -> list[Position]:
    positions = [start]
    for c in moves:
        positions.append(move_robot(c, positions[-1]))
    return positions

################################################################################
if __name__ == "__main__":
    main()
