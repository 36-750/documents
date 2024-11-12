#
# The Pair type (a, b) as a Bifunctor
#
# This is the canonical product type, dual to Either.
#
# ruff: noqa: EM102, PLR2004

from __future__ import annotations

from collections.abc import Callable

from .Applicative import Applicative
from .Bifunctor   import Bifunctor
from .Functor     import map
from .Traversable import Traversable

__all__ = ['Pair', 'pair', 'fork', 'duplex']


class Pair[A, B](tuple, Bifunctor, Traversable):
    def __new__(cls, *contents):
        if len(contents) == 0 or len(contents) > 2:
            raise ValueError(f'Pair requires 2 values but {len(contents)} were given.')

        if len(contents) == 1 and isinstance(contents[0], tuple):
            tup = contents[0]
        else:
            tup = (contents[0], contents[1])

        return super().__new__(cls, tup)

    @property
    def with_first(self):
        "Returns the function x :-> (a, x) where a is the first component of this pair."
        return lambda x: Pair(self[0], x)

    @property
    def with_second(self):
        "Returns the function x :-> (x, b) where a is the second component of this pair."
        return lambda x: Pair(x, self[1])

    # A Bifunctor is a Functor in the second type variable
    #   map f == bimap id f
    def map[A, B](self, g: Callable[[A], B]):
        a, b = self
        return Pair(a, g(b))

    def bimap[C, D](self, f: Callable[[A], B], g: Callable[[C], D]):
        a, b = self
        return Pair(f(a), g(b))

    def traverse(self, _f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        a, b = self
        return map(self.with_first, g(b))


#
# Pair-based function combinators
#

def pair(x, y):
    "Forms a pair. A curriable, drop-in replacement for functions.pair."
    return Pair(x, y)


def fork(f, g):
    "Returns a function that maps x :-> (f(x), g(x))."
    def forked(*args, **kwds):
        return Pair(f(*args, **kwds), g(*args, **kwds))

    return forked

def duplex(f, g):
    "Returns a function that maps (x, y) :-> (f(x), g(y))."
    def forked(pair):
        x, y = pair
        return Pair(f(x), g(y))

    return forked
