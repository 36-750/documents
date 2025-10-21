#
# Forget is a profunctor whose second argument is a phantom type (ignored)
#
# newtype Forget r a b = Forget { runForget :: a -> r }
#
# This is isomorphic to Star (Const r) but arises enough that it is
# worth having a name for it.

from __future__    import annotations

from typing        import Callable

from ..Bicofunctor import Bicofunctor
from ..Const       import Const, runConst, makeConst, typeConst
from ..Either      import either_, Left, Right
from ..Maybe       import None_
from ..Monoids     import Monoid
from ..functions   import Function, compose, const, fst, snd
from ..utils       import MissingMonoid, eff

from .Choice       import Choice
from .Cochoice     import Cochoice
from .Strong       import Strong

__all__ = ['Forget', 'ForgetM']


class Forget[R, A](Strong, Cochoice, Choice, Bicofunctor):
    """A profunctor representing a mapping to a fixed type.

    The second type argument is a phantom type (i.e., ignored).

    newtype Forget r a b = Forget { runForget :: a -> r }

    This is isomorphic to Star (Const r) but arises enough that it is
    worth having a name for it.

    We extract the enclosed function with Forget.run.

    To act as a Choice, this needs a default argument supplied at
    construction. This also needs a Monoid interpretation of r for
    other constructions, so an optional Monoid can be supplied, and
    the default is then Monoid.munit. If not supplied, the Monoid is
    the generic Collect by default.

    """
    def __init__(
            self,
            a_to_r: Callable[[A], R],
            monoid: Monoid = MissingMonoid('Forget used as Choice or Bicofunctor')
    ):
        self._a_to_r = Function(a_to_r)
        self._monoid = monoid

    @classmethod
    def run(cls, fg):
        return fg._a_to_r

    def dimap(self, f, _):
        return Forget(compose(self._a_to_r, f), self._monoid)

    def into_first(self):
        return Forget(compose(self._a_to_r, fst), self._monoid)

    def into_second(self):
        return Forget(compose(self._a_to_r, snd), self._monoid)

    def unleft(self):
        return Forget(compose(Left, self._a_to_r), self._monoid)

    def unright(self):
        return Forget(compose(Right, self._a_to_r), self._monoid)

    def bicomap[B](self, f: Callable[[B], A], _g: Callable) -> Forget[R, B]:
        return Forget(compose(self._a_to_r, f), self._monoid)

    def into_left(self):
        return Forget(either_(self._a_to_r, const(self._monoid.munit)), self._monoid)

    def into_right(self):
        return Forget(either_(const(self._monoid.munit), self._a_to_r), self._monoid)

    def wander(self, f):   # wander : Applicative f => (a -> f b) -> (s -> f t)
        cls = typeConst(self._monoid)
        g = eff(makeConst(self._monoid), self._a_to_r, effect=cls)
        return Forget(compose(runConst, f(g)), self._monoid)

    def visit(self, f):
        cls = typeConst(self._monoid)
        g = eff(makeConst(self._monoid), self._a_to_r, effect=cls)
        pure = Const(self._monoid.munit, self._monoid).pure  # Could use as is, but use the function
        return Forget(compose(runConst, lambda s: f(pure, g, s)), self._monoid)

class ForgetM[R, A](Strong, Cochoice, Choice):
    """A profunctor representing a mapping to a fixed type.

    The second type argument is a phantom type (i.e., ignored).

    newtype ForgetM r a b = ForgetM { runForgetM :: a -> Maybe r }

    This is isomorphic to Star (Const r) but arises enough that it is
    worth having a name for it.

    We extract the enclosed function with Forget.run.

    """
    def __init__(self, r_to_a: Callable[[A], R]):
        self._a_to_mr = Function(r_to_a)

    @classmethod
    def run(cls, fg):
        return fg._a_to_mr

    def dimap(self, f, _):
        return ForgetM(compose(self._a_to_mr, f))

    def into_first(self):
        return ForgetM(compose(self._a_to_mr, fst))

    def into_second(self):
        return ForgetM(compose(self._a_to_mr, snd))

    def into_left(self):
        return ForgetM(either_(self._a_to_mr, const(None_())))

    def into_right(self):
        return ForgetM(either_(const(None_()), self._a_to_mr))

    def unleft(self):
        return ForgetM(compose(Left, self._a_to_mr))

    def unright(self):
        return ForgetM(compose(Right, self._a_to_mr))

    def bicomap[B](self, f: Callable[[B], A], _g: Callable) -> ForgetM[R, B]:
        return ForgetM(compose(self._a_to_mr, f))
