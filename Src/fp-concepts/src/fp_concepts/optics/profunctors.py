"""Concrete profunctors for use in optics methods.

"""
from __future__    import annotations

from typing        import Callable, Self

from ..Bicofunctor import Bicofunctor
from ..Const       import Const, runConst, makeConst, typeConst
from ..Either      import either_, Left, Right
from ..Functor     import Functor, lift, map                   # pylint: disable=redefined-builtin
from ..Identity    import Identity
from ..Maybe       import None_
from ..Monoids     import Monoid
from ..Pair        import Pair
from ..functions   import Function, compose, const, fst, snd
from ..utils       import MissingMonoid, eff

from .Choice       import Choice
from .Cochoice     import Cochoice
from .Strong       import Strong

__all__ = ['Forget', 'ForgetM', 'Star']


#
# Forget is a profunctor whose second argument is a phantom type (ignored)
#
# newtype Forget r a b = Forget { runForget :: a -> r }
#
# This is isomorphic to Star (Const r) but arises enough that it is
# worth having a name for it.

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
        super().__init__()

    @classmethod
    def run(cls, fg: Self):
        return fg._a_to_r    # pylint: disable=protected-access

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
        super().__init__()

    @classmethod
    def run(cls, fg):
        return fg._a_to_mr    # pylint: disable=protected-access

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

#
# Star is a profunctor that lifts a functor into a profunctor.
#
# newtype Star f a b = Star { runStar :: a -> f b }
#
# This is represents Kleisli arrows.
#

# class Star[A, B](Strong, Choice):
#     "ATTN"
#     def __init__(self, a_to_fb: Callable[[A], Functor[B]], effect: type[Functor]):
#         self._a_to_fb = Function(a_to_fb)
#         self._effect = effect
#         super().__init__()
#
#     def dimap[C, D](self, f: Callable[[C], A], g: Callable[[B], D]) -> Star[C, D]:
#         return Star(compose(lift(g), self._a_to_fb, f), self._effect)


class Star[A, B](Strong, Choice):
    """A wrapper for the type a -> f b for Functor f : Type -> Type.

    This is an instance of various classes:

    + ATTN

    """
    def __init__(self, a_to_fb: Callable[[A], Functor[B]], effect: type[Functor] = Identity):
        self._fn = a_to_fb
        self._functor = effect

    def run(self):
        return self._fn

    def dimap(self, f, g):
        return Star(compose(lift(g), self._fn, f), self._functor)

    def into_first(self):
        def inj_first(v):
            a, _ = v
            return map(Pair(v).with_second, self._fn(a))
        return Star(inj_first, self._functor)

    def into_second(self):
        def inj_second(v):
            _, a = v
            return map(Pair(v).with_first, self._fn(a))
        return Star(inj_second, self._functor)

    def into_left(self):
        # require applicative _functor
        g = either_(compose(lift(Left), self._fn), compose(self._functor.pure, Right))
        return Star(g, self._functor)

    def into_right(self):
        # require applicative _functor
        g = either_(compose(self._functor.pure, Left), compose(lift(Right), self._fn))
        return Star(g, self._functor)

    def wander1(self, f):  # f : (a -> f b) -> (s -> f t)
        g = f(self._fn)
        return Star(g, self._functor)

    def wander(self, f):  # f : (a -> f b) -> (s -> f t)
        g = f(self._fn)
        return Star(g, self._functor)

    def visit(self, f):   # f : forall r. (r -> f r) -> (a -> f b) -> (s -> f t)
        # require applicative _functor
        g = f(self._functor.pure, self._fn)
        return Star(g, self._functor)
