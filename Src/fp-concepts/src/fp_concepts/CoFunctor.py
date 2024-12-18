#
# Contravariant functors, the dual of Functor, or equivalently a functor on the op category.
#
# trait CoFunctor (f : Type -> Type) where
#     comap : (b -> a) -> f a -> f b
#

from __future__ import annotations

from abc             import abstractmethod
from collections.abc import Callable
from typing          import Protocol

from .functions      import Function

__all__ = ['CoFunctor', 'comap', 'colift', 'Predicate']

#
# CoFunctor as a mixin
#

class CoFunctor(Protocol):
    @abstractmethod
    def comap[A, B](self, g: Callable[[B], A]):
        ...

def comap[A, B](f: Callable[[B], A], cf: CoFunctor):
    """Maps a function over a contravariant functor, returning a transformed cofunctor.

    """
    return cf.comap(f)

def colift[A, B](f: Callable[[B], A]):
    """Lifts a function to a mapping on cofunctors.

    This is just the partial application comap(f, __).

    """
    def colift_f(cf: CoFunctor):
        return cf.comap(f)

    return colift_f


#
# Examples
#

class Predicate[A](Function, CoFunctor):
    def __init__(self, predicate: Callable[[A], bool]):
        super().__init__(predicate)

    def __call__(self, x: A, *args, **kwds) -> bool:
        return super().__call__(x, *args, **kwds)

    def comap[B](self, g: Callable[[B], A]):
        return self @ g


#  even = Predicate(lambda x: x % 2 == 0)
#  odd = comap(inc, even)
#
#  even(10)
#  #=> True
#  even(9)
#  #=> False
#  odd(10)
#  #=> False
#  even(9)
#  #=> True
