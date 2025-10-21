#
# Wrappers classes and associated utilities
#
# This is in a separate module to avoid circularity.
# Some of this may be provisional/experimental.
#

from __future__ import annotations

from .Applicative import Applicative
from .functions   import Function

__all__ = [
    'EffectfulFunction',
    'get_effect',
    'TypedFunction',  # Provisional
]

class EffectfulFunction(Function):
    "Class representing a function that produces an Applicative Functor."

    def __init__(self, f, ap: type[Applicative]):
        self._applicative = ap
        super().__init__(f)

    @property
    def effect(self):
        return self._applicative

def get_effect(f) -> type | None:
    "If f is an effectful function returns its Applicative, else None"
    if hasattr(f, 'effect'):
        return f.effect
    return None

# ATTN: Provisional, might be useful with using()
# This is a potential alternative to having a use= argument
# or it can supplement that.
class TypedFunction(Function):
    "Class representing a function with associated types in its signature."

    def __init__(self, f, **types):
        self._types = dict(types)
        super().__init__(f)

    def has(self, associated_type):
        return self._types.get(associated_type, None)
