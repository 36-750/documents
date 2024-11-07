#
# Naperian Tuples
#
# We view an NTuple a as a function from [1..n] -> a,
# so all components are the same type. This gives us
# natural Functor and Applicative instances.

from __future__   import annotations

from typing       import Callable, Optional, cast

from .Applicative import Applicative, map2
from .Functor     import Functor, pymap
from .List        import List, snoc_
from .Traversable import Traversable

__all__ = ['NTuple',]


class NTuple[A](tuple, Applicative, Traversable):
    """Tuples with components of a common type as Applicative Traversables.

    Here, NTuple a is isomorphic to [1..n] -> a for some n.
    In this sense, map is just function composition, and
    map2 is composition with the tensor product i :-> g(a1(i), a2(i)).

    These are, however, implemented as wrapped Python tuples.

    """
    def __new__(cls, *args, **kwds):
        return super().__new__(cls, *args, **kwds)

    def __repr__(self):
        return super().__repr__()

    def __getitem__(self, key):
        items = super().__getitem__(key)
        if isinstance(key, slice):
            return NTuple(items)
        return items

    @classmethod
    def of(cls, *xs: tuple[Iterable[A], ...]):
        return cls(xs)
    
    def map[B](self, g: Callable[[A], B]):
        return NTuple(pymap(g, self))

    @classmethod
    def pure(cls, a):
        return cls([a])

    def map2[B, C](self, g: Callable[[A, B], C], fb: NTuple[B]) -> NTuple[C]:
        if len(self) != len(fb):
            raise TypeError(f'map2 requires NTuples of the same length: {len(self)} != {len(fb)}')

        concat = []
        for i, a in enumerate(self):
            concat.append(g(a, fb[i]))
        return NTuple(concat)

    def traverse(self, f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        folded = f.pure(List())
        for item in self:
            folded = map2(snoc_, g(item), folded)
        return folded.map(NTuple)
