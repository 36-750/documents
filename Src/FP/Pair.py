#
# The Pair type (a, b) as a Bifunctor
#
# This is the canonical product type, dual to Either.
#

from __future__   import annotations

from typing       import Callable

from .Functor     import Functor, map
from .Applicative import Applicative
from .Bifunctor   import Bifunctor
from .Traversable import Traversable

__all__ = ['Pair', 'fork', 'duplex']


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
        return lambda x: Pair(1, self[1])

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
