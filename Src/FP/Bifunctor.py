from __future__ import annotations

from abc        import ABC
from functools  import partial, wraps
from typing     import Callable

from .Functor   import Functor
from .functions import identity

__all__ = ['Bifunctor', 'bimap', 'bilift', 'map_first', 'map_second',]


#
# Functor as a mixin
#

# ATTN: Make this a Functor with map == map_second
# Add map_first and map_second as default methods
#
class Bifunctor(Functor):
    def bimap[A, B, C, D](self, f: Callable[[A], B], g: Callable[[C], D]):
        ...

def bimap[A, B, C, D](f: Callable[[A], B], g: Callable[[C], D], F: Bifunctor) -> Bifunctor:
    "Maps functions over both components of a bifunctor, returning a transformed bifunctor."
    return F.bimap(f, g)

def bilift[A, B, C, D](f: Callable[[A], B], g: Callable[[C], D]):
    """Lifts functions on components to a mapping on bifunctors.

    This is just the partial application bimap(f, g, __).

    """
    def lift_fg(F: Bifunctor):
        return F.bimap(f, g)
 
    return lift_fg

def map_first[A, B](f: Callable[[A], B], F: Bifunctor) -> Bifunctor:
    "Maps a function over the first component of a bifunctor."
    return F.bimap(f, identity)

def map_second[C, D](g: Callable[[C], D], F: Bifunctor) -> Bifunctor:
    "Maps a function over the second component of a bifunctor."
    return F.bimap(identity, g)
