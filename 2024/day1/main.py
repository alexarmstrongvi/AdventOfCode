#!/usr/bin/env python
import sys
from collections import Counter
from pathlib import Path
import time

path = Path(sys.argv[1])
assert path.is_file(), path

start = time.perf_counter()
left, right = list(zip(*map(lambda s:map(int,s.split()), path.read_text().splitlines())))

total_diff = sum(map(lambda x : abs(x[0]-x[1]), zip(sorted(left), sorted(right))))
elapsed = time.perf_counter() - start
print('Part 1:', total_diff, f'[{elapsed*1000:.3f}ms]')

start = time.perf_counter()
score = sum(x * Counter(right)[x] for x in left)
elapsed = time.perf_counter() - start
print('Part 2:', score, f'[{elapsed*1000:.3f}ms]')
