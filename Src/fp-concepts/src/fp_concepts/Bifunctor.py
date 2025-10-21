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
    def bimap[A, B, C, D](self, f: Callable[[A], C], g: Callable[[B], D]):
        ...

    def map_first[A, C](self, f: Callable[[A], C]) -> Bifunctor:
        return self.bimap(f, identity)

    def map_second[B, D](self, g: Callable[[B], D]) -> Bifunctor:
        return self.bimap(identity, g)

    def map[B, D](self, g: Callable[[B], D]):
        return self.map_second(g)


def bimap[A, B, C, D](f: Callable[[A], C], g: Callable[[B], D], bf: Bifunctor) -> Bifunctor:
    "Maps functions over both components of a bifunctor, returning a transformed bifunctor."
    return bf.bimap(f, g)

def bilift[A, B, C, D](f: Callable[[A], C], g: Callable[[B], D]):
    """Lifts functions on components to a mapping on bifunctors.

    This is just the partial application bimap(f, g, __).

    """
    def lift_fg(bf: Bifunctor):
        return bf.bimap(f, g)

    return lift_fg

def map_first[A, C](f: Callable[[A], C], bf: Bifunctor) -> Bifunctor:
    "Maps a function over the first component of a bifunctor."
    return bf.bimap(f, identity)

def map_second[B, D](g: Callable[[B], D], bf: Bifunctor) -> Bifunctor:
    "Maps a function over the second component of a bifunctor."
    return bf.bimap(identity, g)
