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
from .functions   import is_iterable, is_sequence

__all__ = ['Pair', 'pair', 'fork', 'duplex']


class Pair[A, B](tuple, Bifunctor, Traversable):
    """A 2-tuple with benefits.

    This is an instance of tuple that is an instance of Bifunctor,
    Functor (in the second component), and Traversable.

    It can be constructed with two values, like Pair(1, 2),
    or with a single iterable *of length 2*, like Pair([1, 2]).
    An exception is raised if other than two components are
    supplied.

    """
    def __new__(cls, *contents):
        if len(contents) == 0 or len(contents) > 2:
            raise ValueError(f'Pair requires 2 values but {len(contents)} were given.')

        if len(contents) == 1:
            if is_sequence(contents[0]):  # ATTN: can just do iterable case
                tup = contents[0]
            elif is_iterable(contents[0]):
                tup = list(contents[0])
            else:
                raise ValueError('Two values or a sequence of two values needed to make a Pair.')
        else:
            tup = (contents[0], contents[1])

        if len(tup) != 2:
            raise ValueError(f'Pair requires 2 values but {len(tup)} were given.')

        return super().__new__(cls, tup)

    @property
    def with_first(self):
        "Returns the function x :-> (a, x) where a is the first component of this pair."
        return lambda x: Pair(self[0], x)

    @property
    def with_second(self):
        "Returns the function x :-> (x, b) where b is the second component of this pair."
        return lambda x: Pair(x, self[1])

    # A Bifunctor is a Functor in the second type variable
    #   map f == bimap id f
    def map[D](self, g: Callable[[B], D]) -> Pair[A, D]:  # type: ignore  # mypy error
        a, b = self
        return Pair(a, g(b))

    def bimap[C, D](self, f: Callable[[A], C], g: Callable[[B], D]) -> Pair[C, D]:   # type: ignore  # mypy error
        a, b = self
        return Pair(f(a), g(b))

    def traverse(self, _f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        a, b = self
        return map(self.with_first, g(b))


#
# Pair-based function combinators
#
# Use pair instead of functions.pair.
#

def pair(x, y):
    "Forms a pair. A curry-able, drop-in replacement for functions.pair."
    return Pair(x, y)


def fork(f, g):
    "Returns a function that maps x :-> (f(x), g(x))."
    def forked(*args, **kwds):
        return Pair(f(*args, **kwds), g(*args, **kwds))

    return forked

def duplex(f, g):
    "Returns a function that maps (x, y) :-> (f(x), g(y))."
    def duplexed(pair):
        x, y = pair
        return Pair(f(x), g(y))

    return duplexed
