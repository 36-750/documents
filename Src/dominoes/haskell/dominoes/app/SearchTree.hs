-- SearchTree.hs - A Rose tree recording the search process

module SearchTree
  (SearchTreeBase(..),
   Algebra,
   CoAlgebra,
   hylo) where

import Control.Arrow ((>>>))

type End = Int
type Algebra f a = f a -> a
type CoAlgebra f a = a -> f a

data SearchTreeBase a = SearchNode End [a]
  deriving Functor

  -- A hylomorphism that builds and reduces the tree lazily
  -- hylo from Greek hyle, "matter"
hylo :: Functor f => Algebra f a -> CoAlgebra f b -> b -> a
hylo alg coalg = coalg >>> fmap (hylo alg coalg) >>> alg
