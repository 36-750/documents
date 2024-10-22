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

from __future__ import annotations

from typing      import Callable, TypeGuard

from Functor     import Functor, map
from Applicative import Applicative
from Monad       import Monad
from Traversable import Traversable

__all__ = ['Maybe', 'None_', 'Some', 'maybe', 'isNone', 'isSome',]


class Maybe[A](Monad, Traversable):
    def get(self, default: A) -> A:
        ...

    def map[A, B](self, g: Callable[[A], B]) -> Maybe[B]:
        ...

    @classmethod
    def pure(cls, a: A) -> Maybe[A]:
        return Some(a)

    def map2[A, B, C](self, g: Callable[[A, B], C], fb: Maybe[B]) -> Maybe[C]:
        ...

    def bind(self, f: Callable[[A], Maybe[B]]) -> Maybe[B]:
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

    def traverse(self, f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        ...

class Some[A](Maybe[A]):
    __match_args__ = ('_value',)

    def __init__(self, value: A):
        self._value = value

    def __str__(self):
        return f'Some {self._value}'

    def __repr__(self):
        return f'Some({self._value})'

    def __eq__(self, other):
        if isinstance(other, Some):
            return self._value == other._value
        return False

    def get(self, default_: A) -> A:
        return self._value

    def map[A, B](self, g: Callable[[A], B]) -> Maybe[B]:
        try:
            return Some(g(self._value))
        except Exception:
            return None_()

    def map2[A, B, C](self, g: Callable[[A, B], C], fb: Maybe[B]) -> Maybe[C]:
        if isinstance(fb, None_):
            return fb
        return Some(g(self._value, fb._value))

    def bind(self, f: Callable[[A], Maybe[B]]) -> Maybe[B]:
        return f(self._value)

    def traverse(self, _f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        return map(Some, g(self._value))

class None_[A](Maybe[A]):   # The name None is already taken
    def __str__(self):
        return f'None'

    def __repr__(self):
        return f'None_()'

    def __eq__(self, other):
        if isinstance(other, None_):
            return True
        return False

    def get(self, default: A) -> A:
        return default

    def map[A, B](self, g: Callable[[A], B]) -> Maybe[B]:
        return self

    def map2[A, B, C](self, g: Callable[[A, B], C], fb: Maybe[B]) -> Maybe[C]:
        return self

    def bind(self, f: Callable[[A], Maybe[B]]) -> Maybe[B]:
        return self

    def traverse(self, _f: type[Applicative], _g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        return self

def isNone(x: Maybe[A]) -> TypeGuard[None_]:
    return isinstance(x, None_)

def isSome(x: Maybe[A]) -> TypeGuard[Some]:
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
            return None  # Only applies if wrong type passed in
