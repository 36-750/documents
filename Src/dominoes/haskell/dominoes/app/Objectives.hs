-- Objectives for building and optimizing the search tree

module Objectives where

import Data.List

import qualified Data.Map as M

import DominoPool
import SearchTree


  -- Co-Algebra builds a tree from a starting tile and a pool
build :: CoAlgebra SearchTreeBase (Dots, Pool)
build (end, pool) =
  case M.lookup end pool of
    Nothing -> SearchNode end []
    Just found -> SearchNode end [(exposed, dissocDomino (end, exposed) pool) | exposed <- M.keys found]



  -- Algebra Helpers
type Chain = [Domino]
type Score = Int

findBest :: [(Score, Dots, Chain)] -> (Score, Dots, Chain)
findBest children =
  foldl1' better children
  where better acc@(sa, _, _) item@(si, _, _) = if si > sa then item else acc


  -- Three different Algebras
  -- 1. Gather all leaf chains,
  -- 2. Find strongest chain, and
  -- 3. Find longest chain.

  -- Find all valid, complete chains; leaves of the search tree
allChains :: Algebra SearchTreeBase (Dots, [Chain])
allChains (SearchNode end []) = (end, [])
allChains (SearchNode end children) =
  (end, concat [prepends end n chains | (n, chains) <- children])
  where prepends j k [] = [[(j,k)]]
        prepends j k cs = [(j, k) : c | c <- cs]

  -- Find the chain with the largest sum in the tree
  -- At each stage, exposed end is counted before complete
strongestChain :: Algebra SearchTreeBase (Score, Dots, Chain)
strongestChain (SearchNode end []) = (end, end, [])
strongestChain (SearchNode end children) =
  (score + 2*end, end, (end, dots):chain)
  where (score, dots, chain) = findBest children

  -- Find the chain in the tree that is the longest
longestChain :: Algebra SearchTreeBase (Score, Dots, Chain)
longestChain (SearchNode end []) = (0, end, [])
longestChain (SearchNode end children) =
  (score + 1, end, (end, dots):chain)
  where (score, dots, chain) = findBest children
