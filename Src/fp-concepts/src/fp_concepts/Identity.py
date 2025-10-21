#
# The Identity Functor
#
# This provides a trivial functorial context. Useful when
# a functorial context is needed to match types but is
# otherwise window dressing.
#
# It is a Monad and Applicative trivially.
#
# newtype Identity a = Identity { runIdentity : a }
#

from __future__ import annotations

from collections.abc import Callable

from .Applicative import Applicative
from .Functor     import map
from .Monad       import Monad
from .Traversable import Traversable

__all__ = ['Identity',]


class Identity[A](Monad, Traversable):
    __match_args__ = ('_value',)

    def __init__(self, x: A):
        self._value = x

    def __str__(self):
        return f'Identity {self._value}'

    def __repr__(self):
        return f'Identity({self._value})'

    @classmethod
    def run(cls, fa: Identity[A]) -> A:
        return fa._value

    def map[B](self, g: Callable[[A], B]) -> Identity[B]:
        return Identity(g(self._value))

    @classmethod
    def pure(cls, x: A) -> Identity[A]:
        return Identity(x)

    def map2[B, C](self, g: Callable[[A, B], C], fb: Identity[B]) -> Identity[C]:
        return Identity(g(self._value, fb._value))

    def bind[B](self, g: Callable[[A], Identity[B]]) -> Identity[B]:
        return g(self._value)

    def traverse(self, _f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        return map(Identity, g(self._value))
