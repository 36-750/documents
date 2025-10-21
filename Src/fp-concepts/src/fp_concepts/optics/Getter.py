#
# A Getter s a is an optic of type
#
#   type Getter s a = (Profunctor p, Bicofunctor p, Cochoice p) => p a a -> p s s
#
# Such a p, being covariant and contravariant in its second type argument,
# must have a phantom second type argument. Being a contravariant functor
# and Cochoice, implies that p a b must be isomorphic to a constant
# function on a, e.g., a -> ().
#
# Thus, Getter s a is isomorphic to
#
#   type Getter s a = Getter { runGetter :: s -> a }
#
# The function getter below lifts a functio s -> a to such an object.
#

from __future__    import annotations

from typing        import Callable, cast

from ..Bicofunctor import Bicofunctor
from ..Either      import Left, Right
from ..Profunctor  import Profunctor, dilift  # , lmap
from ..functions   import Function, identity

from .Cochoice     import Cochoice
from .profunctors  import Forget

__all__ = ['view', 'view_with', 'getter']


def absurd(*args, **kwargs):
    raise TypeError('Getter is read only; rmap component is a phantom.')

# ATTN: Not sure this is really needed
# class A_Getter[T, U](Cochoice, Bicofunctor):
#     """Constraint wrapper for domain and codomain of a Getter.
#
#     This is primarily used for typing. See `getter` below.
#
#     """
#     def __init__(self, p: Profunctor[T, U]):
#         self._p = p
#
#     def dimap[V, W](self, f: Callable[[V], T], _g: Callable[[U], W]) -> A_Getter[V, W]:
#         return A_Getter[V, W](self._p.dimap(f, cast(Callable[[U], W], absurd)))
#
#     def bicomap[V, W](self, f: Callable[[V], T], _g: Callable[[W], U]) -> A_Getter[V, W]:  # type: ignore
#         return A_Getter[V, W](self._p.dimap(f, cast(Callable[[U], W], absurd)))
#
#     def unleft(self):
#         return A_Getter(self._p.dimap(Left, absurd))
#
#     def unright(self):
#         return A_Getter(self._p.dimap(Right, absurd))
#
# type Getter[S, A] = Callable[[A_Getter[A, A]], A_Getter[S, S]]


#
# Combinators
#

idF: Forget = Forget(identity)

def view(optic):
    """Returns the value pointed to by a Getter.

    """
    return Forget.run(optic(idF))

def view_with(optic, f=identity):
    """Returns the value pointed to by a Getter transformed by a function.

    """
    return Forget.run(optic(Forget(f)))

def getter[S, A](f: Callable[[S], A]):
    """Builds and returns a Getter from a function from structure to substructure.

    """
    # Hard to make work and fragile
    # def do_get(pf):
    #     class A_Getter(pf.__class__):
    #         "Constraint wrapper for domain and codomain of a Getter."
    #         def __new__(cls, *contents):
    #             return super().__new__(cls, *contents)
    #
    #         def dimap[V, W](self, f: Callable[[V], S], _g: Callable[[A], W]) -> A_Getter[V, W]:
    #             return A_Getter[V, W](pf.dimap(f, cast(Callable[[A], W], absurd)))
    #
    #         def bicomap[V, W](self, f: Callable[[V], S], _g: Callable[[W], A]) -> A_Getter[V, W]:  # type: ignore
    #             return A_Getter[V, W](pf.dimap(f, cast(Callable[[A], W], absurd)))
    #
    #         def unleft(self):
    #             return A_Getter(pf.dimap(Left, absurd))
    #
    #         def unright(self):
    #             return A_Getter(pf.dimap(Right, absurd))
    #
    #     return A_Getter(pf)
    #
    # return Function(do_get)

    # Old and simple way
    return dilift(Function(f), cast(Callable[[A], S], absurd))
