# trait Applicative f => Alternative (f : Type -> Type) where
#     empty : f a
#     alt   : f a -> f a -> f a

from __future__   import annotations

from abc          import abstractmethod
from typing       import Protocol

from .Applicative import Applicative

__all__ = ['Alternative', 'alt']


#
# Applicative as a mixin
#

class Alternative[A](Applicative, Protocol):
    @property
    def empty(self) -> Alternative[A]:
        raise NotImplementedError

    @abstractmethod
    def alt(self, fb: Alternative[A]) -> Alternative[A]:
        ...

def alt[A](fa: Alternative[A], fb: Alternative[A]) -> Alternative[A]:
    return fa.alt(fb)
