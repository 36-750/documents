#
# trait Bicofunctor (p : Type -> Type -> Type) where
#     bicomap : (b -> a) -> (d -> c) -> p a c -> p b d
#     bicomap f g = cofirst f . cosecond g
#
#     cofirst : (b -> a) -> p a c -> p b c
#     cofirst f = bicomap f identity
#
#     cosecond : (d -> c) -> p a c -> p a d
#     cosecond g : bicomap identity g
#

from __future__      import annotations

from collections.abc import Callable
from typing          import Protocol

from .functions      import identity

__all__ = ['Bicofunctor', 'bicomap', 'cofirst', 'cosecond']


class Bicofunctor[A, C](Protocol):
    # Subclasses MUST override at least ONE of these methods
    def bicomap[B, D](self, f: Callable[[B], A], g: Callable[[C], D]) -> Bicofunctor[B, D]:
        x = self.cosecond(g)
        return x.cofirst(f)

    def cofirst[B](self, f: Callable[[B], A]) -> Bicofunctor[B, C]:
        return self.bicomap(f, identity)

    def cosecond[D](self, g: Callable[[C], D]) -> Bicofunctor[A, D]:
        return self.bicomap(identity, g)

def bicomap[A, B, C, D](f: Callable[[B], A], g: Callable[[C], D], x: Bicofunctor[A, C]) -> Bicofunctor[B, D]:
    return x.bicomap(f, g)

def bicomap_[A, B, C, D](f: Callable[[B], A], g: Callable[[C], D]) -> Callable[[Bicofunctor[A, C]], Bicofunctor[B, D]]:
    def do_bicomap_(x: Bicofunctor[A, C]) -> Bicofunctor[B, D]:
        return x.bicomap(f, g)

    return do_bicomap_

def cofirst[A, B, C](f: Callable[[B], A], x: Bicofunctor[A, C]) -> Bicofunctor[B, C]:
    return x.cofirst(f)

def cosecond[A, C, D](g: Callable[[C], D], x: Bicofunctor[A, C]) -> Bicofunctor[A, D]:
    return x.cosecond(g)
