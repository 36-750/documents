#
# trait Functor f where
#     map : (a -> b) -> f a -> f b
#

from __future__ import annotations

from abc             import ABC
from collections.abc import Iterable
from functools       import partial, wraps
from typing          import Callable, Protocol

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

class Functor(Protocol):
    def map[A, B](self, g: Callable[[A], B]):
        ...

class IndexedFunctor[I](Functor, Protocol):
    def imap[A, B](self, g: Callable[[I, A], B]):
        ...


#
# Generic Functions for Functor Methods
#

def map[A, B](f: Callable[[A], B], F: Functor, *delegates: Iterable):
    """Maps a function over a functor, returning a transformed functor.

    If the given `F` does not have a .map attribute, this delegates
    to the builtin map if `F` is iterable, else raises a KeyError.

    The `delegates` iterable arguments are only used in the case
    of delegating to builtin-map and raises a TypeError if supplied
    with a Functor instance.

    When importing this, you can call it fmap to avoid overlap with
    builtin Python map.

    """
    if hasattr(F, 'map'):
        if len(delegates) > 0:
            raise TypeError('map takes only a single functor instance, multiple values given.')
        return F.map(f)
    elif isinstance(F, Iterable):
        return pymap(f, F, *delegates)

    raise KeyError('map requires a Functor instance implementing .map.')

def lift[A, B](f: Callable[[A], B]):
    """Lifts a function to a mapping on functors.

    This is just the partial application map(f, __).

    """
    def lift_f(F: Functor):
        return F.map(f)
 
    return lift_f

def imap[I, A, B](f: Callable[[I, A], B], x: IndexedFunctor):
    """Maps a function over a IndexedFunctor with an initial index argument.

    The index type and initialization is determined by the specific
    IndexedFunctor instance.

    """
    return x.imap(f)
