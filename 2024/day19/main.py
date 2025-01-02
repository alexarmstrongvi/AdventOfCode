#!/usr/bin/env python
# Standard library
import logging
import time
from functools import lru_cache
from collections import defaultdict
from dataclasses import dataclass, field

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# Linen Layout
#
# Example input:
# r, wr, b, g, bwu, rb, gb, br
#
# brwrr
# bggr
# gbbr
# rrbgbr
# ubwu
# bwurrg
# brgr
# bbrgwb
#
# Part 1: 6 possible designs
# Part 2: 16 arrangements of those designs


def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    text_in, text_out = text.split('\n\n')
    designs = text_out.split()

    # Option 1: 150ms
    # towel_patterns = text_in.split(', ')

    # Option 2: 3X speed up
    # towel_patterns = defaultdict(list)
    # for p in text_in.split(', '):
    #     towel_patterns[p[0]].append(p)

    # Option 3: 7X speed up
    towel_patterns = Trie()
    for p in text_in.split(', '):
        towel_patterns.add(p)

    @lru_cache(maxsize=2**16)
    def count_arrangements(design: str) -> int:
        if design == '':
            return 1
        return sum(
            count_arrangements(design[len(p):])
            # Option 1
            # for p in towel_patterns if design.startswith(p)
            # Option 2
            # for p in towel_patterns[design[0]] if design.startswith(p)
            # Option 3
            for p in towel_patterns.get_prefixes(design)
        )

    # Part 1 & 2
    start = time.perf_counter()
    n = list(map(count_arrangements, designs))
    n_possible_designs = sum(map(bool, n))
    n_arrangements = sum(n)
    elapsed = time.perf_counter() - start
    print(f'Part 1: {n_possible_designs} [t={elapsed*1000:.3f}ms]')
    print(f'Part 2: {n_arrangements} [SAME]')

################################################################################
@dataclass(slots=True)
class TrieNode:
    prefix : str | None = None
    children : dict[str, 'TrieNode'] = field(default_factory=lambda : defaultdict(TrieNode))

class Trie:
    """
    A specialized search tree data structure used to store and retrieve strings
    from a dictionary or set. Also known as a digital tree or prefix tree.

    see https://en.wikipedia.org/wiki/Trie
    """
    def __init__(self):
        self.root = TrieNode()

    def add(self, prefix: str) -> None:
        """Add prefix to trie"""
        node = self.root
        for char in prefix:
            node = node.children[char]
        node.prefix = prefix

    def get_prefixes(self, word: str) -> list[str]:
        node = self.root
        prefixes = []
        for char in word:
            if (node := node.children.get(char)) is None:
                break
            if node.prefix is not None:
                prefixes.append(node.prefix)

        return prefixes

if __name__ == "__main__":
    main()
