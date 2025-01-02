#!/usr/bin/env python
# Standard library
import logging
import time
from collections import defaultdict
from collections.abc import Iterable

# 1st party
import aoc_utils as aoc

# Globals
log = logging.getLogger('AoC')

################################################################################
# LAN Party
#
# Example input:
# kh-tc
# qp-kh
# de-cg
# ka-co
# yn-aq
# qp-ub
# cg-tb
# vc-aq
# ...
#
# Part 1: 7 of 12 cliques
# Part 2: co,de,ka,ta

def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    graph = defaultdict(set)
    for edge in text.splitlines():
        n1, n2 = edge.split('-')
        graph[n1].add(n2)
        graph[n2].add(n1)
    graph: Graph = dict(graph)

    # Part 1
    start     = time.perf_counter()
    cliques   = find_3cliques(graph)
    n_cliques = sum(any(node.startswith('t') for node in c) for c in cliques)
    elapsed   = time.perf_counter() - start
    print(f'Part 1: {n_cliques} [t={(elapsed)*1000:.3f}ms]')

    # Part 2
    start    = time.perf_counter()
    clique   = max(find_maximal_cliques(graph), key=len)
    password = ','.join(sorted(clique))
    elapsed  = time.perf_counter() - start
    print(f'Part 2: {password!r} [t={(elapsed)*1000:.3f}ms]')

################################################################################
Vertex = str
Graph = dict[Vertex, set[Vertex]]

def find_3cliques(graph: Graph) -> list[set[Vertex]]:
    cliques = set()
    seen = set()
    for node1, neighbors in graph.items():
        for node2 in neighbors - seen:
            for node3 in graph[node2] - seen:
                if node1 in graph[node3]:
                    cliques.add(frozenset({node1, node2, node3}))
        seen.add(node1)
    cliques = [set(x) for x in cliques]
    return cliques

def find_maximal_cliques(
    graph       : Graph, 
    subgraph    : set[str] | None = None, 
    candidates  : set[str] | None = None, 
    was_checked : set[str] | None = None,
) -> Iterable[set[Vertex]]:
    '''Bron-Kerbosch enumeration algorithm that finds maximal cliques in an
    undirected graph.

    see https://en.wikipedia.org/wiki/Bron%E2%80%93Kerbosch_algorithm
    '''

    if subgraph is None or candidates is None or was_checked is None:
        candidates  = set(graph.keys())
        subgraph    = set()
        was_checked = set()
    
    if len(candidates) == len(was_checked) == 0:
        yield subgraph.copy()

    while len(candidates) > 0:
        vertex    = candidates.pop()
        neighbors = graph[vertex]

        subgraph.add(vertex)
        yield from find_maximal_cliques(
            graph, 
            subgraph = subgraph,
            # Limit candidates to vertices that are neighbors of all vertices in
            # the clique
            candidates  = candidates & neighbors,
            was_checked = was_checked & neighbors
        )

        # Backtrack to previous subgraph and move vertex to `was_checked` so
        # later recursive calls can know that vertex was checked and all maximal
        # cliques containing it were found.
        subgraph.remove(vertex)
        was_checked.add(vertex)
        assert len(was_checked & candidates) == 0

    # if len(was_checked) > 0:
    #     log.debug(
    #         'Exiting early. All cliques with a subset of %s added to %s were '
    #         'already found.', ','.join(was_checked), ','.join(subgraph)
    #     )

################################################################################
if __name__ == "__main__":
    main()
