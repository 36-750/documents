from __future__ import annotations

from abc             import abstractmethod
from collections.abc import Callable

from .Functor   import Functor
from .functions import identity

__all__ = ['Bifunctor', 'bimap', 'bilift', 'map_first', 'map_second',]


#
# Functor as a mixin
#

class Bifunctor(Functor):
    @abstractmethod
    def bimap[A, B, C, D](self, f: Callable[[A], B], g: Callable[[C], D]):
        ...

    def map_first[A, B](self, f: Callable[[A], B]) -> Bifunctor:
        return self.bimap(f, identity)

    def map_second[C, D](self, g: Callable[[C], D]) -> Bifunctor:
        return self.bimap(identity, g)

    def map[C, D](self, g: Callable[[C], D]):
        return self.map_second(g)


def bimap[A, B, C, D](f: Callable[[A], B], g: Callable[[C], D], bf: Bifunctor) -> Bifunctor:
    "Maps functions over both components of a bifunctor, returning a transformed bifunctor."
    return bf.bimap(f, g)

def bilift[A, B, C, D](f: Callable[[A], B], g: Callable[[C], D]):
    """Lifts functions on components to a mapping on bifunctors.

    This is just the partial application bimap(f, g, __).

    """
    def lift_fg(bf: Bifunctor):
        return bf.bimap(f, g)

    return lift_fg

def map_first[A, B](f: Callable[[A], B], bf: Bifunctor) -> Bifunctor:
    "Maps a function over the first component of a bifunctor."
    return bf.bimap(f, identity)

def map_second[C, D](g: Callable[[C], D], bf: Bifunctor) -> Bifunctor:
    "Maps a function over the second component of a bifunctor."
    return bf.bimap(identity, g)
