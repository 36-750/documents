# ruff: noqa: N802, N806

from __future__ import annotations

from collections.abc import Callable

from .Const       import makeConst, runConst
from .Monoids     import Monoid
from .Traversable import Traversable, traverse
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
