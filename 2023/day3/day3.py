import itertools
from pathlib import Path
import sys
import re
from typing import Any
from collections import defaultdict
from collections.abc import Iterable
import math

def main():
    ifile = Path(sys.argv[1]).open('r')
    lines = (line.rstrip('\n') for line in ifile)

    part_numbers = []
    possible_gears = defaultdict(list)
    for i, ((prev, next), curr) in enumerate(lag_and_lead(lines)):
        curr_part_nums = []
        for match in re.finditer(r'\d+', curr):
            border = border_2d(curr, match.span(), prev, next)
            num = int(match.group())
            symbol_found = False
            for i_shift, j, c in border:
                if not is_symbol(c):
                    continue
                symbol_found = True
                if c == '*':
                    possible_gears[(i+i_shift, j)].append(num)
            if symbol_found:
                curr_part_nums.append(num)
        print(f'INFO | R{i} part #s: {curr_part_nums}')
        part_numbers.extend(curr_part_nums)

    gear_ratios = []
    for (i,j), nums in possible_gears.items():
        if len(nums) != 2:
            continue
        gear_ratio = math.prod(nums)
        print(f'INFO | Gear [R{i},C{j}] : {nums} -> {gear_ratio}')
        gear_ratios.append(gear_ratio)

    print('INFO | Part 1 solution:', sum(part_numbers))
    print('INFO | Part 2 solution:', sum(gear_ratios))

def is_symbol(c):
    return c != '.' and not c.isdigit()

def border_2d(line, span, above, below):
    at_top    = above is None
    at_left   = span[0] == 0
    at_right  = span[1] == len(line)
    at_bottom = below is None

    start = span[0]-1 if not at_left  else 0
    end   = span[1]   if not at_right else len(line)-1

    if not at_top:
        for j in range(start,end+1):
            yield -1, j, above[j]

    if not at_left:
        yield 0, start, line[start]
    if not at_right:
        yield 0, end, line[end]

    if not at_bottom:
        for j in range(start, end+1):
            yield 1, j, below[j]

def nwise(iterable, *, n) -> Iterable[tuple[Any,...]]:
    return zip(*(
        itertools.islice(it, i, None) 
        for i, it in enumerate(itertools.tee(iterable, n))
    ))

def lag_and_lead(iterable) -> Iterable[tuple[Any,...]]:
    return (
        ((lag,lead), x) for lag, x, lead in nwise(
            itertools.chain([None], iterable, [None]),
            n = 3,
        )
    )

if __name__ == '__main__':
    main()
