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
# ruff: noqa: N801, N802
#

from __future__   import annotations

from collections.abc import Callable
from typing          import cast

from .Applicative import Applicative
from .Monoids     import Monoid
from .Traversable import Traversable

__all__ = ['Const', 'runConst', 'makeConst', 'typeConst']

_const_registry: dict[Monoid, type[Applicative]] = {}


def Const(x, monoid: Monoid | None = None):
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

        if monoid not in _const_registry:
            class ConstM[A, B](Applicative, Traversable):
                _monoid: Monoid = monoid   # type: ignore

                def __init__(self):
                    self._value = monoid.munit  # x

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

            _const_registry[monoid] = ConstM

        # ATTN: Question -- Is it better to just modify an instance or inheriting from a value-specific class.
        #       Use this for now because the types are effectively shared for a common monoid, though formally
        #       not really.  The alternative (see below) makes the types distinct for different types of values
        #       but also for the same type of value. It is unclear whether this overlap causes problems,
        #       but it seems at the moment unlikely. Use varied instances for now.
        #
        # The inheritance alternative looks like:
        #
        # cls: type = _const_registry[monoid]
        #
        # class ConstMx[A, B](cls):
        #     def __init__(self):
        #         super().__init__()
        #         self._value = x
        #
        # return ConstMx()

        if not monoid.conforms(x):
            raise ValueError(f'Value {x} inconsistent with Monoid {str(monoid)} in Const.')

        # We think of Const() as being the real constructor so mutating the value here is morally OK
        instance = _const_registry[monoid]()
        instance._value = x    # type: ignore
        return instance

        # class ConstM[A, B](Applicative, Traversable):
        #     _monoid: Monoid = monoid   # type: ignore
        #
        #     def __init__(self):
        #         self._value = x
        #
        #     def __str__(self):
        #         return f'Const({self._value})'
        #
        #     def __repr__(self):
        #         return f'Const({self._value}, {self._monoid.label})'
        #
        #     @classmethod
        #     def run(cls, fab: ConstM[A, B]) -> A:
        #         return fab._value
        #
        #     @property
        #     def monoid_of(self):
        #         return self._monoid
        #
        #     def map[C](self, _g: Callable[[B], C]) -> ConstM[A, C]:
        #         return cast(ConstM[A, C], self)
        #
        #     @classmethod
        #     def pure(cls, _x: B) -> ConstM[A, B]:
        #         return Const(cls._monoid.munit, monoid=cls._monoid)
        #
        #     def map2[C, D](self, _g: Callable[[B, C], D], fc: ConstM[A, C]) -> ConstM[A, D]:
        #         return Const(self._monoid.mcombine(self._value, fc._value), self._monoid)
        #
        #     def traverse(self, f: type[Applicative], _g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        #         return f.pure(self)
        #
        # return ConstM()

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

        def map[C](self, _g: Callable[[B], C]) -> Const_[A, C]:   # type: ignore
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

def typeConst(m: Monoid):
    """Returns the base Const type associated with a given Monoid.

    This type should *not* be used in lieu of the Const() constructor.
    Values of the base type are initialized with the monoid identity
    and the base constructor does not take a value.

    The key use case for this function is for registering effects
    and accessing the pure function for the Const applicative.
    These are the same for Const(x, m) for all conforming x.

    """
    if m in _const_registry:
        return _const_registry[m]
    return Const(m.munit, m).__class__
