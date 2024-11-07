#
# The Dictionary as a Functor
#
# Instances for Foldable and Traversable may not
# be fully lawful as two dicts can be equal in the large
# though their key orders may differ.  We ignore that
# for the convenience of having the methods.
#

from __future__ import annotations

from collections.abc import Iterable
from typing          import Callable

from .Functor        import Functor, IndexedFunctor, map
from .Applicative    import Applicative
from .Foldable       import Foldable, IndexedFoldable
from .Traversable    import Traversable, IndexedTraversable, sequence
from .Monoids        import Monoid
from .List           import List
from .functions      import with_fst

__all__ = ['Dict']


#
# Dictionary k v as a Functor
#

class Dict[K, V](dict, Functor):
    def __new__(cls, *args, **kwds):
        return super().__new__(cls, *args, **kwds)

    @classmethod
    def of(cls, *xs: tuple[K, V]):
        return cls(xs)

    def map(self, g: Callable[[V], B]):
        return self.__class__({k: g(v) for k, v in self.items()})

    def imap(self, g: Callable[[K, V], B]):
        return self.__class__({k: g(k, v) for k, v in self.items()})

    def foldM[M](self, f: Callable[[V], M], monoid: Monoid) -> M:
        r = monoid.munit
        for v in self.values():
            m = g(v)
            r = monoid.mcombine(r, m)
        return r

    def fold[B](self, f: Callable[[B, A], B], initial: B) -> B:
        acc = initial
        for v in self.values():
            acc = f(acc, v)
        return acc

    def ifoldM[M](self, f: Callable[[K, A], M], monoid: Monoid) -> M:
        r = monoid.munit
        for k, v in self.items():
            m = g(k, v)
            r = monoid.mcombine(r, m)
        return r

    def ifold[B](self, f: Callable[[K, B, A], B], initial: B) -> B:
        acc = initial
        for k, v in self.items():
            acc = f(k, acc, v)
        return acc

    def traverse(self, f: type[Applicative], g: Callable) -> Applicative:   # Hard to type properly in Python
        spine = sequence(List(map(with_fst(k), g(v)) for k, v in self.items()), f)
        return map(lambda kvs: Dict.of(*kvs), spine)

    def itraverse(self, f: type[Applicative], g: Callable[[I, A], Applicative]) -> Applicative:   # Hard to type properly in Python
        spine = sequence(List(map(with_fst(k), g(k, v)) for k, v in self.items()), f)
        return map(lambda kvs: Dict.of(*kvs), spine)
