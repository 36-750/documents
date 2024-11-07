from __future__ import annotations

from typing       import Callable

from .Functor     import Functor
from .Applicative import Applicative
from .Traversable import Traversable, traverse
from .Monoids     import Monoid
from .Const       import Const, makeConst, runConst
from .functions   import compose as c
from .utils       import Collect

__all__ = ['foldMap']


#
# foldMap : (Monoid m, Traversable t) => (a -> m) -> t a -> m
#
# We need to specify the Monoid (defaults to Collect) because Python
# cannot infer it automatically.
#
# In TL1, this has a simple expression
#
#   foldMap f = runConst . traverse (Const . f)
#

def foldMap(f: Callable, t: Traversable, m: Monoid = Collect):
    C = makeConst(m)(0).__class__  # Give access to pure and monoid, which is all we need in traverse
    return runConst(traverse(c(makeConst(m), f), t, C))
