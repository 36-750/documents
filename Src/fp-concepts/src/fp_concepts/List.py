#
# The List Functor and relatives
#
# type List a = Nil | Cons a (List a)
#
#
# ruff: noqa: N802, EM102
#

from __future__ import annotations

from collections.abc import Callable

from .Applicative import Applicative, map2
from .Functor     import pymap
from .Monad       import Monad
from .Monoids     import Monoid
from .Traversable import Traversable

__all__ = ['List', 'NonEmptyList', 'ZipList',
           'zip_with', 'zip_longest',
           'cons', 'snoc', 'snoc_', 'append_']


#
# The List Functor
# ----------------
#
# While the motivating type is
#
#     type List a = Nil | Cons a (List a)
#
# it is simply implemented as a subclass of the
# built-in Python list.
#
# This is has an instance for many of the basic traits,
# including Functor, Applicative, Alternative, Monad,
# Foldable, and Traversable.
#

class List[A](list, Monad, Traversable):
    def __new__(cls, *args, **kwds):
        return super().__new__(cls, *args, **kwds)

    # Ensure List type conserved on slicing, concatenation, copy

    def __getitem__(self, key):
        items = super().__getitem__(key)
        if isinstance(key, slice):
            return self.__class__(items)
        return items

    def __add__(self, other):
        concat = super().__add__(other)
        return List(concat)

    def __radd__(self, other):
        concat = super().__radd__(other)
        return List(concat)

    def copy(self):
        return self.__class__(super().copy())

    # Analogue of built-in list construction
    # Example: List.of(1, 2, 3, 4)

    @classmethod
    def of(cls, *xs: A):
        """Returns a new List with the given arguments as elements.

        Examples:
          + List.of(1, 2, 3, 4)
          + List.of(Some(4), None_(), Some(10))

        """
        return cls(xs)

    # Functor and IndexedFunctor Instances

    def map[B](self, g: Callable[[A], B]):
        return self.__class__(pymap(g, self))

    # def imap[I, B](self, g: Callable[[I, A], B]):
    def imap[B](self, g: Callable[[int, A], B]):
        return self.__class__(g(i, elt) for i, elt in enumerate(self))

    # Applicative Instance

    @classmethod
    def pure(cls, a):
        return cls([a])

    def map2[B, C](self, g: Callable[[A, B], C], fb: List[B]) -> List[C]:
        concat = []
        for a in self:
            for b in fb:
                concat.append(g(a, b))
        return self.__class__(concat)   # type: ignore

    # Alternative Instance

    @classmethod         # ATTN: 30 Sep 2025 from @property
    def empty(self):
        return self.__class__([])

    def alt(self, fb):
        return self.__class__([*self, *fb])

    # Monad Instance

    def bind[B](self, g: Callable[[A], List[B]]) -> List[B]:
        concat: list[B] = []
        for a in self:
            concat.extend(g(a))
        return self.__class__(concat)  # type: ignore

    @classmethod
    def __do__(cls, make_generator):
        def increment(pos: list[tuple[int, int]]) -> int:
            i, m = pos[-1]
            if i + 1 >= m:
                while i + 1 >= m:
                    pos.pop()
                    if len(pos) == 0:
                        break
                    i, m = pos[-1]
                else:
                    pos[-1] = (i + 1, m)

                return -1

            pos[-1] = (i + 1, m)
            return i + 1

        joined = []
        positions: list[tuple[int, int]] = []

        while True:
            index = 0
            bound = None
            generator = make_generator()
            try:
                while True:
                    x = generator.send(bound)
                    m = len(x)
                    if m == 0 and len(positions) == 0:
                        return List()
                    if m == 0:
                        increment(positions)
                        break

                    if index >= len(positions):
                        positions.append((0, m))
                        i = 0
                    else:
                        i = positions[index][0]
                    bound = x[i]
                    index += 1
            except StopIteration as finished:
                joined.append(finished.value)
                increment(positions)
            if len(positions) == 0:
                return List(joined)

    # Foldable and IndexedFoldable Instances

    def foldM[M](self, f: Callable[[A], M], monoid: Monoid) -> M:
        r = monoid.munit
        for elt in self:
            m = f(elt)
            r = monoid.mcombine(r, m)
        return r

    def fold[B](self, f: Callable[[B, A], B], initial: B) -> B:
        acc = initial
        for elt in self:
            acc = f(acc, elt)
        return acc

    def ifoldM[M](self, f: Callable[[int, A], M], monoid: Monoid) -> M:
        r = monoid.munit
        for index, elt in enumerate(self):
            m = f(index, elt)
            r = monoid.mcombine(r, m)
        return r

    def ifold[B](self, f: Callable[[int, B, A], B], initial: B) -> B:
        acc = initial
        for index, elt in enumerate(self):
            acc = f(index, acc, elt)
        return acc

    # Traversable and IndexedTraversable Instances

    def traverse(self, f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        traversed = f.pure(List())
        for item in self:
            traversed = map2(append_, traversed, g(item))
        return traversed

    def itraverse(self, f: type[Applicative], g: Callable[[int, A], Applicative]) -> Applicative:  # g : i -> a -> f b
        traversed = f.pure(List())
        for index, item in enumerate(self):
            traversed = map2(append_, traversed, g(index, item))
        return traversed


#
# List Utilities
#

def zip_with[A, B, C](g: Callable[[A, B], C], fa: List[A], fb: List[B]) -> List[C]:
    """ATTN

    The returned collection has type List even if the arguments are subclasses.
    See also ZipList.

    """
    return List(pymap(g, fa, fb))

def zip_longest[A, B, C](g: Callable[[A, B], C], fa: List[A], fb: List[B], default: C) -> List[C]:
    """ATTN

    The returned collection has type List even if the arguments are subclasses.
    See also ZipList.

    """
    m = len(fa)
    n = len(fb)
    extra = max(m, n) - min(m, n)
    zipped = list(pymap(g, fa, fb))
    padded = [default] * extra
    return List([*zipped, *padded])

def cons[A](x: A, ls: List[A]) -> List[A]:
    "Prepends an element on the front of a list and returns it. O(n) in Python."
    xs = List.pure(x)
    xs.extend(ls)
    return xs

def snoc[A](x: A, ls: List[A]) -> List[A]:
    "Appends an element at the back of a list and returns it. O(n) from copy."
    return ls + List.of(x)

def snoc_[A](x: A, ls: List[A]) -> List[A]:
    "Mutating append of an element at the back of a list and returns it. O(1) in Python"
    ls.append(x)
    return ls

def append_[A](ls: List[A], x: A) -> List[A]:
    "Flipped version of snoc_ to ensure applicative effects are in the right order."
    ls.append(x)
    return ls


#
# NonEmptyList
#
# type NonEmptyList a = Cons a (List a)
#

class NonEmptyList[A](List[A]):
    def __init__(self, xs):
        if len(xs) == 0:
            raise ValueError('NonEmptyList cannot be empty')
        super().__init__(xs)

    # Maintain non-empty invariant on removal operations

    def __delitem__(self, key):
        # pylint: disable=too-many-boolean-expressions
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            # ATTN: Check this test when step > 1, just a quick stab here
            if ((step == 1  and stop - start >= len(self)) or
                (step == -1 and start - stop >= len(self)) or
                (abs(step) > 1 and abs(stop - start) > 0 and len(self) == 1)):
                raise ValueError(f'del[{key}] would delete all elements of a NonEmptyList')
        elif len(self) == 1:
            raise ValueError(f'del[{key}] would remove the only element of a NonEmptyList')

        super().__delitem__(key)

    def clear(self):
        raise ValueError('clear would delete all elements of a NonEmptyList')

    def remove(self, value, /):
        if len(self) == 1:
            raise ValueError('remove would delete the only element of a NonEmptyList')
        super().remove(value)

    def pop(self, index=-1, /) -> A:
        if len(self) == 1:
            raise ValueError(f'pop({index}) would delete the only element of a NonEmptyList')
        return super().pop(index)


#
# ZipList
#
#     newtype ZipList a = ZipList (List a)
#
# This is a version of List with a different Applicative instance.
# ZipLists behave just like Lists, but the applicative mappings
# work *elementwise*. So, for example:
#
#   map2 mul [1, 2, 3, 4] [10, 20, 30] == [10, 40, 90]
#
# with the length of the shortest list. Note that this is the
# behavior of the builtin Python map with multiple arguments.
#

class ZipList[A](List):
    def map2[B, C](self, g: Callable[[A, B], C], fb: List[B]) -> ZipList[C]:
        return self.__class__(pymap(g, self, fb))  # type: ignore

    def __repr__(self):
        base = super().__repr__()
        return f'ZipList({base})'

    # There is no Monad Instance

    def bind[B](self, _g: Callable[[A], List[B]]) -> ZipList[B]:
        raise TypeError('ZipList does not have a Monad instance')

    @classmethod
    def __do__(cls, make_generator):
        raise TypeError('ZipList does not have a Monad instance')
