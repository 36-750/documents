#
# Sum (coproduct) type Either a b
#
# type Either a b = Left a | Right b
#
# ...
#
from __future__   import annotations

from typing       import Callable, TypeGuard

from .Functor     import Functor
from .Applicative import Applicative
from .Monad       import Monad
from .Bifunctor   import Bifunctor
from .Traversable import Traversable


__all__ = ['Either', 'Left', 'Right', 'isLeft', 'isRight', 'either',]


class Either[A, B](Monad, Bifunctor, Traversable):
    def from_left(self, default: A) -> A:
        ...

    def from_right(self, default: B) -> B:
        ...

    def map[C](self, g: Callable[[B], C]) -> Either[A, C]:
        ...

    @classmethod
    def pure(cls, b: B) -> Either[A, B]:
        return Some(a)

    def map2[C, D](self, g: Callable[[B, C], D], fb: Either[A, C]) -> Either[A, D]:
        ...

    def bind[C](self, f: Callable[[B], Either[A, C]]) -> Either[A, C]:
        ...

    def bimap[C, D](self, f: Callable[[A], C],  g: Callable[[B], D]) -> Either[C, D]:
        ...

    @classmethod
    def __do__(cls, make_generator) -> Either[A, B]:
        generator = make_generator()
        f = lambda result: generator.send(result)
    
        try:
            x = f(None)
            while True:
                if isLeft(x):
                    return x
                x = x.bind(f)
        except StopIteration as finished:
            return Right(finished.value)

    def __eq__(self, other):
        ...

class Left[A, B](Either[A, B]):
    __match_args__ = ('_value',)

    def __init__(self, value: A):
        self._value = value

    def __str__(self):
        return f'Left {self._value}'

    def __repr__(self):
        return f'Left({self._value})'

    def __eq__(self, other):
        if isinstance(other, Left):
            return self._value == other._value
        return False

    def from_left(self, default: A) -> A:
        return self._value

    def from_right(self, default: B) -> B:
        return default

    def map[B, C](self, g: Callable[[B], C]) -> Either[A, C]:
        return self

    def map2[C, D](self, g: Callable[[B, C], D], fb: Either[A, C]) -> Either[A, D]:
        return self

    def bind[C](self, f: Callable[[B], Either[A, C]]) -> Either[A, C]:
        return self

    def bimap[C, D](self, f: Callable[[A], C],  g: Callable[[B], D]) -> Either[C, D]:
        return Left(f(self._value))

    def traverse(self, f: type[Applicative], _g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        return f.pure(self)

class Right[A, B](Either[A, B]):
    __match_args__ = ('_value',)

    def __init__(self, value: B):
        self._value = value

    def __str__(self):
        return f'Right {self._value}'

    def __repr__(self):
        return f'Right({self._value})'

    def __eq__(self, other):
        if isinstance(other, Right):
            return self._value == other._value
        return False

    def from_left(self, default: A) -> A:
        return default

    def from_right(self, default: B) -> B:
        return self._value

    def map[C](self, g: Callable[[B], C]) -> Right[C]:
        return Right(g(self._value))

    def map2[C, D](self, g: Callable[[B, C], D], fc: Either[A, C]) -> Either[A, D]:
        if isLeft(fc):
            return fc
        return Right(g(self._value, fc._value))

    def bind[C](self, f: Callable[[B], Either[A, C]]) -> Either[A, C]:
        return f(self._value)

    def bimap[C, D](self, f: Callable[[A], C],  g: Callable[[B], D]) -> Either[C, D]:
        return Right(g(self._value))

    def traverse(self, _f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        return map(Right, g(self._value))

def isLeft[A, B](x: Either[A, B]) -> TypeGuard[Left[A, B]]:
    return isinstance(x, Left)

def isRight[A, B](x: Either[A, B]) -> TypeGuard[Right[A, B]]:
    return isinstance(x, Right)

def either[A, B, C](f: Callable[[A], C], g: Callable[[B], C], m: Either[A, B]) -> C:
    """Extracts a transformed value from an Either by case analysis.

    If given a Left, apply the function f to its value; if given a Right,
    apply the function g. Returns the resulting value.

    """
    match m:
        case Left(a):
            return f(a)
        case Right(b):
            return g(b)
        case _:
            return None  # Only applies if wrong type passed in
