#
# The List Functor and relatives
#

from __future__ import annotations

from collections.abc import Iterable
from typing          import Callable

from .Monoids        import Monoid
from .Functor        import Functor, IndexedFunctor, pymap
from .Applicative    import Applicative, map2
from .Monad          import Monad
from .Foldable       import Foldable, IndexedFoldable
from .Traversable    import Traversable, IndexedTraversable

__all__ = ['List', 'NonEmptyList', 'ZipList', 'cons', 'snoc', 'snoc_']


#
# The List Functor
#
# type List a = Nil | Cons a (List a)
#
# This is a Functor, Applicative, and Monad
#

class List[A](list, Monad, Traversable):
    def __new__(cls, *args, **kwds):
        return super().__new__(cls, *args, **kwds)

    def __repr__(self):
        return super().__repr__()

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

    @classmethod
    def of(cls, *xs: tuple[Iterable[A], ...]):
        return cls(xs)

    def map[A, B](self, g: Callable[[A], B]):
        return self.__class__(pymap(g, self))

    def imap[I, A, B](self, g: Callable[[I, A], B]):
        return self.__class__(g(i, elt) for i, elt in enumerate(self))

    @classmethod
    def pure(cls, a):
        return cls([a])

    def map2[A, B, C](self, g: Callable[[A, B], C], fb: List[B]) -> List[C]:
        concat = []
        for a in self:
            for b in fb:
                concat.append(g(a, b))
        return self.__class__(concat)

    def bind(self, g: Callable[[A], List[B]]) -> List[B]:
        concat = []
        for a in self:
            concat.extend(g(a))
        return self.__class__(concat)

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
                    elif m == 0:
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

    def ifoldM[M](self, f: Callable[[I, A], M], monoid: Monoid) -> M:
        r = monoid.munit
        for index, elt in enumerate(self):
            m = f(index, elt)
            r = monoid.mcombine(r, m)
        return r

    def ifold[B](self, f: Callable[[I, B, A], B], initial: B) -> B:
        acc = initial
        for index, elt in enumerate(self):
            acc = f(index, acc, elt)
        return acc

    def traverse(self, f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        traversed = f.pure(List())
        for item in self:
            traversed = map2(append_, traversed, g(item))
        return traversed

    def itraverse[I](self, f: type[Applicative], g: Callable[[I, A], Applicative]) -> Applicative:  # g : i -> a -> f b
        traversed = f.pure(List())
        for index, item in enumerate(self):
            traversed = map2(append_, traversed, g(index, item))
        return traversed


#
# List Utilities
#

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

class NonEmptyList(List):
    def __init__(self, xs):
        if len(xs) == 0:
            raise ValueError('NonEmptyList cannot be empty')
        super().__init__(xs)

    def __delitem__(self, key):
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

    def pop(self, index=-1, /):
        if len(self) == 1:
            raise ValueError(f'pop({index}) would delete the only element of a NonEmptyList')
        return super().pop(index)

    def copy(self):
        return self.__class__(super().copy())


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

class ZipList(List):
    def map2[A, B, C](self, g: Callable[[A, B], C], fb: ZipList[B]) -> ZipList[C]:
        return self.__class__(pymap(g, self, fb))

    def bind(self, g: Callable[[A], ZipList[B]]) -> ZipList[B]:
        raise TypeError('ZipList does not have a Monad instance')

    @classmethod
    def __do__(cls, make_generator):
        raise TypeError('ZipList does not have a Monad instance')
