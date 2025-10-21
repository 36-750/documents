#
# Sum (coproduct) type Either a b
#
# type Either a b = Left a | Right b
#
# ruff: noqa: N802, E731
#

from __future__      import annotations

from abc             import abstractmethod
from collections.abc import Callable
from typing          import TypeGuard, cast

from .Functor        import map
from .Applicative    import Applicative
from .Bifunctor      import Bifunctor
from .Monad          import Monad
from .Traversable    import Traversable


__all__ = ['Either', 'Left', 'Right', 'isLeft', 'isRight', 'either', 'either_', ]


class Either[A, B](Monad, Bifunctor, Traversable):
    @abstractmethod
    def from_left(self, default: A) -> A:
        ...

    @abstractmethod
    def from_right(self, default: B) -> B:
        ...

    @classmethod
    def pure(cls, b: B) -> Either[A, B]:
        return Right(b)

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
            return cls.pure(finished.value)

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

    def from_left(self, _default: A) -> A:
        return self._value

    def from_right(self, default: B) -> B:
        return default

    def map[C](self, _g: Callable[[B], C]) -> Either[A, C]:      # type: ignore
        return cast(Left[A, C], self)

    def map2[C, D](self, _g: Callable[[B, C], D], _fb: Either[A, C]) -> Either[A, D]:
        return cast(Left[A, D], self)

    def bind[C](self, _f: Callable[[B], Either[A, C]]) -> Either[A, C]:
        return cast(Left[A, C], self)

    def bimap[C, D](self, f: Callable[[A], C], _g: Callable[[B], D]) -> Either[C, D]:   # type: ignore
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

    def from_right(self, _default: B) -> B:
        return self._value

    def map[C](self, g: Callable[[B], C]) -> Right[A, C]:    # type: ignore
        return Right(g(self._value))

    def map2[C, D](self, g: Callable[[B, C], D], fc: Either[A, C]) -> Either[A, D]:
        if isLeft(fc):
            return cast(Left[A, D], fc)
        return Right(g(self._value, cast(Right[A, C], fc)._value))

    def bind[C](self, f: Callable[[B], Either[A, C]]) -> Either[A, C]:
        return f(self._value)

    def bimap[C, D](self, _f: Callable[[A], C],  g: Callable[[B], D]) -> Either[C, D]:    # type: ignore
        return Right(g(self._value))

    def traverse(self, _f: type[Applicative], g: Callable[[B], Applicative]) -> Applicative:  # g : a -> f b
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
        case _:   # Only applies if wrong type passed in
            return None   # type: ignore

def either_[A, B, C](f: Callable[[A], C], g: Callable[[B], C]) -> Callable[[Either[A, B]], C]:
    """Partial application of either on two arguments; returns the function m :--> either(f, g, m).

    This partial is a common use case for either, so this is provided as a convenience.
    The _ in the name is supposed to evoke the hole in the last argument.

    """
    return lambda m: either(f, g, m)
