# trait Applicative f => Alternative (f : Type -> Type) where
#     empty : f a
#     alt   : f a -> f a -> f a

from __future__   import annotations

from abc          import abstractmethod
from typing       import Protocol

from .Applicative import Applicative

__all__ = ['Alternative', 'alt', 'guard']


#
# Alternative as a mixin
#

# ATTN: Should this have a type parameter or be handled like Applicative?

class Alternative[A](Applicative, Protocol):
    @classmethod
    def empty(cls) -> Alternative[A]:
        raise NotImplementedError

    @abstractmethod
    def alt(self, fb: Alternative[A]) -> Alternative[A]:
        ...

def alt[A](fa: Alternative[A], fb: Alternative[A]) -> Alternative[A]:
    return fa.alt(fb)

def guard(f: type[Alternative], condition: bool) -> Alternative[tuple[()]]:  # ATTN: type Unit = tuple[()]
    return f.unit() if condition else f.empty()

# ATTN: Include some and many?  Can we implement them?
