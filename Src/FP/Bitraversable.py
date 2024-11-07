#
# Bifunctors that can be traversed in order on both variables
#  
# trait Bitraversable (f : Type -> Type -> Type) where
#     traverse : (a -> f c) -> (b -> f d) -> t a b -> f (t c d)
#

from __future__ import annotations

from abc             import ABC
from collections.abc import Iterable
from functools       import partial, wraps
from typing          import Callable

from .Applicative    import Applicative, IdentityA
from .Bifunctor      import Bifunctor, bimap
from .functions      import Function, identity

__all__ = ['Bitraversable', 'bitraverse', 'bisequence']


class Bitraversable(Bifunctor):
    def bitraverse(self, f: type[Applicative], g1: Callable, g2: Callable) -> Applicative:   # Hard to type properly in Python
        ...

def bitraverse( g1: Callable, g2: Callable, bt: Bitraversable, effect: Optional[type[Applicative]] = IdentityA) -> Applicative:
    """Evaluates effectful functions at each element of a structure, giving the same shape in an effectful context.

    Type: (Bitraversable t, Applicative f) => (a -> f c) -> (b -> f d) -> t a b -> f (t c d)

    """
    return bt.traverse(get_effect(g1) or get_effect(g2) or effect, g1, g2)


def bisequence(bt: Bitraversable, effect: Optional[type[Applicative]] = IdentityA) -> Applicative:
    """Evaluate effects on each element of a structure, collecting the results in the effectful context.

    Type: (Bitraversable t, Applicative f) =>  t a b -> f (t a b)

    """
    return bitraverse(identity, identity, t, effect)
