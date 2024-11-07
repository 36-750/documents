from __future__ import annotations

from functools       import partial, wraps
from typing          import Callable, Optional

from .Functor        import Functor, map
from .Monoids        import Monoid, munit, mcombine, Trivial
from .functions      import curry, pair, fn_eval

__all__ = ['Applicative', 'map2', 'combine', 'pure', 'ap', 'IdentityA', ]


#
# Applicative as a mixin
#

class Applicative(Functor):
    @classmethod
    def pure(cls, a):
        ...

    def map2(self, g, fb):
        ...

    @classmethod
    @property
    def unit(cls):
        return cls.pure( () )

    def combine(self, fb):
        return self.map2(pair, fb)

    def ap(self, fb):
        return self.map2(fn_eval, fb)


def map2(g, fa, fb):
    return fa.map2(g, fb)

def combine(fa, fb):
    return fa.combine(fb)

def pure(fa, a):
    return fa.pure(a)

def ap(fa_to_b: Applicative | Callable, fa: Applicative, *fs: Applicative, auto_curry=True) -> Applicative:
    if not isinstance(fa_to_b, Applicative):
        if auto_curry:
            fa_to_b = fa.pure(curry(fa_to_b))
        else:
            fa_to_b = fa.pure(fa_to_b)
    # elif auto_curry:
    #     fa_to_b = fa_to_b.map(curry)  # ATTN: PROVISIONAL

    fb = fa_to_b.ap(fa)
    for fx in fs:
        fb = fb.ap(fx)
    return fb


# A copy of the Identity Functor that is only an Applicative
# This is useful as a default applicative in infrastructure
# modules that would lead to circularity if loading Identity
# module. See also IdentityM in case a default Monad is needed.

class IdentityA[A](Applicative):
    """A default Applicative that mimics Identity without Monad or Traversable.

    This is useful in defaults only infrastructure modules in this package,
    like Monad and Traversable, that Identity actually loads. Users should
    not use this explicitly.

    """
    __match_args__ = ('value',)

    def __init__(self, x: A):
        self._value = x

    def __str__(self):
        return f'IdentityA {self._value}'

    def __repr__(self):
        return f'IdentityA({self._value})'

    @classmethod
    def run(cls, fa: IdentityA[A]) -> A:
        return fa._value

    def map(self, g: Callable[[A], B]) -> IdentityA[B]:
        return IdentityA(g(self._value))

    @classmethod
    def pure(cls, x: A) -> IdentityA[A]:
        return IdentityA(x)

    def map2[B, C](self, g: Callable[[A, B], C], fb: IdentityA[B]) -> IdentityA[C]:
        return IdentityA(g(self._value, fb._value))
