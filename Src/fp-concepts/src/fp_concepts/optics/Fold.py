""" Fold - optics that extract elements from a container

A Fold s a can extract elements of type a from a container of type s.
It cannot set or update those elements; see Traversal for that.

"""

from __future__    import annotations

from operator      import truediv
from typing        import Callable

from ..Bicofunctor import cofirst
from ..List        import List
from ..Monoids     import Monoid, Count, Endo, Sum, Product, mtuple
from ..Pair        import Pair
from ..Traversable import traverse_
from ..functions   import Function, compose, curry, fn_eval, identity, partial, uncurry
from ..utils       import Collect

from .profunctors  import Forget
from .Optic        import Optic, OpticIs

from .generics     import rphantom, wander_

__all__ = [
    'Fold',
    'fold_vl',
    'foldedA',
    'folded',
    'folding',
    'fold_map_of',
    'fold_of',
    'collect',
    'sum_of',
    'count_of',
    'product_of',
    'mean_of',
    'left_fold_of',
    'right_fold_of',
]

class Fold(Optic):  # ATTN:Placeholder
    def __init__(self, f):
        super().__init__(f, OpticIs.FOLD)

# fold_vl : Applicative f => (a -> f b) -> (s -> f t) -> Optic s t a b
def fold_vl(f):
    return Fold(compose(rphantom, wander_(f), rphantom))

# folded : Foldable f => Fold (f a) a
folded = fold_vl(traverse_)  # ATTN: This should be Foldable_.traverse_, but that raises a difficulty.

def foldedA(effect):
    return fold_vl(lambda g: traverse_(g, effect=effect))

# Create a Fold from a function returning a foldable result.
# folding : Foldable f => (s -> f a) -> Fold s a
def folding(f):
    g = partial(cofirst, f)
    return Fold(compose(g, folded.run))


#
# Folding Actions
#

def fold_map_of(optic, f, monoid: Monoid = Collect):
    p = Forget(f, monoid)
    optic_f = optic.cast_as(OpticIs.FOLD)
    g = Forget.run(optic_f(p))

    return Function(g)

def fold_of(optic, monoid: Monoid = Collect):
    return fold_map_of(optic, identity, monoid)

# Original: toListOf
def collect(optic):
    return fold_map_of(optic, List.pure, Collect)

def sum_of(optic):
    return fold_of(optic, Sum)

def count_of(optic):
    return fold_of(optic, Count)

def product_of(optic):
    return fold_of(optic, Product)

def mean_of(optic):
    init = Pair(0, 1).with_second
    return uncurry(truediv) @ fold_map_of(optic, init, mtuple(Sum, Count))

def right_fold_of[X, R](optic: Optic,  x_r_r: Callable[[X, R], R], init: R):
    reduce = curry(x_r_r)
    return Function(lambda s: fn_eval(s >> fold_map_of(optic, reduce, Endo), init))

def left_fold_of[X, R](optic: Optic,  r_x_r: Callable[[X, R], R], init: R):
    def reduce(x, r_r):
        def act(r):
            return r_r(r_x_r(r, x))
        return act

    return lambda s: (s >> right_fold_of(optic, reduce, identity))(init)
