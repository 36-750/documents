module SearchTreeExt where

import SearchTree

-- Other Recursion Schemes  

newtype FixedPoint f = FixedPoint { unroll :: f (FixedPoint f) }

type SearchTree = FixedPoint SearchTreeBase

  -- An anamorphism that builds a search tree from a seed
  -- ana from Greek, "building"
ana :: Functor f => CoAlgebra f a -> a -> FixedPoint f
ana coalg = coalg >>> fmap (ana coalg) >>> FixedPoint

  -- A catamorphism that reduces a search tree
  -- cata from Greek, "collapse", "destruction", "downward", "inward"
cata :: Functor f => Algebra f a -> FixedPoint f -> a
cata alg = unroll >>> fmap (cata alg) >>> alg
  
