#!/usr/bin/env python
import sys
from pathlib import Path

path = Path(sys.argv[1])
assert path.is_file(), path

answer = sum(
    map(
        lambda x : abs(x[0]-x[1]), 
        zip(
            *map(
                sorted, 
                zip(
                    *[map(int, l.split()) for l in path.read_text().splitlines()]
                )
            )
        )
    )
)
print(answer)
