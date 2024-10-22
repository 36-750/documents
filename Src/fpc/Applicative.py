from __future__ import annotations

from functools       import partial, wraps
from typing          import Callable, Optional

from Functor         import Functor, map
from Monoid          import Monoid, munit, mcombine, Trivial
from functions       import curry, pair, fn_eval

__all__ = ['Applicative', 'map2', 'combine', 'pure', 'ap',]


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

    def ap(self, fa):
        return self.map2(fn_eval, fa)


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
        
    fb = fa_to_b.ap(fa)
    for fx in fs:
        fb = fb.ap(fx)
    return fb
