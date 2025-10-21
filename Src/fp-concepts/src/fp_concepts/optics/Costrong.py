#
# Costrong (aka Cocartesian) is the trait
#
# trait Profunctor p => Costrong p where
#     unfirst  : p (a, c) (b, c) -> p a b
#     unsecond : p (c, a) (c, b) -> p a b
#
# One of unfirst or unsecond must be defined for an instance.
#

from __future__   import annotations

from typing       import cast

from ..Profunctor import Profunctor
from ..functions  import swap

__all__ = ['Costrong', 'unfirst', 'unsecond']


class Costrong[A, B](Profunctor):
    """Profunctors with ``co-strength''

    Specifically, we can extract the annotated components of the
    profunctor into a profunctor with unannotated components. The
    methods unfirst and unsecond project away that annotation as
    either the first or second element of the pair.

    trait Profunctor p => Costrong p where
        unfirst  : p (a, c) (b, c) -> p a b
        unsecond : p (c, a) (c, b) -> p a b

    One of unfirst or unsecond must be defined for an instance.

    """
    def unfirst(self):
        return unsecond(self.dimap(swap, swap))

    def unsecond(self):
        return unfirst(self.dimap(swap, swap))

def unfirst[A, B, C](annotated: Costrong[tuple[A, C], tuple[B, C]]) -> Costrong[A, B]:
    return cast(Costrong[A, B], annotated.unfirst())

def unsecond[A, B, C](annotated: Costrong[tuple[C, A], tuple[C, B]]) -> Costrong[A, B]:
    return cast(Costrong[A, B], annotated.unsecond())
