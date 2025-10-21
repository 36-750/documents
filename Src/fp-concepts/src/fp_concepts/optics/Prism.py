from __future__   import annotations

from typing       import Callable, cast

from .Choice      import Choice, into_right
from ..Either     import Either, Left, Right, either
from .Optic       import Optic, OpticIs
from ..functions  import identity

__all__ = ['Prism', 'prism', 'left', 'right']


class Prism[A, B, S, T](Optic):
    def __init__(self, cab_to_cst: Callable[[Choice[A, B]], Choice[S, T]]):
        self._cab_to_cst: Callable[[Choice[A, B]], Choice[S, T]] = cab_to_cst
        super().__init__(cab_to_cst, OpticIs.PRISM)

# class SimplePrism[A, B](Prism[A, B, A, B]):
#     def __init__(self, cab_to_cab: Callable[[Choice[A, B]], Choice[A, B]]):
#         super().__init__(cab_to_cab)

def prism[A, B, S, T](
        construct: Callable[[B], T],
        match: Callable[[S], Either[T, A]]
) -> Prism[A, B, S, T]:
    def the_prism(p_ab: Choice[A, B]) -> Choice[S, T]:
        p_sa_sb: Choice[Either[T, A], Either[T, B]] = into_right(p_ab)
        p = p_sa_sb.dimap(match, lambda esb: either(identity, construct, esb))
        return cast(Choice[S, T], p)

    return Prism(the_prism)

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
