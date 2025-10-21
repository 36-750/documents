#
# The Maybe Monad
#
# type Maybe a = None | Some a
#
# This represents a context in which a value of a particular type
# may be present or may be missing. It is a Functor, an Applicative,
# and a Monad.
#
# We can destructure Maybe's with pattern matching or the maybe
# function, the functions isNone and isSome provide (type guarding)
# predicates.
#
# See List for utility functions map_maybe and cat_maybes.
#
# ruff: noqa: N801, N802, E731
#

from __future__ import annotations

from abc             import ABC, abstractmethod
from collections.abc import Callable
from typing          import TypeGuard, cast

from .Alternative import Alternative
from .Applicative import Applicative
from .Functor     import map
from .Monad       import Monad
from .Traversable import Traversable
from .Unit        import Unit

__all__ = ['Maybe', 'None_', 'Some', 'maybe', 'maybe_', 'isNone', 'isSome',]


class Maybe[A](Monad, Traversable, Alternative, ABC):
    @abstractmethod
    def get(self, default: A) -> A:
        ...

    @abstractmethod
    def map[B](self, g: Callable[[A], B]) -> Maybe[B]:
        ...

    @classmethod
    def pure(cls, a: A) -> Maybe[A]:
        return Some(a)

    @abstractmethod
    def map2[B, C](self, g: Callable[[A, B], C], fb: Maybe[B]) -> Maybe[C]:
        ...

    @property
    def empty(self):
        return None_()

    def alt(self, fb: Maybe[A]) -> Maybe[A]:   # type: ignore
        if not self:
            return fb
        return self

    @abstractmethod
    def bind[B](self, f: Callable[[A], Maybe[B]]) -> Maybe[B]:
        ...

    @classmethod
    def __do__(cls, make_generator) -> Maybe[A]:
        generator = make_generator()
        f = lambda result: generator.send(result)

        try:
            x = f(None)
            while True:
                if isNone(x):
                    return x
                x = x.bind(f)
        except StopIteration as finished:
            return Some(finished.value)

    @abstractmethod
    def traverse(self, f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        ...

class Some[A](Maybe[A]):
    __match_args__ = ('_value',)

    def __init__(self, value: A):
        self._value = value

    def __str__(self):
        return f'Some {str(self._value)}'

    def __repr__(self):
        return f'Some({repr(self._value)})'

    def __eq__(self, other):
        if isinstance(other, Some):
            return self._value == other._value
        return False

    def __bool__(self):
        return True

    def get(self, _default: A) -> A:
        return self._value

    def map[B](self, g: Callable[[A], B]) -> Maybe[B]:
        try:
            return Some(g(self._value))
        except Exception:
            return None_()

    def map2[B, C](self, g: Callable[[A, B], C], fb: Maybe[B]) -> Maybe[C]:
        if isinstance(fb, None_):
            return fb
        return Some(g(self._value, fb._value))  # type: ignore

    def bind[B](self, f: Callable[[A], Maybe[B]]) -> Maybe[B]:
        return f(self._value)

    def traverse(self, _f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        return map(Some, g(self._value))

    # def itraverse[I](self, _f: type[Applicative], g: Callable[[I, A], Applicative]) -> Applicative:
    def itraverse(self, _f: type[Applicative], g: Callable[[Unit, A], Applicative]) -> Applicative:
        # g : () -> a -> f b
        return map(Some, g((), self._value))

class None_[A](Maybe[A]):   # The name None is already taken
    def __str__(self):
        return 'None'

    def __repr__(self):
        return 'None_()'

    def __eq__(self, other):
        if isinstance(other, None_):
            return True
        return False

    def __bool__(self):
        return False

    def get(self, default: A) -> A:
        return default

    def map[B](self, _g: Callable[[A], B]) -> Maybe[B]:
        return cast(None_[B], self)

    def map2[B, C](self, _g: Callable[[A, B], C], _fb: Maybe[B]) -> Maybe[C]:
        return cast(None_[C], self)

    def bind[B](self, _f: Callable[[A], Maybe[B]]) -> Maybe[B]:
        return cast(None_[B], self)

    def traverse(self, f: type[Applicative], _g: Callable[[A], Applicative]) -> Applicative:
        # g : a -> f b
        return f.pure(self)

    def itraverse[I](self, f: type[Applicative], _g: Callable[[I, A], Applicative]) -> Applicative:
        # g : () -> a -> f b
        return f.pure(self)

def isNone[A](x: Maybe[A]) -> TypeGuard[None_]:
    return isinstance(x, None_)

def isSome[A](x: Maybe[A]) -> TypeGuard[Some]:
    return isinstance(x, Some)

def maybe[A, B](default: B, f: Callable[[A], B], m: Maybe[A]) -> B:
    """Extracts a transformed value from a Maybe by case analysis.

    If given a None_, return the specified value (i.e., apply the
    constant function to its value); if given a Some,
    apply the function f. Returns the resulting value.

    """
    match m:
        case None_():
            return default
        case Some(b):
            return f(b)
        case _:
            raise TypeError('maybe applied to a non-Maybe type')

def maybe_[A, B](default: B, f: Callable[[A], B]) -> Callable[[Maybe[A]], B]:
    """Partial application of maybe on two arguments; returns the function m :--> maybe(f, g, m).

    This partial is a common use case for maybe, so this is provided as a convenience.
    The _ in the name is supposed to evoke the hole in the last argument.

    """
    return lambda m: maybe(default, f, m)
