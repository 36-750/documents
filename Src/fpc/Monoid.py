# Best current version (I think)

from __future__ import annotations

import math

from functools import reduce
from operator  import attrgetter
from typing    import Protocol, runtime_checkable

from functions import identity, const, uncurry, compose

__all__ = ['Semigroup', 'Monoid', 'munit', 'mcombine',
           'Trivial', 'Free',
           'First', 'Last', 'Min', 'Max', 'Sum', 'Product',
           'MonoidalDictM', 'cartesian', 'mtuple',
           ]

#
# Monoids
#
# While we have several choices, including having monoid objects *wrap*
# values, here we use monoid objects as *interpreters* of values.
# This eliminates one level of wrapping/unwrapping as we process the data.
#
# Each monoid has an `munit` property, an `mcombine` method, and a label,
# but we exclude `label` from the protocol. We also include
# a `conforms` method in our implementations for checking valid inputs
# but we do not use it inside mcombine, say, or include it in the protocol.
#

class Semigroup(Protocol):
    def mcombine(self, x, y): ...

@runtime_checkable
class Monoid(Semigroup, Protocol):
    @property
    def munit(self): ...

    @property
    def label(self):
        return self.__class__.__name__.rstrip('M')

    def __str__(self):
        return str(self.label)

    def __repr__(self):
        return f'{self.__class__.__name__}()'

def munit(m):
    "The identity/unit element of a given monoid."
    return m.munit

def mcombine(m, x, y):
    "The combine operation for a given monoid and two monoidal values."
    return m.mcombine(x, y)


#
# Wrappers for Commonly-Used Monoids
#

def Trivial(e):
    class TrivialM(Monoid):
        "A singleton monoid with a single element, which is the identity."
     
        def mcombine(self, _x, _y):
            return e
     
        @property
        def munit(self):
            return e
     
        def conforms(self, x) -> bool:
            "Accepts only a single value"
            return x == e

    return TrivialM()

class ListM(Monoid):
    "A monoid that collects values in lists."

    def mcombine(self, x, y):
        return [*x, *y]

    @property
    def munit(self):
        return []

    def conforms(self, x) -> bool:
        "Accepts List[Any]"
        return isinstance(x, list)

List = ListM()
Free = List

class FirstM(Monoid):
    "A monoid that takes the first non-missing value."

    def mcombine(self, x, y):
        return y if x is None else x

    @property
    def munit(self):
        return None

    def conforms(self, x) -> bool:
        "Any value is ok, including None"
        return True

First = FirstM()

class LastM(Monoid):
    "A monoid that takes the last non-missing value."

    def mcombine(self, x, y):
        return x if y is None else y

    @property
    def munit(self):
        return None

    def conforms(self, x) -> bool:
        "Any value is ok, including None"
        return True

Last = LastM()

class MinM(Monoid):
    "A monoid that takes the numerical minimum."

    def mcombine(self, x, y):
        return min(x, y)

    @property
    def munit(self):
        return math.inf

    def conforms(self, x) -> bool:
        "Checks for primitive numeric value. We would like this to be more general."
        return isinstance(x, int) or isinstance(x, float)

Min = MinM()

class MaxM(Monoid):
    "A monoid that takes the numerical maximum."

    def mcombine(self, x, y):
        return max(x, y)

    @property
    def munit(self):
        return -math.inf

    def conforms(self, x) -> bool:
        "Checks for primitive numeric value. We would like this to be more general."
        return isinstance(x, int) or isinstance(x, float)

Max = MaxM()

class SumM(Monoid):
    "A monoid that sums the numbers it sees."

    def mcombine(self, x, y):
        return x + y

    @property
    def munit(self):
        return 0

    def conforms(self, x) -> bool:
        "Checks for primitive numeric value. We would like this to be more general."
        return isinstance(x, int) or isinstance(x, float)

Sum = SumM()

class ProductM(Monoid):
    "A monoid that multiplies the numbers it sees."

    def mcombine(self, x, y):
        return x * y

    @property
    def munit(self):
        return 1

    def conforms(self, x) -> bool:
        "Checks for primitive numeric value. We would like this to be more general."
        return isinstance(x, int) or isinstance(x, float)

Product = ProductM()

class MonoidalDictM(Monoid):
    "A monoid that merges arbitrary monoidal dictionaries."

    def __init__(self, merge_fn=lambda x, y: y):
        self.merge_fn = merge_fn

    def mcombine(self, x, y):
        return self.merge(x, y)

    @property
    def munit(self):
        return {}

    def conforms(self, x) -> bool:
        "Any dictionary value is ok"
        return isinstance(x, dict)

    @staticmethod
    def map(f, mm):
        return {k: f(v) for k, v in mm.items()}

    def merge(self, x, y):
        return self.merge_with(x, y, self.merge_fn)

    @staticmethod
    def merge_with(mm1, mm2, f):
        merged = {k: mm1.get(k, mm2.get(k)) for k in mm1.keys() ^ mm2.keys()}
        merged.update({k: f(mm1[k], mm2[k]) for k in mm1.keys() & mm2.keys()})
        return merged

    @staticmethod
    def collect(a, b):
        if isinstance(a, list):
            if isinstance(b, list):
                return [*a, *b]
            return [*a, b]
        elif isinstance(b, list):
            return [a, *b]
        return [a, b]

    @staticmethod
    def collect_unique(a, b):
        if isinstance(a, set):
            if isinstance(b, set):
                return a | b
            return {*a, b}
        elif isinstance(b, set):
            return {a, *b}
        return {a, b}

    @staticmethod
    def first(a, b):
        return a

    @staticmethod
    def second(a, b):
        return b

def cartesian(monoids):
    "Returns a Monoid wrapper class for a cartesian product of other monoids."
    monoids = tuple(monoids)
    unit = tuple(map(lambda m: m.munit, monoids))
    product_label = f'cartesian({", ".join(map(lambda x: x.label, monoids))})'

    class MTuple(Monoid):
        "A cartesian product of monoids"

        def mcombine(self, x, y):
            return tuple(mcombine(monoids[k], x[k], y[k]) for k in range(len(x)))

        @property
        def munit(self):
            return unit

        @property
        def label(self):
            return product_label

        def conforms(self, x) -> bool:
            "A tuple of the same length and conforming to monoids in template is required"
            return isinstance(x, tuple) and len(x) == len(monoids) and all(m.conforms(x) for m in monoids)

    return MTuple()

def mtuple(*monoids):
    "Like cartesian, but the component monoids are given as separate arguments."
    return cartesian(monoids)

# ...more monoids: JoinString, Concat, Collect, CollectUnique, CountUnique, Duplicated, Frequencies, Bag
