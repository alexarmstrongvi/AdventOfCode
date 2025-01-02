#!/usr/bin/env python
# Standard library
import logging
import time
from collections import Counter
from itertools import accumulate

# 3rd party
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from numpy.typing import NDArray
from tqdm import tqdm

# 1st party
import aoc_utils as aoc

# Globals
ArrInt32 = NDArray[np.int32]
log = logging.getLogger('AoC')

################################################################################
# Monkey Market
#
# Example input:
# 1
# 10
# 100
# 2024
#
# Part 1: 37327623
# Part 2:

def main() -> None:
    # Boilerplate
    args = aoc.parse_args()
    aoc.configure_logging(args.log_level)
    text = aoc.read_input(args.input)

    # Solution
    initial_secret_nums = [int(x) for x in text.splitlines()]

    # Part 1
    start = time.perf_counter()
    secret_nums = np.stack([
        simulate_secret_numbers(n, 2000) for n in tqdm(initial_secret_nums)
    ])
    total = secret_nums[:,-1].sum()
    elapsed = time.perf_counter() - start
    print(f'Part 1: {total} [t={(elapsed)*1000:.3f}ms]')

    # Part 2
    start = time.perf_counter()
    n_bananas = buy_max_bananas(secret_nums)
    elapsed = time.perf_counter() - start
    print(f'Part 1: {n_bananas} [t={(elapsed)*1000:.3f}ms]')


################################################################################
def simulate_secret_numbers(secret_num: int, n_steps: int) -> ArrInt32:
    nums = np.zeros(n_steps+1, dtype=np.int32)
    nums[0] = secret_num
    for i in range(n_steps):
        nums[i+1] = predict_next_secret_num(nums[i])
    return nums

def predict_next_secret_num(n: int) -> int:
    # Option 1)
    # mix   = lambda n, x : n ^ x
    # prune = lambda n    : n % 16777216
    # n = prune(mix(n, n *64))
    # n = prune(mix(n, n //32))
    # n = prune(mix(n, n *2048))

    # Option 2) binary operations: 2X speedup
    n = ((n << 6)  ^ n) & (2**24-1)
    n = ((n >> 5)  ^ n) & (2**24-1)
    n = ((n << 11) ^ n) & (2**24-1)

    return n

def buy_max_bananas(secret_nums: ArrInt32) -> int:
    prices = secret_nums % 10
    changes = np.diff(prices, axis=1)
    window_size = 4

    windows = sliding_window_view(changes, window_shape=window_size, axis=1)
    rows = tqdm(windows, desc='Counting sequences', unit='row')
    sequences = sum(
        (Counter(set(map(tuple, row.tolist()))) for row in rows),
        start = Counter()
    )
    log.info(
        '%d subsequences found in multiple buyers',
        sum(x>1 for x in sequences.values())
    )

    max_per_buyer = prices[:, window_size:].max(axis=0)
    max_possible = list(accumulate(reversed(sorted(max_per_buyer.tolist()))))

    max_n_bananas = 0
    log.debug(Counter(sequences.values()))
    # VERY SLOW: ~1hr to run
    for seq, cnt in tqdm(sequences.most_common(), unit='seq'):
        # Early exits
        if max_possible[cnt] <= max_n_bananas:
            break
        if cnt == 1:
            max_n_bananas = max(max_n_bananas, max_per_buyer.max())
            break

        i_buyer, i_time = np.nonzero((windows == seq).all(axis=2))
        _, first_occurance = np.unique(i_buyer, return_index=True)
        i_buyer = i_buyer[first_occurance]
        i_time  = i_time[first_occurance]
        n_bananas = prices[i_buyer, i_time+len(seq)].sum()
        max_n_bananas = max(max_n_bananas, n_bananas)
    return max_n_bananas

################################################################################
if __name__ == "__main__":
    main()
