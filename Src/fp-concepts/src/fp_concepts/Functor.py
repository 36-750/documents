#
# trait Functor f where
#     map : (a -> b) -> f a -> f b
#
#
# ruff: noqa: A001
#

from __future__ import annotations

from abc             import abstractmethod
from collections.abc import Callable, Iterable
from typing          import Protocol

__all__ = ['Functor', 'IndexedFunctor', 'map', 'lift', 'imap', 'pymap',]


#
# We will overwrite (and extend) the built-in map, so
# save a reference to it for use where needed.
# This is exportable for the same reason, although
# map below should be a plug-and-play alternative.
#

pymap = map  # Reference to built-in map


#
# Functor as a mixin
#

class Functor[A](Protocol):
    @abstractmethod
    def map[B](self, g: Callable[[A], B]):
        ...

class IndexedFunctor[I, A](Functor, Protocol):
    @abstractmethod
    def imap[B](self, g: Callable[[I, A], B]):
        ...


#
# Generic Functions for Functor Methods
#

def map[A, B](f: Callable[[A], B], functor: Functor, *delegates: Iterable):
    """Maps a function over a functor, returning a transformed functor.

    If the given `functor` does not have a .map attribute, this delegates
    to the builtin map if `functor` is iterable, else raises a KeyError.

    The `delegates` iterable arguments are only used in the case
    of delegating to builtin-map and raises a TypeError if supplied
    with a Functor instance.

    When importing this, you can call it fmap to avoid overlap with
    builtin Python map.

    """
    if hasattr(functor, 'map'):
        if len(delegates) > 0:
            raise TypeError('map takes only a single functor instance, multiple values given.')
        return functor.map(f)
    elif isinstance(functor, Iterable):
        return pymap(f, functor, *delegates)

    raise KeyError('map requires a Functor instance implementing .map.')

def lift[A, B](f: Callable[[A], B]):
    """Lifts a function to a mapping on functors.

    This is just the partial application map(f, __).

    """
    def lift_f(functor: Functor):
        return functor.map(f)

    return lift_f

def imap[I, A, B](f: Callable[[I, A], B], x: IndexedFunctor):
    """Maps a function over a IndexedFunctor with an initial index argument.

    The index type and initialization is determined by the specific
    IndexedFunctor instance.

    """
    return x.imap(f)
