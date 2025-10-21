#
# The Dictionary as a Functor
#
# Instances for Foldable and Traversable may not
# be fully lawful as two dicts can be equal in the large
# though their key orders may differ.  We ignore that
# for the convenience of having the methods.
#
# ruff: noqa: N802
#

from __future__ import annotations

from collections.abc import Callable

from .Applicative    import Applicative
from .Functor        import Functor, map
from .List           import List
from .Monoids        import Monoid
from .Traversable    import sequence
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

    def map[B](self, g: Callable[[V], B]):
        return self.__class__({k: g(v) for k, v in self.items()})

    def imap[B](self, g: Callable[[K, V], B]):
        return self.__class__({k: g(k, v) for k, v in self.items()})

    def foldM[M](self, f: Callable[[V], M], monoid: Monoid) -> M:
        r = monoid.munit
        for v in self.values():
            m = f(v)
            r = monoid.mcombine(r, m)
        return r

    def fold[B](self, f: Callable[[B, V], B], initial: B) -> B:
        acc = initial
        for v in self.values():
            acc = f(acc, v)
        return acc

    def ifoldM[M](self, f: Callable[[K, V], M], monoid: Monoid) -> M:
        r = monoid.munit
        for k, v in self.items():
            m = f(k, v)
            r = monoid.mcombine(r, m)
        return r

    def ifold[B](self, f: Callable[[K, B, V], B], initial: B) -> B:
        acc = initial
        for k, v in self.items():
            acc = f(k, acc, v)
        return acc

    def traverse(self, f: type[Applicative], g: Callable[[V], Applicative]) -> Applicative:   # Hard to type properly in Python
        spine = sequence(List(map(with_fst(k), g(v)) for k, v in self.items()), f)
        return map(lambda kvs: Dict.of(*kvs), spine)

    def itraverse(self, f: type[Applicative], g: Callable[[K, V], Applicative]) -> Applicative:   # Hard to type properly in Python
        spine = sequence(List(map(with_fst(k), g(k, v)) for k, v in self.items()), f)
        return map(lambda kvs: Dict.of(*kvs), spine)
