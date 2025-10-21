#
# Cartesian (aka Strong) is the trait
#
# trait Profunctor p => Cartesian p where
#     to_first  : p a b -> p (a, c) (b, c)
#     to_second : p a b -> p (c, a) (c, b)
#
# One of to_first or to_second must be defined for an instance.
#

from __future__   import annotations

from typing       import Callable, cast

from ..Profunctor import Profunctor, dimap
from ..functions  import compose, identity

__all__ = ['Cartesian', 'into_first', 'into_second', 'lens']

def swap(v):
    return (v[1], v[0])


class Cartesian[A, B](Profunctor):
    """Profunctors with ``strength''

    Specifically, we can annotate the components of the profunctor
    with information of an arbitrary type, as a pair. The methods
    into_first and into_second inject that annotation as either the
    first or second element of the pair.

    This trait is also known as Strong in many treatments.

    trait Profunctor p => Cartesian p where
        into_first  : p a b -> p (a, c) (b, c)
        into_second : p a b -> p (c, a) (c, b)

    One of into_first or into_second must be defined for a valid instance.

    """
    def into_first[C](self) -> Cartesian[tuple[A, C], tuple[B, C]]:
        p = self.into_second().dimap(swap, swap)
        return cast(Cartesian[tuple[A, C], tuple[B, C]], p)

    def into_second[C](self) -> Cartesian[tuple[C, A], tuple[C, B]]:
        p = self.into_first().dimap(swap, swap)
        return cast(Cartesian[tuple[C, A], tuple[C, B]], p)

def into_first[A, B, C](p_ab: Cartesian[A, B]) -> Cartesian[tuple[A, C], tuple[B, C]]:
    return p_ab.into_first()

def into_second[A, B, C](p_ab: Cartesian[A, B]) -> Cartesian[tuple[C, A], tuple[C, B]]:
    return p_ab.into_second()

def lens[A, B, S, T](
        getter: Callable[[S], A],
        setter: Callable[[S, B], T]
) -> Callable[[Cartesian[A, B]], Cartesian[S, T]]:
    def the_lens(p_ab: Cartesian[A, B]) -> Cartesian[S, T]:
        p_ac_bc: Cartesian[tuple[A, S], tuple[B, S]] = p_ab.into_first()
        p = p_ac_bc.dimap(lambda s: (getter(s), s),
                          lambda b_s: setter(*b_s))
        return cast(Cartesian[S, T], p)

    return the_lens
