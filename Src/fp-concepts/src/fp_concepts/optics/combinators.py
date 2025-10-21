#
# A Temporary gathering of interesting combinators and optics and methods
#

from __future__    import annotations

from operator      import truediv
from typing        import Callable

from ..Bicofunctor import bicomap_, cofirst, cosecond
from ..Either      import Left, Right, either
from ..Identity    import Identity
from ..Maybe       import maybe, Some
from ..Monoids     import Monoid, Count, Endo, Sum, Product, mtuple
from ..Pair        import Pair
from ..Profunctor  import dilift, rmap
from ..Traversable import traverse_
from ..functions   import Function, compose, const, curry, fn_eval, identity, partial, uncurry
from ..utils       import Collect

from .Choice       import into_left, into_right
from .profunctors  import Forget
from .Optic        import Optic, OpticIs
from .Review       import preview
from .Strong       import into_first

#
# Generic Functions for instances
#

def absurd(*args, **kwargs):
    raise TypeError('This profunctor is read only; rmap component is a phantom.')

# rphantom :: (Profunctor p, Bicontravariant p) => p c a -> p c b
def rphantom(p):
    return rmap(absurd, cosecond(absurd, p))

# fold_vl : Applicative f => (a -> f b) -> (s -> f t) -> Optic s t a b
def fold_vl(f):
    return Optic(compose(rphantom, wander_(f), rphantom), OpticIs.FOLD)

# wander : Applicative f => (a -> f b) -> (s -> f t)
def wander(f, p):
    if hasattr(p, 'wander'):
        return p.wander(f)
    raise TypeError('Profunctor does not have wander method')

def wander_(f):
    def wander_c(p):
        return wander(f, p)

    return wander_c

# visit
#   : (forall f. Functor f => (forall r. r -> f r) -> (a -> f b) -> s -> f t)
#   -> p a b
#   -> p s t
def visit(f, p):
    if hasattr(p, 'visit'):
        return p.visit(f)

    def m_tch(s):
        return f(Right, Left, s)

    def build(s):
        return lambda b: Identity.run(f(Identity, const(Identity(b)), s))

    return compose(
        dilift( lambda s: Pair(m_tch(s), s),
                lambda ebt_s: either(build(ebt_s[1]), identity, ebt_s[0]) ),
        into_first,
        into_left
    )

def visit_(f):
    def visit_c(p):
        return visit(f, p)

    return visit_c


#
# Combinators
#

# afold :: (forall f. Functor f => (forall r. r -> f r) -> (a -> f u) -> s -> f v)
#       -> AffineFold s a
# Creates an AffineFold from functions like pure and traverse

def afold(f):
    return Optic(compose(rphantom, visit_(f), rphantom), OpticIs.AFFINE_FOLD)

# Create an AffineFold from a partial function
# afolding :: (s -> Maybe a) -> AffineFold s a
# afolding f = Optic (contrabimap (\s -> maybe (Left s) Right (f s)) Left . right')
def afolding(f):
    def af(s):
        return maybe(Left(s), Right, f(s))
    return Optic(compose(bicomap_(af, Left), into_right), OpticIs.AFFINE_FOLD)

folded = fold_vl(traverse_)
foldedA = lambda effect: fold_vl(lambda g: traverse_(g, effect=effect))

# Create a Fold from a function returning a foldable result.
# folding : Foldable => (s -> f a) -> Fold s a
def folding(f):
    g = partial(cofirst, f)
    return Optic(compose(g, folded), OpticIs.FOLD)

# filtered : (a -> bool) -> AffineFold a a
def filtered(predicate):
    def fd(point, f, a):
        if predicate(a):
            return f(a)
        return point(a)
    return afold(fd)

# Try the first AffineFold; if it fails, try the second.
def a_or(a, b):
    def alt(s):
        return maybe(preview(b)(s), Some, preview(a)(s))
    return afolding(alt)

#
# Folding Actions
#

def foldMapOf(optic, f, monoid: Monoid = Collect):
    p = Forget(f, monoid)
    optic_f = optic.cast_as(OpticIs.FOLD)
    g = Forget.run(optic_f(p))

    return Function(g)

def foldOf(optic, monoid: Monoid = Collect):
    return foldMapOf(optic, identity, monoid)

def sumOf(optic):
    return foldOf(optic, Sum)

def countOf(optic):
    return foldOf(optic, Count)

def productOf(optic):
    return foldOf(optic, Product)

def meanOf(optic):
    init = Pair(0, 1).with_second
    return uncurry(truediv) @ foldMapOf(optic, init, mtuple(Sum, Count))

def right_foldOf[X, R](optic: Optic,  x_r_r: Callable[[X, R], R], init: R):
    reduce = curry(x_r_r)
    return Function(lambda s: fn_eval(s >> foldMapOf(optic, reduce, Endo), init))

def left_foldOf[X, R](optic: Optic,  r_x_r: Callable[[X, R], R], init: R):
    def reduce(x, r_r):
        def act(r):
            return r_r(r_x_r(r, x))
        return act

    return lambda s: (s >> right_foldOf(optic, reduce, identity))(init)
