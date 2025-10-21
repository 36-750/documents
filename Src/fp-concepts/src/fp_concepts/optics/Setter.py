"""Setters ATTN

"""

from __future__   import annotations

from .Optic       import Optic, OpticIs
from ..functions  import Function, const

__all__ = ['over', 'put']


def over(opt: Optic, a_to_b):
    "ATTN"
    setter = opt.cast_as(OpticIs.SETTER)
    return setter(Function(a_to_b))

def put(opt: Optic, val):
    "ATTN"
    return over(opt, const(val))
