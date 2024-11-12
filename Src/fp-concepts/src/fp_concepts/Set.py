#
# The Set as a Functor
#
# In theory, this requires contents that are comparable
# for equality, but in this context, we can manage using
# Python's built-in is-equality.

from __future__ import annotations

from collections.abc import Callable, Iterable

from .Functor        import Functor, pymap
from .Monoids        import UnionM

__all__ = ['Set']


#
# Set a as a Functor
#
# These are the prototypical functors in category theory, but
# the constraint on comparability end up being an obstacle.
# But not here...
#

class SetMonoidDescriptor:  # Enables class data of type Set
    def __get__(self, obj, objtype=None):
        return UnionM(objtype)

class Set[A](set, Functor):
    monoid = SetMonoidDescriptor()

    def __new__(cls, *args, **kwds):
        return super().__new__(cls, *args, **kwds)

    # # Set's repr puts Set({1, 2, 3})
    # def __repr__(self):
    #     return set(self).__repr__()

    @classmethod
    def of(cls, *xs: Iterable[A]):
        return cls(xs)

    def map[A, B](self, g: Callable[[A], B]):
        return self.__class__(pymap(g, self))
