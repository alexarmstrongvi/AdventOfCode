#!/usr/bin/env python
import sys
from pathlib import Path
from collections import Counter

path = Path(sys.argv[1])
assert path.is_file(), path

left, right = list(zip(*map(lambda s:map(int,s.split()), path.read_text().splitlines())))

total_diff = sum(map(lambda x : abs(x[0]-x[1]), zip(sorted(left), sorted(right))))
print('Part 1:', total_diff)
score = sum(x * Counter(right)[x] for x in left)
print('Part 2:', score)
