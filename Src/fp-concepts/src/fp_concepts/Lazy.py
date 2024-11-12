#
# ATTN: Provisional
#

from __future__ import annotations

from typing          import Callable

from .Functor        import Functor
from .Applicative    import Applicative, map2
from .Monad          import Monad
from .Maybe          import Maybe, Some, None_, maybe
from .functions      import compose, identity

__all__ = ['Lazy',]


class Lazy[A](Monad):
    def __init__(self, thunk: Callable[[], A], value=None_()):
        self._thunk = thunk
        self._realized = value

    def __call__(self):
        return self.force

    @property
    def force(self):
        if not self._realized:
            self._realized = Some(self._thunk())
        return maybe(None, identity, self._realized)

    def map[B](self, g: Callable[[A], B]):
        return Lazy(compose(g, self._thunk), maybe(None_(), g, self._realized))

    @classmethod
    def pure(cls, a: A):
        return cls(lambda: a)
    
    def map2(self, g, fb):
        value = map2(g, self._realized, fb._realized)
        return Lazy(lambda: g(self._thunk(), fb._thunk()), value)

    def bind(self, g):
        def thunk():
            mb = g(self._thunk())
            return mb._thunk()
        return Lazy(thunk)

