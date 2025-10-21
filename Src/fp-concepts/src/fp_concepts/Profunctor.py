#
# Abstract base class and generic methods for Profunctors
#
# trait Profunctor p where
#     dimap : (c -> a) -> (b -> d) -> p a b -> p c d
#     lmap  : (c -> a)             -> p a b -> p c b
#     rmap  :             (b -> d) -> p a b -> p a d
#
#     lmap f = dimap f id
#     rmap g = dimap id g
#
# Laws:
#
#     dimap id id == id
#     lmap id == id
#     rmap id == id
#
#     dimap (f . g) (k . h) == dimap g k . dimap f h
#     lmap (f . g) == lmap g . lmap f
#     rmap (k . h) == rmap k . rmap h
#

from __future__ import annotations

from abc             import abstractmethod
from collections.abc import Callable
from typing          import Protocol

from .functions      import identity


class Profunctor[A, B](Protocol):
    @abstractmethod
    def dimap[C, D](self, f: Callable[[C], A], g: Callable[[B], D]) -> Profunctor[C, D]:
        ...

    def lmap[C](self, f: Callable[[C], A]) -> Profunctor[C, B]:
        return self.dimap(f, identity)

    def rmap[D](self, g: Callable[[B], D]) -> Profunctor[A, D]:
        return self.dimap(identity, g)


def dimap[A, B, C, D](f: Callable[[C], A], g: Callable[[B], D], p: Profunctor[A, B]) -> Profunctor[C, D]:
    "Maps over profunctors: Profunctor p => (c -> a) -> (b -> d) -> p a b -> p c d."
    return p.dimap(f, g)

def lmap[A, B, C](f: Callable[[C], A],p: Profunctor[A, B]) -> Profunctor[C, B]:
    "Maps over profunctor input: Profunctor p => (c -> a) -> p a b -> p c b."
    return p.lmap(f)

def rmap[A, B, D](g: Callable[[B], D], p: Profunctor[A, B]) -> Profunctor[A, D]:
    "Maps over profunctor output: Profunctor p => (b -> d) -> p a b -> p a d."
    return p.rmap(g)

def dilift[A, B, C, D](f: Callable[[C], A], g: Callable[[B], D]) -> Callable[[Profunctor[A, B]], Profunctor[C, D]]:
    "Partial version of dimap: Lifts a pair of appropriate functions to a mapping of profunctors."
    def lifted(p: Profunctor[A, B]) -> Profunctor[C, D]:
        return p.dimap(f, g)

    return lifted
