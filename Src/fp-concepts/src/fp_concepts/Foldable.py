#
# trait Foldable (f : Type -> Type) where
#     foldM : Monoid m => (a -> m) -> f a -> m
#     fold  : (a -> b -> a) -> a -> f b -> a
#
# trait IndexedFoldable (f : Type -> Type) where
#     ifoldM : Monoid m => (i -> a -> m) -> f a -> m
#     ifold  : (i -> a -> b -> a) -> a -> f b -> a
#
# ruff: noqa: N802
#

from __future__      import annotations

from abc             import abstractmethod
from collections.abc import Callable
from typing          import Protocol

from .Monoids        import Monoid


__all__ = ['Foldable', 'IndexedFoldable', 'foldM', 'fold', 'ifoldM', 'ifold',]


class Foldable[A](Protocol):
    @abstractmethod
    def foldM[M](self, f: Callable[[A], M], monoid: Monoid) -> M:
        ...

    @abstractmethod
    def fold[B](self, f: Callable[[B, A], B], initial: B) -> B:
        ...


class IndexedFoldable[I, A](Protocol):
    @abstractmethod
    def ifoldM[M](self, f: Callable[[I, A], M], monoid: Monoid) -> M:
        ...

    @abstractmethod
    def ifold[B](self, f: Callable[[I, B, A], B], initial: B) -> B:
        ...


#
# Generic Functions
#

def foldM[A, M](f: Callable[[A], M], xs: Foldable[A], monoid: Monoid) -> M:
    """Fold over a structure, converting each component to a monoid and combining.

    This will typically operate over Functors, but it is fine to define these
    methods for any object (e.g., any Iterable).

    Parameters

    + f : a -> m -- function that maps elements of the structure to a monoid
    + xs  -- The structure to be folded.
    + monoid -- a Monoid object specifying how to combine mapped elements.

    Returns the final monoidal result, which is the unit of the monoid if the
    structure xs is empty.

    """
    return xs.foldM(f, monoid)

def fold[A, B](f: Callable[[B, A], B], initial: B, xs: Foldable[A]) -> B:
    """Fold over a structure accumulating a result from an initial value.

    This is a general form of functools.reduce. It is designed to work
    over a suitable Functor but the fold method can be defined for any
    type of object.

    Parameters:

    + f : (b -> a -> b) -- A function that updates an accumulator (of type b)
        given an element of the structure (of type a)
    + initial : b  -- The initial accumulator. This is returned when the
        structure is empty
    + xs - The structure to be folded over.

    Returns the final accumulator value.

    """
    return xs.fold(f, initial)

def ifoldM[I, A, M](f: Callable[[I, A], M], xs: Foldable[A], monoid: Monoid) -> M:
    """Fold over an indexed structure, converting each component to a monoid and combining.

    The indexes are intrinsic to the structure and are typically obtained by
    an IndexedFunctor instance, though this can be defined for more general objects.

    Parameters

    + f : i -> a -> m -- function that maps indices and elements of the structure
        to a monoid

    + xs  -- The structure to be folded. This will typically be a Functor, but
        can be defined for other objects as well (e.g., any Iterable).

    + monoid -- a Monoid object specifying how to combine mapped elements.

    Returns the final monoidal result, which is the unit of the monoid if the
    structure xs is empty.

    """
    return xs.ifoldM(f, monoid)


def ifold[I, A, B](f: Callable[[I, B, A], B], xs: Foldable[A], initial: B) -> B:
    """Fold over a structure accumulating a result from an initial value.

    This is a general form of functools.reduce. It is designed to work
    over a suitable Functor but the fold method can be defined for any
    type of object.

    Parameters:

    + f : (b -> a -> b) -- A function that updates an accumulator (of type b)
        given an element of the structure (of type a)
    + initial : b  -- The initial accumulator. This is returned when the
        structure is empty
    + xs - The structure to be folded over.

    Returns the final accumulator value.

    """
    return xs.ifold(f, initial)


