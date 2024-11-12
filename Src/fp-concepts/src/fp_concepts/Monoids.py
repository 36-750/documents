#
# Monoid class along with several commonly used Monoids.
#
# class Monoid m where:
#     munit : m
#     mcombine : m -> m -> m
#
# Here, the class instances are just holders of the
# two constituent functions. Generic functions are
# also provided; these take the monoid as the first
# argument.
#
# Semigroup is a superclass with the same mcombine
# but no unit.
#
# Both are set to protocols that are checkable at
# runtime, so explicit inheritence need not be used.
#
# ruff: noqa: N802

from __future__ import annotations

import math

from typing     import Protocol, runtime_checkable

__all__ = [
    # Classes and Generic Functions
    'Semigroup', 'Monoid', 'munit', 'mcombine', 'make_monoid',

    # Concrete Monoids
    'Trivial', 'Free',
    'First', 'Last', 'Min', 'Max', 'Sum', 'Product',
    'Conjunction', 'Disjunction',
    'Union', 'UnionM', 'MonoidalDictM',

    # Monoid combinators
    'cartesian', 'mtuple',
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

def make_monoid(unit, combine, name='Custom'):
    "Creates a monoid object from a unit and associative operation."
    class CustomM(Monoid):
        @property
        def munit(self):
            return unit

        @property
        def label(self):
            return name

        def mcombine(self, x, y):
            return combine(x, y)

    return CustomM()


#
# Commonly-Used Monoids
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

# Free does not use our List class to avoid circularity,
# but see utils.py for a List-ified version

class FreeM(Monoid):
    "The free monoid: a monoid that collects values in lists."

    def mcombine(self, x, y):
        return [*x, *y]

    @property
    def munit(self):
        return []

    def conforms(self, x) -> bool:
        "Accepts List[Any]"
        return isinstance(x, list)

Free = FreeM()

class FirstM(Monoid):
    "A monoid that takes the first non-missing value."

    def mcombine(self, x, y):
        return y if x is None else x

    @property
    def munit(self):
        return None

    def conforms(self, _x) -> bool:
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

    def conforms(self, _x) -> bool:
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

class ConjunctionM(Monoid):
    "Boolean with `and` as the monoid operator."

    @property
    def munit(self):
        return True

    def mcombine(self, a, b):
        return a and b

Conjunction = ConjunctionM()

class DisjunctionM(Monoid):
    "Boolean with `or` as the monoid operator."

    @property
    def munit(self):
        return False

    def mcombine(self, a, b):
        return a or b

Disjunction = DisjunctionM()

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

class UnionM(Monoid):
    def __init__(self, base_cls=set):
        self._base = base_cls

    @property
    def munit(self):
        return self._base()

    def mcombine(self, a, b):
        return self._base(a.union(b))

Union = UnionM()

class MonoidalDictM(Monoid):
    "A monoid that merges arbitrary monoidal dictionaries."

    def __init__(self, merge_fn=lambda _x, y: y):
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
    def first(a, _b):
        return a

    @staticmethod
    def second(_a, b):
        return b

# ...more monoids: JoinString, Concat, Collect, CollectUnique, CountUnique, Duplicated, Frequencies, Bag


#
# Monoid Combinators
#

def cartesian(monoids):
    "Returns a Monoid wrapper class for a cartesian product of other monoids."
    monoids = tuple(monoids)
    unit = tuple(m.munit for m in monoids)
    product_label = f'cartesian({", ".join(x.label for x in monoids)})'

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
