#
# Star is a wrapper for the type a -> f b
# where f : Type -> Type.
#

from __future__    import annotations

from typing        import Callable

from ..Applicative import Applicative
from ..Either      import Left, Right, either_
from ..Functor     import Functor, lift, map
from ..Identity    import Identity
from ..Pair        import Pair
from ..Profunctor  import Profunctor
from ..functions   import compose

__all__ = ['Star']


class Star[A, B](Profunctor):
    """A wrapper for the type a -> f b for Functor f : Type -> Type.

    This is an instance of various classes:

    + ATTN

    """
    def __init__(self, a_to_fb: Callable[[A], Functor[B]], f: type[Functor] = Identity):
        self._fn = a_to_fb
        self._functor = f

    def run(self):
        return self._fn

    def dimap(self, f, g):
        return Star(compose(lift(g), self._fn, f), self._functor)

    def into_first(self):
        def inj_first(v):
            a, c = v
            return map(Pair(v).with_second, self._fn(a))
        return Star(inj_first, self._functor)

    def into_second(self):
        def inj_second(v):
            c, a = v
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


def traverseOf(opt, a_to_fb, effect: type[Applicative] = Identity):
    return Star.run(opt(Star(a_to_fb, effect)))
