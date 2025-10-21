#
# A Temporary gathering of interesting combinators and optics and methods
#

from __future__    import annotations

from ..Bicofunctor import bicomap_
from ..Either      import Left, Right
from ..Maybe       import maybe, Some
from ..functions   import compose

from .Choice       import into_right
from .Optic        import Optic, OpticIs
from .Review       import preview

from .generics     import rphantom, visit_

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
