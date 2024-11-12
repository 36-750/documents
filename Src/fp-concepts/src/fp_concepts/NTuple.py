#
# Naperian Tuples
#
# We view an NTuple a as a function from [1..n] -> a,
# so all components are the same type. This gives us
# natural Functor and Applicative instances.
#
# ruff: noqa: EM102


from __future__ import annotations

from collections.abc import Callable, Iterable

from .Applicative import Applicative, map2
from .Functor     import pymap
from .List        import List, append_
from .Traversable import Traversable

__all__ = ['NTuple',]


class NTupleBase[A](tuple, Applicative, Traversable):
    """Tuples with components of a common type as Applicative Traversables.

    Here, NTuple a is isomorphic to [1..n] -> a for some n.
    In this sense, map is just function composition, and
    map2 is composition with the tensor product i :-> g(a1(i), a2(i)).

    These are, however, implemented as wrapped Python tuples.

    """
    _size = 1

    def __new__(cls, *args, **kwds):
        if len(args) == 0:
            mesg = f'Ntuple({cls._size}) requires {cls._size} elements.'
            raise TypeError(mesg)
        input = list(args[0])  # Allow iterators/generators/iterables as input
        if len(input) != cls._size:
            mesg = f'Ntuple({cls._size}) initialized with {len(input)} != {cls._size} elements.'
            raise TypeError(mesg)
        return super().__new__(cls, input, *args[1:], **kwds)

    def __getitem__(self, key):
        items = super().__getitem__(key)
        if isinstance(key, slice):
            return self.__class__(items)
        return items

    @classmethod
    def of(cls, *xs: tuple[Iterable[A], ...]):
        return cls(xs)

    def map[B](self, g: Callable[[A], B]):
        return self.__class__(pymap(g, self))

    @classmethod
    def pure(cls, a):
        return cls([a] * cls._size)

    def map2[B, C](self, g: Callable[[A, B], C], fb: NTupleBase[B]) -> NTupleBase[C]:
        if len(self) != len(fb):
            raise TypeError(f'map2 requires NTuples of the same length: {len(self)} != {len(fb)}')

        concat = []
        for i, a in enumerate(self):
            concat.append(g(a, fb[i]))
        return self.__class__(concat)

    def traverse(self, f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        traversed = f.pure(List())
        for item in self:
            traversed = map2(append_, traversed, g(item))
        return traversed.map(self.__class__)

ntuple_registry = {}

def NTuple(n: int, *args):
    if n <= 0:
        raise TypeError('NTuple requires a positive length')
    if n in ntuple_registry:
        cls = ntuple_registry[n]
    else:
        class NTuple_n(NTupleBase):
            _size = n
        ntuple_registry[n] = NTuple_n
        cls = NTuple_n

    if len(args) == 0:
        return cls
    return cls(args[0])
