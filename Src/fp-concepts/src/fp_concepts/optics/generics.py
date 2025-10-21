#
# Generic Functions for Instances
#
# There might be a better place for these
#

from __future__    import annotations

from ..Bicofunctor import cosecond
from ..Either      import Left, Right, either
from ..Identity    import Identity
from ..Pair        import Pair
from ..Profunctor  import dilift, rmap
from ..functions   import compose, const, identity

from .Choice       import into_left
from .Strong       import into_first

#
# Generic Functions for instances
#

def absurd(*args, **kwargs):
    raise TypeError('This profunctor is read only; rmap component is a phantom.')

# rphantom :: (Profunctor p, Bicontravariant p) => p c a -> p c b
def rphantom(p):
    return rmap(absurd, cosecond(absurd, p))

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
