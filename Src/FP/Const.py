#
#
# The Const a Functor
#
# newtype Const a b = Const { runConst : a }
#
# Const a is a functor that ignores its "element type" b.
# If a is a Monoid, then Const a is an Applicative,
# but it is not a Monad.
#
# Because of the Python type system is exogeneous, we need to define
# a separate local class for every value of a. We also accept a
# monoid to be used for the applicative instances. If no monoid is
# supplied, we use a trivial monoid by default. It would probably be
# better to return a const that is not an applicative in that case.
# 
#
from __future__   import annotations

from typing       import Callable, Optional, cast

from .Applicative import Applicative
from .Functor     import Functor
from .Monoids     import Monoid
from .Traversable import Traversable

__all__ = ['Const', 'runConst', 'makeConst']


def Const(x, monoid: Optional[Monoid] = None):
    """Constructs a Const a b functor with specified value and optional Monoid.

    Const a is a functor that ignores its "element type" b.

        newtype Const a b = Const { runConst : a }

    If a is a Monoid, then Const a is an Applicative, otherwise is
    is plain Functor. If the `monoid` argument is supplied, it
    should be a Monoid, and the returned functor will have an
    Applicative instance.

    """
    if monoid is not None:
        # We need the constraint that type A is a monoid, and this
        # monoid should be uniquely determined by A. However, that
        # is not enforceable, so some care is needed to ensure that
        # combined Const's have the same monoid.

        class ConstM[A, B](Applicative, Traversable):
            _monoid = monoid
            
            def __init__(self):
                self._value = x
         
            def __str__(self):
                return f'Const({self._value})'

            def __repr__(self):
                return f'Const({self._value}, {self._monoid.label})'

            @classmethod
            def run(cls, fab: ConstM[A, B]) -> A:
                return fab._value
         
            @property
            def monoid_of(self):
                return self._monoid

            def map[C](self, _g: Callable[[B], C]) -> ConstM[A, C]:
                return cast(ConstM[A, C], self)
         
            @classmethod
            def pure(cls, _x: B) -> ConstM[A, B]:
                return Const(cls._monoid.munit, monoid=cls._monoid) 
         
            def map2[C, D](self, _g: Callable[[B, C], D], fc: ConstM[A, C]) -> ConstM[A, D]:
                return Const(self._monoid.mcombine(self._value, fc._value), self._monoid)

            def traverse(self, f: type[Applicative], _g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
                return f.pure(self)

        return ConstM()

    class Const_[A, B](Traversable):
        _monoid = None
        
        def __init__(self):
            self._value = x
     
        def __str__(self):
            return f'Const({self._value})'

        def __repr__(self):
            return f'Const({self._value})'

        @classmethod
        def run(cls, fab: Const_[A, B]) -> A:
            return fab._value
     
        @property
        def monoid(self):
            return None

        def map[C](self, _g: Callable[[B], C]) -> Const_[A, C]:
            return cast(Const_[A, C], self)

        def traverse(self, f: type[Applicative], _g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
            return f.pure(self)
 
    return Const_()

def runConst(x):
    "An accessible version of Const.run that works with all incarnations of Const[A, B]."
    return x._value

def makeConst(m: Monoid):
    "A factory that returns function the function x -> Const(x, monoid=m)."
    return lambda x: Const(x, m)
