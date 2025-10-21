#
# Choice (aka Cocartesian) is the trait
#
# trait Profunctor p => Choice p where
#     into_left  : p a b -> p (Either a c) (Either b c)
#     into_right : p a b -> p (Either c a) (Either c b)
#
# One of to_first or to_second must be defined for an instance.
#

from __future__   import annotations

from abc          import abstractmethod
from typing       import Callable, Protocol, cast

from ..Either     import Either, Left, Right, either
from ..Profunctor import Profunctor
from ..functions  import identity

__all__ = ['Choice', 'into_left', 'into_right']


def swap[S, T](x: Either[S, T]) -> Either[T, S]:
    return either(Right, Left, x)

class Choice[A, B](Profunctor, Protocol):
    """Profunctors with ``strength'' using coproducts for annotation.

    Specifically, we can annotate the components of the profunctor
    with information of an arbitrary type, as a disjoint union.
    The methods into_left and into_right inject that annotation as
    either the first or second part of a disjoint union (Either).

    This trait is also known as Cocartesian in some treatments.

    trait Profunctor p => Choice p where
        into_left  : p a b -> p (Either a c) (Either b c)
        into_right : p a b -> p (Either c a) (Either c b)

    One of into_left or into_right must be defined for a valid instance.

    """
    # ATTN: Make this a Protocol only?
    @abstractmethod
    def dimap[C, D](self, f: Callable[[C], A], g: Callable[[B], D]) -> Choice[C, D]:
        ...

    def into_left[C](self) -> Choice[Either[A, C], Either[B, C]]:
        p = self.into_right().dimap(swap, swap)                       # type: ignore
        return cast(Choice[Either[A, C], Either[B, C]], p)

    def into_right[C](self) -> Choice[Either[C, A], Either[C, B]]:
        p = self.into_left().dimap(swap, swap)                       # type: ignore
        return cast(Choice[Either[C, A], Either[C, B]], p)

def into_left[A, B, C](p_ab: Choice[A, B]) -> Choice[Either[A, C], Either[B, C]]:
    return p_ab.into_left()

def into_right[A, B, C](p_ab: Choice[A, B]) -> Choice[Either[C, A], Either[C, B]]:
    return p_ab.into_right()

def prism[A, B, S, T](
        construct: Callable[[B], T],
        match: Callable[[S], Either[T, A]]
) -> Callable[[Choice[A, B]], Choice[S, T]]:
    # (s -> Either s a) (Either s b -> t)
    def the_prism(p_ab: Choice[A, B]) -> Choice[S, T]:
        p_sa_sb: Choice[Either[T, A], Either[T, B]] = into_right(p_ab)
        p = p_sa_sb.dimap(match, lambda esb: either(identity, construct, esb))
        return cast(Choice[S, T], p)

    return the_prism

def _left_matcher[A, B, C](x: Either[A, B]) -> Either[Either[C, B], A]:
    match x:
        case Left(y):
            return Right(y)
        case Right(y):
            return Left(Right(y))
        case _:  # Cannot happen with right type input
            raise TypeError('Wrong type for left')

def _right_matcher[A, B, C](x: Either[A, B]) -> Either[Either[A, C], B]:
    match x:
        case Left(y):
            return Left(Left(y))
        case Right(y):
            return Right(y)
        case _:  # Cannot happen with right type input
            raise TypeError('Wrong type for right')

left = prism(Left, _left_matcher)      # type: ignore  # why not inferred??
right = prism(Right, _right_matcher)   # type: ignore  # why not inferred??
