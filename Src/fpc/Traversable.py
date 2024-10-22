#
# trait Traversable (t : Type -> Type) where
#     traverse : Applicative f => (a -> f b) -> t a -> f (t b)
#
from __future__ import annotations

from typing      import Callable

from Functor     import Functor
from Applicative import Applicative

__all__ = ['Traversable', 'traverse']


class Traversable(Functor):
    def traverse(self, f: type[Applicative], g: Callable) -> Applicative:   # Hard to type properly in Python
        ...

#
# Traversal over a traversable functor using an effectful function.
# A traversable functor t a can be (conceptually) decomposed into
# a shape t Unit and a List a. This applies the function to each
# value in the list putting the results in the same shape. The entire
# result is in the effectful context.

# traverse : (Applicative f, Traversable t) => (a -> f b) -> t a -> f (t b)
#
# Note that we pass the applicative *class* as a first argument because Python
# cannot infer it from g. We only use -- at most -- the `pure` class method.
# 
def traverse(f: type[Applicative], g: Callable, t: Traversable) -> Applicative:
    """

    """
    return t.traverse(f, g)
