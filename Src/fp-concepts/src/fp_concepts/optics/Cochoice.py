#
# Cochoice (aka Cocartesian) is the trait
#
# trait Profunctor p => Cochoice p where
#     unleft  : p a b -> p (Either a c) (Either b c)
#     unright : p a b -> p (Either c a) (Either c b)
#
# One of to_first or to_second must be defined for an instance.
#

from __future__   import annotations

from typing       import Protocol, cast

from ..Either     import Either, Left, Right, either
from ..Profunctor import Profunctor

__all__ = ['Cochoice', 'unleft', 'unright']


def swap[S, T](x: Either[S, T]) -> Either[T, S]:
    return either(Right, Left, x)

class Cochoice[A, B](Profunctor, Protocol):
    """Profunctors with ``costrength'' using coproducts for annotation.

    Specifically, we can annotate the components of the profunctor
    with information of an arbitrary type, as a disjoint union.
    The methods unleft and unright inject that annotation as
    either the first or second part of a disjoint union (Either).

    Specifically, we can extract the annotated components of the
    profunctor into a profunctor with unannotated components. The
    methods unfirst and unsecond extract that annotation as
    either the left or right elements of a disjoint union (Either).

    trait Profunctor p => Cochoice p where
        unleft  : p (Either a c) (Either b c) -> p a b
        unright : p (Either c a) (Either c b) -> p a b

    One of unleft or unright must be defined for a valid instance.

    """
    def unleft[C](self):
        return unright(self.dimap(swap, swap))

    def unright[C](self):
        return unleft(self.dimap(swap, swap))

def unleft[A, B, C](annotated: Cochoice[Either[A, C], Either[B, C]]) -> Cochoice[A, B]:
    return cast(Cochoice[A, B], annotated.unleft())

def unright[A, B, C](annotated: Cochoice[Either[C, A], Either[C, B]]) -> Cochoice[A, B]:
    return cast(Cochoice[A, B], annotated.unright())
