#
# Various utilities and useful pieces for the implementation
#

from __future__ import annotations

from Monoid import Monoid
from List   import List
from Maybe  import Maybe, maybe

class CollectM(Monoid):
    "A monoid that collects values in Lists, upcasting non-lists with pure."

    def mcombine(self, x, y):
        mx = x if isinstance(x, List) else List.of(x)
        my = y if isinstance(y, List) else List.of(y)
        return List([*mx, *my])

    @property
    def munit(self):
        return List([])

    def conforms(self, x) -> bool:
        "Accepts Any"
        return True

Collect = CollectM()

# class CollectMaybeM(Monoid):
#     "ATTN"
#  
#     def collect(x):
#         return maybe(List(), List.of, x)
#  
#     def mcombine(self, x, y):
#         
