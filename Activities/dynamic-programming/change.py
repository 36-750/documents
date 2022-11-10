#!/usr/local/priority/bin/python

"""
Code for solving the making change dynamic programming problem.
Based on the puzzle: "Small Change for Mujikhistan" in
/Doctor Ecco's Cyberpuzzles/ by Dennis E. Shasha
"""

import sys
import argparse
from itertools import combinations, chain

MAX_CENTS = 100

def subsets(iter, r):
    return list(map(set, combinations(iter, r)))

def all_coin_sets(denominations, size, always_penny=True):
    """Iterator over all coin sets of specified size with allowed denominations.

       denominations -- sequence of allowed coin values
       size          -- number of coins in each returned coin set
       always_penny  -- should pennies be included in every coin set?

    Returns an iterator/map object over coin sets.
    """

    if always_penny:
        return [s.union([1]) for s in subsets(set(denominations) - set([1]), size - 1)]
    else:
        return subsets(set(denominations), size)

def make_change(denominations, num_coins, weights=[1] * MAX_CENTS,
                intuitive=False, always_penny=True):
    """Find a set of coins that minimizes expected purchase number.

         denominations -- a collection of coin denominations excluding pennies
         num_coins     -- how many coins to use for making change
         weights       -- unnormalized distribution over costs 1:MAX_CENTS-1
         intuitive     -- use intuitive counting?
         always_penny  -- include pennies in each coin set?

    Returns a tuple containing the best weighted average change size,
    the minimizing coin set, and the change made for each purchase cost.
    The latter is a list whose 0th index is None for easy indexing by cost.
    """

    best_coins = None
    best_change = None
    best_average = MAX_CENTS

    for coin_set in all_coin_sets(denominations, num_coins, always_penny):
        change = best_change_with(coin_set, intuitive)

        if not all(change):  # Could not make change for all values
            continue

        average = 0.0
        denomin = 0.0
        for total in range(1, MAX_CENTS):
            average += weights[total] * len(change[total])
            denomin += weights[total]

        average = average / denomin

        if average < best_average:
            best_average = average
            best_coins = coin_set
            best_change = change[:]

    best_change[0] = None

    return best_average, best_coins, best_change

def best_change_with(coin_set, intuitive=False):
    """
    Computes the most efficient change from a given coin set for each cost.

        coin_set   -- set of coin denominations to use
        intuitive  -- whether to use intuitive (greedy) counting

    Returns optimal change for each target price from 1 to MAX_CENTS-1.
    This is given as a list whose 0th element is None to enable
    indexing by cost.

    """
    best = [[] for _ in range(MAX_CENTS)]
    num_coins = len(coin_set)
    min_coin = min(coin_set)

    sentinel = list(range(MAX_CENTS))
    for i in range(min_coin):
        best[i] = sentinel

    best[min_coin] = [min_coin]

    for target in range(min_coin + 1, MAX_CENTS):
        if intuitive:
            change = []
            total = target
            for c in sorted(coin_set, reverse=True):
                if c <= total:
                    num_cs = total // c
                    change.extend([c] * num_cs)
                    total -= num_cs * c

            if total > 0:
                best_change = sentinel
            else:
                best_change = change
        else:
            best_change = sentinel

            for c in coin_set:
                if target > c and best[target - c] is not None:
                    # [:] creates a copy, so that change.append does not change
                    # the values stored in best
                    change = best[target - c][:]
                    change.append(c)

                    if len(change) < len(best_change):
                        best_change = change

                elif target == c:
                    best_change = [c]

        if best_change != sentinel:
            best[target] = sorted(best_change)
        else:
            best[target] = None

    return best

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--coins", dest="num_coins",
                        type=int, action="store", default=3,
                        help="Number of coins to consider [default: 3].")
    parser.add_argument("--allow-no-pennies", dest="require_pennies",
                        action="store_false", default=True,
                        help="Set if pennies need not be included in the coin"
                             " set [default: False]")

    parser.add_argument("-i", "--intuitive", action="store_true", default=False,
                        help="Require an intuitive solution")
    # ATTN: add option for weights to be read from a file, default uniform
    #       just use uniform for now
    # ATTN: allow-no-pennies doesn't do much unless you restrict the range
    #       to min_coin:MAX_CENTS

    args = parser.parse_args()
    denominations = tuple(range(1, MAX_CENTS))

    average, coins, change = make_change(denominations, args.num_coins,
                                         intuitive=args.intuitive,
                                         always_penny=args.require_pennies)

    print(('Denominations {} with uniform average {}'
          ''.format(sorted(coins), average)))
    print("Best change for each purchase cost:")
    for cost, best_change in enumerate(change):
        if cost > 0:
            print(('    {} {}'.format(cost, best_change)))
