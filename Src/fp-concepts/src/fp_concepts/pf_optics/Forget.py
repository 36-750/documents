#
# Forget is a profunctor whose second argument is a phantom type (ignored)
#
# newtype Forget r a b = Forget { runForget :: a -> r }
#
# This is isomorphic to Star (Const r) but arises enough that it is
# worth having a name for it.

from __future__    import annotations

from typing        import Callable

from ..Bicovariant import Bicovariant
from .Cartesian    import Cartesian
from ..Profunctor  import Profunctor
from ..functions   import compose, fst, identity, snd

__all__ = ['Forget', 'view']


class Forget[R, A](Cartesian):
    """A profunctor representing a mapping to a fixed type.

    The second type argument is a phantom type (i.e., ignored).
   
    newtype Forget r a b = Forget { runForget :: a -> r }
   
    This is isomorphic to Star (Const r) but arises enough that it is
    worth having a name for it.

    We extract the enclosed function with Forget.run.

    """
    def __init__(self, r_to_a: Callable[[A], R]):
        self._r_to_a = r_to_a

    @classmethod
    def run(cls, fg):
        return fg._r_to_a

    def dimap(self, f, _):
        return Forget(compose(self._r_to_a, f))

    def into_first(self):
        return Forget(compose(self._r_to_a, fst))
    
    def into_second(self):
        return Forget(compose(self._r_to_a, snd))

    def cobimap(self, f: Callable[[B], A], _g: Callable) -> Forget[R, B]:
        return Forget(compose(self._r_to_a, f))



idF = Forget(identity)    

def view(optic):
    return Forget.run(optic(idF))
    
def views(optic, f=identity):
    return Forget.run(optic(Forget(f)))
