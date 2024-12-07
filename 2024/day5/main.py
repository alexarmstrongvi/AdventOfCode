#!/usr/bin/env python
# Standard library
import logging
import time
from collections import defaultdict
from collections.abc import Iterable
from functools import partial, reduce
from graphlib import CycleError, TopologicalSorter
from itertools import combinations, filterfalse, pairwise, takewhile
from operator import itemgetter
from typing import Callable

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    lines = iter(text.splitlines())
    rules = set(takewhile(lambda x : x != '', lines))
    nums = [s.split(',') for s in lines]
    log.debug('Rules: %s', sorted(rules))

    # Part 1
    start = time.perf_counter()
    in_right_order = partial(pages_in_right_order, rules)
    get_mid_item = lambda seq : int(seq[len(seq)//2])
    total_pt1 = sum(map(get_mid_item,filter(in_right_order, nums)))
    elapsed = time.perf_counter() - start
    print(f'Part 1: {total_pt1} [t={elapsed*1000:.3f}ms]')

    # Part 2
    start = time.perf_counter()
    sort = partial(sort_pages_naive, rules)
    total_pt2 = sum(map(get_mid_item,map(sort,filterfalse(in_right_order, nums))))
    elapsed = time.perf_counter() - start
    print(f'Part 2: {total_pt2} [t={elapsed*1000:.3f}ms]')

    ############################################################################ 
    # Alternate solutions
    ############################################################################ 
    # Part 1 & 2 together so updates are partitioned once
    start = time.perf_counter()
    ordered, unordered = partition(nums, in_right_order)
    assert total_pt1 == sum(map(get_mid_item, ordered))
    assert total_pt2 == sum(map(get_mid_item, map(sort,unordered)))
    elapsed = time.perf_counter() - start
    print(f'Elapsed (method 2): {elapsed*1000}ms')

    # More robust sorting using topological sort
    is_sorted = lambda it : all(x <= y for x,y in pairwise(it))
    argsort   = lambda it : [i for i,_ in sorted(enumerate(it), key=itemgetter(1))]
    start = time.perf_counter()
    try:
        rule_nums = tuple(TopologicalSorter(rules_to_graph(rules)).static_order())
        # assert in_right_order(rule_nums)
        rule_map  = dict(zip(rule_nums, range(len(rule_nums))))
        # TODO: Handle numbers for which there are no sorting rules that would
        # cause rule_map.get to return None
        argsort_pages   = lambda it : argsort(map(rule_map.get, it))
        in_right_order2 = lambda it : is_sorted(argsort_pages(it))
        sort2           = lambda seq : itemgetter(*argsort_pages(seq))(seq)

        ordered, unordered = partition(nums, in_right_order2)
        assert total_pt1 == sum(map(get_mid_item, ordered))
        assert total_pt2 == sum(map(get_mid_item, map(sort2,unordered)))
        elapsed = time.perf_counter() - start
        print(f'Elapsed (method 3): {elapsed*1000}ms')
    except CycleError as e:
        cycle = [f'{x}|{y}' for x,y in pairwise(e.args[1])]
        assert len(set(cycle) - rules) == 0
        log.error('Rules create cycle: %s', cycle)

################################################################################
def pages_in_right_order(rules, page_nums) -> bool:
    return all(
        f'{y}|{x}' not in rules 
        # Combinations preserves order
        for x,y in combinations(page_nums,2)
    )

def sort_pages_naive(rules, page_nums):
    nums = page_nums.copy()
    n_loop = 0
    while (idxs := find_unordered_idxs(rules, nums)) is not None:
        # This sorting approach can very easily get caught in an infinite loop
        # if a lot of numbers are out of order but it works for the input data
        # in this case
        n_loop += 1
        if n_loop > 1_000_000:
            log.error('Infinite loop')
            break

        i,j = idxs 
        nums[i], nums[j] = nums[j], nums[i]
    return nums


def find_unordered_idxs(rules, page_nums) -> tuple[int,int] | None:
    for i,j in combinations(range(len(page_nums)),2):
        x, y = page_nums[i], page_nums[j]
        t = f'{y}|{x}'
        if t in rules:
            # log.debug('Rule broken %s: %s', t, page_nums)
            return i,j
    return None

def partition[T](
    it: Iterable[T], 
    pred: Callable[[T],bool]
) -> tuple[list[T],list[T]]:
    # Option 1: Procedural
    # a = []
    # b = []
    # for x in it:
    #     if pred(x):
    #         a.append(x)
    #     else:
    #         b.append(x)

    # Option 2: Functional
    a,b = reduce(
        lambda acc, x : (acc[0]+[x], acc[1]) if pred(x) else (acc[0], acc[1]+[x]),
        it,
        ([],[]),
    )

    return a,b

def rules_to_graph(rules):
    graph = defaultdict(set)
    for rule in rules:
        before, after = rule.split('|')
        graph[after].add(before)
    return graph
if __name__ == "__main__":
    main()
