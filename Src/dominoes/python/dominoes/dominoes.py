#!/usr/local/bin/python3

"""
dominoes - a FP/DOP approach to optimizing domino chains

Key ideas:
- Generic recursion
- Immutable views of the search tree
- Generic data structures
- Immutable data
- Data model and shape described (type annotations)
- Effective laziness baked into the algorithm

A fun version of this problem can be found at
 https://adventofcode.com/2017/day/24.

We assume that one end is exposed of a starting domino,
typically 0, and the goal is to build the best chain
according to various criteria (e.g., total number of dots
in the chain).

"""

import fileinput
import re

from argparse        import ArgumentParser
from collections     import namedtuple
from collections.abc import Mapping
from functools       import reduce
from pyrsistent      import PMap, PVector, m, pmap, pvector, v
from typing          import Annotated, Callable, Final, Literal, NamedTuple, NewType, Union

import dominoes.zipper as Zip


#
# Constants
#
ALL_EVALUATED: Final[int] = -1     # Special index value indicating a node is processed
INITIAL_ID: Final[int] = 0         # Starting id for special initial tile
VERSION: Final[str] = "1.0.1"      # Current version of this program


#
# Types and Type Constructors
#
Domino = tuple[int, int]     # Description of the original domino

class Pool(NamedTuple):
    ids: dict[int, Domino]
    available: PMap
    nextid: int

DominoId = NewType('DominoId', int)

class PlayedDomino(NamedTuple):
    """A domino in play with one end exposed; id distinguishes repeats."""
    id: int   # id of pair in domino table
    end: int  # the exposed end of this domino


#
# Pool Management
#
# We keep a pool of available dominoes, allowing for repeats.
# The pool is indexed by the end values and gives a list of dominoes
# matching each end. A domino is added twice in this way, unless
# its two sides are equal. We this map a pool-map below.
#
# Fields:
# + ids: we give unique ids assigned to each domino, a map from id to domino
#       this is set once and never changed; it is shared among all uses
#
# + available: immutable map containing all currently available dominoes,
#       indexed by domino ends and giving a list of matches to that end.
#
# + nextid: a serial integer giving an unused id for the next addition
#
# A Pool is an immutable object

def assoc_domino_internal(avail: PMap, id: int, domino: Domino) -> PMap:
    """Updates a pool-map to add a domino (possibly both ends). Returns the map."""
    def update_avail(_id, _end):
        dom = PlayedDomino(id=_id, end=_end)
        return lambda u: u.append(dom) if u else v(dom)
        
    a, b = domino
    avail = avail.transform([a], update_avail(id, b))
    if a != b:
        avail = avail.transform([b], update_avail(id, a))
    return avail

def make_pool(initial_dominoes: list[Domino], start: int) -> Pool:
    """Creates a new pool from an initial list of dominoes.

    Parameters:
      + initial_dominoes: the total population of dominoes at our disposal
      + start: the exposed end of the special starting domino

    Returns an immutable pool based on the initial dominoes.
    """
    id = INITIAL_ID
    ids = {INITIAL_ID: (0, start)}
    available = pmap({start: v((id, 0))})
    if start != 0:
        available = available.set(0, v((id, start)))
    for i, d in enumerate(initial_dominoes):
        id += 1
        ids[id] = d
        available = assoc_domino_internal(available, id, d)
    return Pool(ids=ids, available=available, nextid=id + 1)

def assoc_domino(pool: Pool, domino: PlayedDomino, orig_domino: Union[Domino, None] = None) -> Pool:
    """Updates pool with a new domino added."""
    id = domino.id
    dpair = pool.ids[id] if orig_domino is None else orig_domino
    available = assoc_domino_internal(pools.available, id, dpair)
    return Pool(ids=pool.ids, available=available, nextid=pool.nextid)

def dissoc_domino(pool: Pool, domino: PlayedDomino) -> Pool:
    """Updates pool with a new domino removed."""
    id = domino.id
    dpair = pool.ids[id]
    available = pool.available.transform([dpair[0]], lambda u: u.remove((id, dpair[1])))
    if dpair[0] != dpair[1]:
        available = available.transform([dpair[1]], lambda u: u.remove((id, dpair[0])))
    return Pool(ids=pool.ids, available=available, nextid=pool.nextid)


#
# Nodes
#
# We have two types of nodes: SearchNodes, which are used when building the
# tree and searching solutions, and SubtreeValue, which are used to
# deconstruct the tree and aggregate scores.

class SearchNode(NamedTuple):
    domino: PlayedDomino
    pool: Pool
    children: Union[PVector, None]               # None marks a fresh, unfilled node
    uneval: Annotated[int, {min: ALL_EVALUATED}]

class SubtreeValue(NamedTuple):
    score: int
    chain: list[tuple[int, int]]    

Node = NewType('Node', Union[SearchNode, SubtreeValue])

def is_subtree_value(node: Node) -> bool:
    return isinstance(node, SubtreeValue)


#
# Zipper configuration
#
# A zipper is an immutable representation of a tree that allows
# pure navigation and modification. The zipper's behavior is
# configured by functions that distinguish branch nodes, get
# a branch node's children, and create a new node 

def is_branch(node: Node) -> bool:
    """Any SearchNode wi """
    return isinstance(node, SearchNode) and node.children is not None

def children(node: Node) -> list[Node]:
    if node.children is None:
        return []
    else:
        return list(node.children)

def make_node(node: Node, children: list[Node]) -> Node:
    if isinstance(node, SearchNode):
        is_unevald = lambda ichild: not is_subtree_value(ichild[1])
        uneval, _ = next(filter(is_unevald, enumerate(children)), (ALL_EVALUATED, None))
        return SearchNode(domino=node.domino, pool=node.pool, children=pvector(children), uneval=uneval)
    else:
        raise Exception('make_node on SubtreeValue does not really make sense')


#
# Co-Algebra: seed -> pool -> SearchNode
#
# The CoAlgebra is the function used at every level to build the next level
# of the search tree (lazily) from a seed and pool.

CoAlgebra = Callable[[PlayedDomino, Pool], SearchNode]

def build(seed: PlayedDomino, pool: Pool) -> SearchNode:
    """Creates a filled SearchNode from a seed domino and available pool"""
    # needs to set uneval = 0 if there are any matches
    # else set it to ALL_EVALUATED
    my_pool = dissoc_domino(pool, seed)
    children = [SearchNode(domino=d, pool=my_pool, children=None, uneval=0)
                for d in my_pool.available[seed.end]]
    # Note: we could apply heuristics here like sorting with the biggest end first
    uneval = 0 if len(children) > 0 else ALL_EVALUATED
    return SearchNode(domino=seed, pool=my_pool, children=pvector(children), uneval=uneval)


#
# Algebra: SearchNode -> SubtreeValue
#
# The Algebra is the transformation that is used at each level to collapse and score a subtree.
# 

Algebra = Callable[[SearchNode], SubtreeValue]

def best_chain(node: SearchNode) -> SubtreeValue:
    """Computes the best subtree chain for the current node.

    When this call is reached, all the node's children will already
    have been processed, passing the best score and partial chain.

    Returns a SubtreeValue node to use in place of the current node.
    """
    # node will have all children processed already
    # passes up chain with best score
    domino = node.pool.ids[node.domino.id]
    my_score = domino[0] + domino[1]
    if len(node.children) == 0:
        return SubtreeValue(score=my_score, chain=[domino])

    best_child = reduce(lambda b, n: n if n.score > b.score else b, node.children)
    return SubtreeValue(score=best_child.score + my_score, chain=[domino, *best_child.chain])

def longest_chain(node: SearchNode) -> SubtreeValue:  # An alternative to show modularity
    """Computes the longest subtree chain for the current node.

    When this call is reached, all the node's children will already
    have been processed, passing the best score and partial chain.

    Returns a SubtreeValue node to use in place of the current node.
    """
    domino = node.pool.ids[node.domino.id]
    if len(node.children) == 0:
        return SubtreeValue(score=1, chain=[domino])

    best_child = reduce(lambda b, n: n if n.score > b.score else b, node.children)
    return SubtreeValue(score=best_child.score + 1, chain=[domino, *best_child.chain])



#
# Main Search
#
# Iteration Step
#
# 1. Initialize tree with starting # requirement (e.g., 0) (initial tile is one square domino, connected only on one side)
# 2. When step called at a node:
#    - if node is unevaluated, add this domino
#    - If no unevaluated children, replace this node  with result of applying the Algebra and move up
#    - Else, move down to the first unevaluated chid and add the domino
# 3. Coalgebra
#    - seed is a tuple (id, end, pool)  [can be three args in python]
#    - Create a new node with added domino removed from the pool and an UnevaluatedNode child for each matching domino in the pool
# 4. Adding a domino at the current node
#    - Call Coalgebra on domino to be added with current node's pool
#    - Replace this node with resulting node
#    - Call step at this node

def initialize(dominoes: list[Domino], start: int = 0, coalg: CoAlgebra = build) -> SearchNode:
    """Builds the initial node in the tree using the input dominoes.

    Parameters:
    + dominoes: input list of available dominoes (repeats ok), excluding special start tile
    + [start=0]: optional alternative number for exposed end of start tile
    + coalg: function that takes a seed: PlayedDomino and a Pool and constructs a node

    Returns an initial search node that serves as the tree root.
    """
    pool = make_pool(dominoes, start)
    init = (0, start) # The starting tile always has id 0
    return coalg(PlayedDomino(id=INITIAL_ID, end=start), pool)

def step(loc: Zip.Zipper, alg: Algebra, coalg: CoAlgebra = build) -> Zip.Zipper:
    """Performs one transformation step on the search tree zipper, returning updated tree.

    The step does not always move the tree, for instance when populating an unfilled node.
    The main steps are:

    1. If he node is unfilled, fill it with matching children in unfilled nodes
    2. If the node has been fully processed, reduce it with the algebra to a SubtreeValue,
       and move up.
    3. If the node has unprocessed children remaining, process the next one.
    4. If, for some reason, at a SubtreeValue, simply move up in the tree.

    Parameters:
    + loc: the current search tree zipper
    + alg: a function of a node that reduces the subtree at that node to a value
    + [coalg]: function that takes a seed: PlayedDomino and a Pool and constructs a node

    Returns an updated zipper
    """
    node = Zip.node(loc)
    match Zip.node(loc):
        case SearchNode(children=None):
            # Node is unfilled
            domino = node.domino
            filled = coalg(domino, node.pool)
            return Zip.replace(loc, filled)
        case SearchNode(uneval=u) if u == ALL_EVALUATED:
            # Node is complete, transform with the algebra
            return Zip.up(Zip.edit(loc, alg))
        case SearchNode():
            # Unevaluated children remain, move to next one
            return Zip.down(loc, node.uneval)
        case SubtreeValue():
            # At a chain node, shouldn't happen but no harm
            return Zip.up(loc)

def search(dominoes: list[Domino], alg: Algebra, start: int = 0) -> SubtreeValue:
    """Runs a full search for an optimal chain, returning the aggregate SubtreeValue.

    The search is completed when all the children of the root node have been processed.
    
    + dominoes: input list of available dominoes (repeats ok), excluding special start tile
    + alg: a function of a node that reduces the subtree at that node to a value
    + [start=0]: optional alternative number for exposed end of start tile

    Returns a SubtreeValue giving the best score and chain for the entire tree.
    """
    init = initialize(dominoes, start)
    tree = Zip.zipper(is_branch, children, make_node, init)

    while not (Zip.is_at_root(tree) and Zip.node(tree).uneval == ALL_EVALUATED):
        tree = step(tree, alg)
    return alg(Zip.node(tree))


#
# Command-Line Options
#    

def get_args():
    """Reads command line arguments and returns object containing stored values.

    Keys:
      start - Number on the singleton start tile (default: 0)
      objective - String indicating which algebra to use (default: 'strongest')
      files - List of filenames given as positional arguments, or None
    """
    parser = ArgumentParser(prog='dominoes')
    parser.add_argument("-s", "--start", type=int, default=0, metavar="TILE",
                        help="Number of dots on the singleton start tile.")
    parser.add_argument("-o", "--objective", type=str, default='strongest', metavar="OBJECTIVE",
                        help="Objective used to produce results from each subtree. Currently supported: strongest, longest")
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument('files', type=str, nargs='*', metavar="DOMINO_SPECS",
                        help="Optional input files from which to read domino list; stdin used if none. Dominoes are specified one per line by a pair of numbers separated by a space.")

    return parser.parse_args()

#
# Input/Output Processing
#

def read_dominoes(files):
    """Reads domino specification from given files or from standard input, if none.

    Dominoes are specified one per line as two space-separated numbers.
    """
    dominoes = []
    with fileinput.input(files=files) as f:
        for line in f:
            if m := re.match(r'\s*(\d+)\s+(\d+)', line):
                dominoes.append((int(m.group(1)), int(m.group(2))))
    return dominoes

def display_chain(chain):
    """Prints chain in order including the singleton start tile.""" 
    print([chain[0][1], *chain[1:]])


#
# Script
#

if __name__ == '__main__':
    args = get_args()
    print(args)
    dominoes = read_dominoes(args.files)
    alg = longest_chain if args.objective == 'longest' else best_chain
    res = search(dominoes, alg, args.start)
    
    print(f'Search for {args.objective} chain with dominoes:')
    print(dominoes)
    print(f'Optimal score {res.score} with chain:')
    display_chain(res.chain)
