#
# trait Bicovariant (p : Type -> Type -> Type) where
#     cobimap : (b -> a) -> (d -> c) -> p a c -> p b d
#     cobimap f g = cofirst f . cosecond g
#
#     cofirst : (b -> a) -> p a c -> p b c
#     cofirst f = cobimap f identity
#
#     cosecond : (d -> c) -> p a c -> p a d
#     cosecond g : cobimap identity g
#

from __future__      import annotations

from collections.abc import Callable

from .functions      import identity

__all__ = ['Bicovariant', 'cobimap', 'cofirst', 'cosecond']


class Bicovariant[A, C]:
    # Subclasses MUST override at least ONE of these methods
    def cobimap[B, D](self, f: Callable[[B], A], g: Callable[[C], D]) -> Bicovariant[B, D]:
        x = self.cosecond(g)
        return x.cofirst(f)

    def cofirst[B](self, f: Callable[[B], A]) -> Bicovariant[B, C]:
        return self.cobimap(f, identity)

    def cosecond[D](self, g: Callable[[C], D]) -> Bicovariant[A, D]:
        return self.cobimap(identity, g)

def cobimap[A, B, C, D](f: Callable[[B], A], g: Callable[[C], D], x: Bicovariant[A, C]) -> Bicovariant[B, D]:
    return x.cobimap(f, g)

def cofirst[A, B, C](f: Callable[[B], A], x: Bicovariant[A, C]) -> Bicovariant[B, C]:
    return x.cofirst(f)

def cosecond[A, C, D](g: Callable[[C], D], x: Bicovariant[A, C]) -> Bicovariant[A, D]:
    return x.cosecond(g)
