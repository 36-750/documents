from abc             import ABC
from collections.abc import Iterable
from functools       import partial

#
# Functor as a mixin
#

class Functor(ABC):
    def map(self, g, fa):
        ...

pymap = map  # Reference to built-in map

def map(f, F):
    "Maps a function over a functor."
    return F.map(f)

def lift(f):
    "Lifts a function to a mapping on functors."
    def lift_f(F):
        return F.map(f)
 
    return lift_f


#
# One way to formalize Maybe, if we want to
#

class Maybe(Functor):
    def get(self, default):
        ...
    ...

class Some(Maybe):
    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return f'Some {self._value}'

    def get(self, default_):
        return self._value

    def map(self, g):
        try:
            return Some(g(self._value))
        except Exception:
            return None_()

class None_(Maybe):   # The name None is already taken
    def __repr__(self):
        return f'None'

    def get(self, default):
        return default

    def map(self, g):
        return self


#
# List
#

class List(Functor, list):
    def __new__(cls, contents):
        return super().__new__(cls, contents)

    def __repr__(self):
        return super().__repr__()

    def map(self, g):
        return List(pymap(g, self))

    @classmethod
    def of(cls, *xs):
        return cls(xs)


#
# Binary Trees
#

class BinaryTree(Functor):
    def __init__(self, sexp: list):
        if len(sexp) == 0:
            raise ValueError('Binary tree requires a nonempty root node.')

        val, left, right, *_ = sexp
        self._value = val
        self._left = BinaryTree(left) if left else None
        self._right = BinaryTree(right) if right else None

    def to_list(self):
        return [
            self._value,
            self._left and self.to_list(self._left),
            self_right and self.to_list(self._right)
        ]
        
    def as_str(self, level=0):
        indent = ' ' * (level * 4)
        lead = '|--- '
        shift = '' if level == 0 else ' '
        root = f'{self._value}\n'
        left = f'{shift}{indent}{lead}{self._left.as_str(level + 1)}' if self._left else f'{shift}{indent}{lead}.\n'
        right = f'{shift}{indent}{lead}{self._right.as_str(level + 1)}' if self._right else f'{shift}{indent}{lead}.\n'
        return root + left + right

    def __str__(self):
        return self.as_str().strip()

    def map(self, g):
        tree = BinaryTree([g(self._value), None, None])
        tree._left = map(g, self._left) if self._left else None
        tree._right = map(g, self._right) if self._right else None
        return tree

if __name__ == '__main__':
    x = Some(10)
    y = None_()
    z = List.of(1, 2, 3, 4, 5)
    u = List.of(Some(1), None_(), Some(2), None_(), Some(3))
    w = ['a', 'b', 'c']
    t = BinaryTree([1, [2, [3, None, None], [4, None, None]], [5, None, None]])

    add = lambda a, b: a + b
    inc = lambda v: v + 1
    incF = lift(inc)
    parenthesize = lambda s: '(' + s + ')'

    print( x.get(0) )
    print( y.get(0) )
    print( map(inc, x) )
    print( map(inc, y) )
    print( map(inc, z) )
    print( map(incF, u) )
    print( map(parenthesize, List(w)) )
    print(t)
    print( map(partial(add, 10), t) )
