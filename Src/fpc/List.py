#
# The List Functor and relatives
#

from __future__ import annotations

from collections.abc import Iterable
from typing          import Callable

from Functor         import Functor, pymap
from Applicative     import Applicative, map2
from Monad           import Monad

__all__ = ['List',]


# 
# The List Functor
#
# type List a = Nil | Cons a (List a)
#
# This is a Functor, Applicative, and Monad
#

class List[A](Monad, list):
    def __new__(cls, *args, **kwds):
        return super().__new__(cls, *args, **kwds)

    def __repr__(self):
        return super().__repr__()

    def __getitem__(self, key):
        items = super().__getitem__(key)
        if isinstance(key, slice):
            return List(items)
        return items

    @classmethod
    def of(cls, *xs: tuple[Iterable[A], ...]):
        return cls(xs)

    def map[A, B](self, g: Callable[[A], B]):
        return List(pymap(g, self))

    @classmethod
    def pure(cls, a):
        return List([a])

    def map2[A, B, C](self, g: Callable[[A, B], C], fb: List[B]) -> List[C]:
        concat = []
        for a in self:
            for b in fb:
                concat.append(g(a, b))
        return List(concat)

    def bind(self, g: Callable[[A], List[B]]) -> List[B]:
        concat = []
        for a in self:
            concat.extend(g(a))
        return List(concat)

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
                        return []
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

    def traverse(self, f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        folded = f.pure(List())
        for item in self[-1::-1]:
            folded = map2(cons, g(item), folded)
        return folded

def cons[A](x: A, ls: List[A]) -> List[A]:
    "Prepends an element on the front of a list and returns it. O(n)"
    xs = List.pure(x)
    xs.extend(ls)
    return xs


#
# NonEmptyList
#
# type NonEmptyList a = Cons a (List a)
#


#
# ZipList
#
# This is a version of List with a different Applicative instance.
#
# ATTN
#
# newtype ZipList a = ZipList (List a)
#
