#
# Various forms of Tree as Functors
#
from __future__ import annotations

from functools   import partial
from typing      import Callable, TypeGuard

from Functor     import Functor, map
from Applicative import Applicative, map2
from Traversable import Traversable, traverse
from List        import List

__all__ = ['BinaryTree', 'Tip', 'is_binary_tree', 'binary_tree', 'complete_btree',
           'RoseTree',]


#
# Helpers
#

class Tip_:
    "A standin for None in specifying Binary Trees in s-expression format."
    def __repr__(self):
        return 'Tip'

    def __bool__(self):
        return False

Tip = Tip_()  # Singleton


#
# Binary Trees
#
# type BinaryTree a = Tip | Node (BinaryTree a) a (BinaryTree a)
#

class AbstractBinaryTree(Functor):  # Abstract Base Class
    def to_sexp(self):
        ...

    def as_str(self, levels=[]):
        ...

class BinaryTree[A](AbstractBinaryTree):
    def __init__(self, sexp: list | tuple):
        "Creates a Binary Tree from s-expression input. See `to_sexp`."
        if len(sexp) == 0:  # Handle empty case elsewhere
            raise ValueError('Binary tree requires a nonempty root node, use binary_tree() for this case.')

        val, left, right, *_ = sexp
        self._value = val
        self._left = BinaryTree(List(left)) if left else None
        self._right = BinaryTree(List(right)) if right else None

    def to_sexp(self):
        """Converts a binary tree to s-expression format.

        A tree is represented by a list or tuple of the form
            [data, left, right] or (data, left, right),
        where left and right are either Tip for empty subtrees
        or lists/tuples in s-expression format for non-empty
        subtrees.

        Example: [1,
                  [2, [4, None, None], [5, None, None]],
                  [3, [6, None, None], None]]

        When created from input, as in the BinaryTree constructor,
        any falsy value can stand in for Tip.

        This returns the s-expression as a list rather than a tuple
        so that the result can be modified.

        """
        return [
            self._value,
            self._left and self._left.to_sexp(),
            self._right and self._right.to_sexp()
        ]

    def as_str(self, levels=[]):
        "Returns a simple string representation of this tree"
        indent = ''.join('\u2502  ' if level == 0 else '   ' for level in levels)
        leadL = '\u251c\u2500 '
        leadR = '\u2514\u2500 '
        root = f'{self._value}\n'
        if self._left or self._right:
            left = f'{indent}{leadL}{self._left.as_str(levels + [0]) if self._left else "\u25a1\n"}'
            right = f'{indent}{leadR}{self._right.as_str(levels + [1]) if self._right else "\u25a1\n"}'
        else:
            left = right = ''
        return root + left + right

    def __str__(self):
        return self.as_str().strip()

    @classmethod
    def unfold[A, B](cls, gen: Callable[[B], tuple[A, Optional[B], Optional[B]]], seed: B) -> BinaryTree[A]:
        "Creates a binary tree by repeatedly unfolding a generating function from a starting seed."
        def unfold_sexp(s):
            if s is None:
                return None

            a, seedL, seedR = gen(s)
            return [a, unfold_sexp(seedL), unfold_sexp(seedR)]

        return BinaryTree(unfold_sexp(seed))

    def map[A, B](self, g: Callable[[A], B]):
        "Functor instance that maps a function over this binary tree."
        tree = BinaryTree([g(self._value), None, None])
        tree._left = map(g, self._left) if self._left else None
        tree._right = map(g, self._right) if self._right else None
        return tree

class EmptyBinaryTree[A](AbstractBinaryTree):
    "A look-alike representing an empty Binary Tree, for any value type."
    @classmethod
    def unfold[A, B](cls, gen: Callable[[B], tuple[A, Optional[B], Optional[B]]], seed: B) -> BinaryTree[A]:
        return BinaryTree.unfold(gen, seed)

    def to_sexp(self):
        return []

    def __str__(self):
        return str(Tip)

    def as_str(self, levels=[]):
        return str(self)

    def map[A, B](self, g: Callable[[A], B]):
        return self

def is_binary_tree(t) -> TypeGuard[BinaryTree]:   # Duck typing here
    "Tests if object is a Binary Tree."
    return isinstance(t, AbstractBinaryTree)

def binary_tree(spec=None, seed=None):
    "Smart binary tree constructor."
    if not spec:
        return EmptyBinaryTree()

    if is_binary_tree(spec):
        return spec   # ATTN: deep copy?

    if callable(spec):
        BinaryTree.unfold(spec, seed)

    if isinstance(spec, (tuple, list)):
        return BinaryTree(spec)

    raise ValueError(f'Unable to construct a binary tree from input: {spec}')

def complete_btree(depth: int) -> BinaryTree[int]:
    "Returns a complete binary tree of given depth with integer data."
    def generate(k):
        if k < 2 ** depth - 1:
            return (k, 2 * k + 1, 2 * k + 2)
        return (k, None, None)

    return BinaryTree.unfold(generate, 0)

#
# Rose Trees
#
# type RoseTree a = Node a (List (RoseTree a))
#

class RoseTree[A](Applicative):
    def __init__(self, sexp: list):
        "Creates a Rose Tree from s-expression input. See `to_sexp`."
        if len(sexp) == 0:
            raise ValueError('Rose tree requires a nonempty root node.')

        val, *children = sexp
        self._data = val
        self._children = List(RoseTree(child) for child in children)

    def to_sexp(self):
        """Converts a rose tree to s-expression format.

        A tree is represented by a list [data, children], where
        children are sub-trees specified by lists in s-expression
        format. Leaf nodes are thus given by singleton lists
        [v] with data v.

        Example: [1, [2, [3], [4], [5]], [6, [7, [8, [9], [10]]]]],

        """
        return [
            self._data,
            *[child.to_sexp() for child in self._children]
        ]

    def as_str(self, levels=[]):
        "Returns a simple string representation of this tree"
        # level == 1 for rightmost subtree
        indent = ''.join('\u2502  ' if level == 0 else '   ' for level in levels)
        leadA = '\u251c\u2500 '
        leadR = '\u2514\u2500 '
        str_form = [f'{self._data}\n']
        n = len(self._children)
        for index, child in enumerate(self._children):
            if index < n - 1:
                str_form.append(f'{indent}{leadA}{child.as_str(levels + [0])}')
            else:
                str_form.append(f'{indent}{leadR}{child.as_str(levels + [1])}')
        return "".join(str_form)

    def __str__(self):
        return self.as_str().strip()

    @classmethod
    def make(cls, data: A, children: list[A]) -> RoseTree[A]:
        t = cls([data])
        t._children = List(children)
        return t

    @classmethod
    def unfold[A, B](cls, gen: Callable[[B], tuple[A, list[B]]], seed: B) -> RoseTree[A]:
        "Creates a rose tree by repeatedly unfolding a generating function from a starting seed."
        def unfold_sexp(s):
            a, seeds = gen(s)

            if len(seeds) == 0:
                return [a]

            return [a, *[unfold_sexp(seed) for seed in seeds]]

        return RoseTree(unfold_sexp(seed))

    def fold[B](self, f: Callable[[A, list[B]], B]) -> B:
        """ Folds the tree into a single value.

        This has type Tree a -> (a -> [b] -> b) -> Tree b.

        """
        def go(t):
            return f(t._data, map(go, t._children))
        return go(self)

    def map[B](self, g: Callable[[A], B]):
        "Functor instance that maps a function over this rose tree."
        tree = RoseTree([g(self._data)])
        tree._children = List(map(g, child) for child in self._children)
        return tree

    @classmethod
    def pure(cls, a):
        return RoseTree([a])

    def map2[B, C](self, f: Callable[[A, B], C], tb: RoseTree[B]) -> RoseTree[C]:
        new_tree = RoseTree([f(self._data, tb._data)])

        g = lambda sub_b: map(partial(f, self._data), sub_b)
        h = lambda sub_a: map2(f, sub_a, tb)

        ab_cs = map(g, tb._children)
        ab_cs.extend(map(h, self._children))
        new_tree._children = ab_cs

        return new_tree

    def traverse(self, f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        def go(t):
            return map2(RoseTree.make, g(t._data), traverse(f, go, t._children))

        return go(self)
