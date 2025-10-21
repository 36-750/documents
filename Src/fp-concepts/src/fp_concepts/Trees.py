#
# Various forms of Tree as Functors
#
# ruff: noqa: N801, N806, E731, EM102

from __future__ import annotations

from collections.abc import Callable
from functools       import partial
from typing          import TypeGuard

from .Applicative import Applicative, map2, ap
from .Functor     import IndexedFunctor, map, imap
from .List        import List
from .Traversable import traverse, itraverse

__all__ = ['BinaryTree', 'Tip', 'is_binary_tree', 'binary_tree', 'complete_btree',
           'RoseTree', 'SExp',]


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

class SExp(list):
    "A Marker class to distinguish lists as values from lists as s-expressions."
    def __init__(self, xs):
        super().__init__(xs)


#
# Binary Trees
#
# type BinaryTree a = Tip | Node (BinaryTree a) a (BinaryTree a)
#

class AbstractBinaryTree(IndexedFunctor):  # Abstract Base Class
    def to_sexp(self):
        ...

    def as_str(self, levels=None):
        ...

class BinaryTree[A](AbstractBinaryTree):
    def __init__(self, sexp: list | tuple):
        "Creates a Binary Tree from s-expression input. See `to_sexp`."
        if len(sexp) == 0:  # Handle empty case elsewhere
            raise ValueError('Binary tree requires a nonempty root node, use binary_tree() for this case.')

        val, left, right, *_ = sexp
        self._value = val
        self._left: BinaryTree[A] | Tip_ = BinaryTree(List(left)) if left else Tip
        self._right: BinaryTree[A] | Tip_ = BinaryTree(List(right)) if right else Tip

    @classmethod
    def make(cls, data: A, left: BinaryTree[A], right: BinaryTree[A]) -> BinaryTree[A]:
        t = cls([data, Tip, Tip])
        t._left = left
        t._right = right
        return t

    def to_sexp(self):
        """Converts a binary tree to s-expression format.

        A tree is represented by a list or tuple of the form
            [data, left, right] or (data, left, right),
        where left and right are either Tip for empty subtrees
        or lists/tuples in s-expression format for non-empty
        subtrees.

        Example: [1,
                  [2, [4, Tip, Tip], [5, Tip, Tip]],
                  [3, [6, Tip, Tip], Tip]]

        When created from input, as in the BinaryTree constructor,
        any falsy value can stand in for Tip.

        This returns the s-expression as a list rather than a tuple
        so that the result can be modified.

        """
        return SExp([
            self._value,
            self._left and self._left.to_sexp(),
            self._right and self._right.to_sexp()
        ])

    def as_str(self, levels=None):
        "Returns a simple string representation of this tree"
        if levels is None:
            levels = []
        indent = ''.join('\u2502  ' if level == 0 else '   ' for level in levels)
        leadL = '\u251c\u2500 '
        leadR = '\u2514\u2500 '
        root = f'{self._value}\n'
        if self._left or self._right:
            left = f'{indent}{leadL}{self._left.as_str([*levels, 0]) if self._left else "\u25a1\n"}'
            right = f'{indent}{leadR}{self._right.as_str([*levels, 1]) if self._right else "\u25a1\n"}'
        else:
            left = right = ''
        return root + left + right

    def __str__(self):
        return self.as_str().strip()

    @classmethod
    def unfold[B](cls, gen: Callable[[B], tuple[A, B | Tip_ | None, B | Tip_ | None]], seed: B) -> BinaryTree[A]:
        "Creates a binary tree by repeatedly unfolding a generating function from a starting seed."
        def unfold_sexp(s):
            if s is None or s is Tip:
                return Tip

            a, seedL, seedR = gen(s)
            return [a, unfold_sexp(seedL), unfold_sexp(seedR)]

        return BinaryTree(unfold_sexp(seed))

    def map[B](self, g: Callable[[A], B]) -> BinaryTree[B]:
        "Maps a function over this binary tree, returning a new tree."
        tree: BinaryTree[B] = BinaryTree([g(self._value), Tip, Tip])
        tree._left = map(g, self._left) if self._left else Tip        # type: ignore  # _left: BinaryTree[A] if not Tip
        tree._right = map(g, self._right) if self._right else Tip     # type: ignore  # _right: BinaryTree[A] if not Tip
        return tree

    def imap[I, B](self, g: Callable[[I, A], B]):
        "Maps an indexed function over this binary tree, returning a new tree."
        def go(index, tree):
            t = BinaryTree([g(index, tree._value), Tip, Tip])
            t._left = go(index + List.of(0), tree._left) if tree._left else Tip
            t._right = go(index + List.of(1), tree._right) if tree._right else Tip
            return t
        return go(List(), self)

    @staticmethod
    def _bt_traverse(effect, node_f, subtree_f, t):
        fl = subtree_f(t._left) if t._left else effect.pure(Tip)
        fa = node_f(t._value)
        fr = subtree_f(t._right) if t._right else effect.pure(Tip)
        return ap(ap(BinaryTree.make, fa, fl), fr)

    def traverse(self, f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        def inorder(tree):
            return self._bt_traverse(f, g, inorder, tree)
        return inorder(self)


class EmptyBinaryTree[A](AbstractBinaryTree):
    "A look-alike representing an empty Binary Tree, for any value type."
    @classmethod
    def unfold[B](cls, gen: Callable[[B], tuple[A, B | Tip_ | None, B | Tip_ | None]], seed: B) -> BinaryTree[A]:
        return BinaryTree.unfold(gen, seed)

    def to_sexp(self):
        return []

    def __str__(self):
        return str(Tip)

    def as_str(self, _levels=None):
        return str(self)

    def map[B](self, _g: Callable[[A], B]):
        return self

    def traverse(self, f: type[Applicative], _g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        return f.pure(self)

def is_binary_tree(t) -> TypeGuard[BinaryTree]:   # Duck typing here for type inference
    "Tests if object is a Binary Tree."
    return isinstance(t, AbstractBinaryTree)

def binary_tree(spec=None, left=Tip, right=Tip, *, seed=None, sexp=None):
    """Smart binary tree constructor.

    Accepts a variety of argument configurations:

    + binary_tree() -- gives the empty BinaryTree
    + binary_tree(bt) -- for bt : BinaryTree, returns bt as is
    + binary_tree(sexp=[...]) -- builds tree from an S-expression
    + binary_tree(SExp([...])) -- builds tree from an S-expression
    + binary_tree(f, seed=x) -- unfolds tree with f and starting seed x
    + binary_tree(data, left, right) -- returns BinaryTree data left right.

    A tree can be specified from an S-expression using either the
    sexp= keyword (alone) or by wrapping the S-expression for the
    tree in SExp(). This extra work is needed to distinguish from
    trees with tuple or list data types. Note that
    BinaryTree.to_sexp returns a SExp object and so can be used
    directly. Also note that BinaryTree accepts an sexp without
    wrapper.

    """
    if not spec and not sexp:
        return EmptyBinaryTree()

    if is_binary_tree(spec):
        return spec   # ATTN: deep copy?

    if callable(spec):
        BinaryTree.unfold(spec, seed)

    if not spec and sexp:
        return BinaryTree(sexp)

    if isinstance(spec, SExp):
        return BinaryTree(spec)

    if isinstance(spec, str):  # Named trees, params in left, right, seed
        if 'complete'.startswith(spec.lower()):
            return complete_btree(left if left else 0)
        raise KeyError(f'Unrecognized named binary tree {spec}')

    return BinaryTree.make(spec, left, right)

def complete_btree(depth: int) -> BinaryTree[int]:
    "Returns a complete binary tree of given depth with integer data."
    def generate(k):
        if k < 2 ** depth - 1:
            return (k, 2 * k + 1, 2 * k + 2)
        return (k, Tip, Tip)

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
        self._value = val
        self._children: List = List(RoseTree(child) for child in children)  # Note: mypy forces hint

    def to_sexp(self):
        """Converts a rose tree to s-expression format.

        A tree is represented by a list [data, children], where
        children are sub-trees specified by lists in s-expression
        format. Leaf nodes are thus given by singleton lists
        [v] with data v.

        Example: [1, [2, [3], [4], [5]], [6, [7, [8, [9], [10]]]]],

        """
        return List.of(
            self._value,
            *[child.to_sexp() for child in self._children]
        )

    def as_str(self, levels=None):
        "Returns a simple string representation of this tree"
        if levels is None:
            levels = []
        indent = ''.join('\u2502  ' if level == 0 else '   ' for level in levels)
        leadA = '\u251c\u2500 '
        leadR = '\u2514\u2500 '
        str_form = [f'{self._value}\n']
        n = len(self._children)
        for index, child in enumerate(self._children):
            if index < n - 1:
                str_form.append(f'{indent}{leadA}{child.as_str([*levels, 0])}')
            else:
                str_form.append(f'{indent}{leadR}{child.as_str([*levels, 1])}')
        return "".join(str_form)

    def __str__(self):
        return self.as_str().strip()

    @classmethod
    def make(cls, data: A, children: list[A]) -> RoseTree[A]:
        t = cls([data])
        t._children = List(children)
        return t

    @classmethod
    def unfold[B](cls, gen: Callable[[B], tuple[A, list[B]]], seed: B) -> RoseTree[A]:
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
            return f(t._value, map(go, t._children))
        return go(self)

    def map[B](self, g: Callable[[A], B]):
        "Functor instance that maps a function over this rose tree."
        tree: RoseTree = RoseTree([g(self._value)])  # Note: mypy forces annotation here??
        tree._children = List(map(g, child) for child in self._children)
        return tree

    def imap[I, B](self, g: Callable[[I, A], B]):
        "Maps an indexed function over this tree, returning a new tree."
        def go(index, tree):
            t = RoseTree([g(index, tree._value)])
            t._children = imap(lambda j, s: go(index + List.of(j), s), tree._children)
            return t
        return go(List(), self)

    @classmethod
    def pure(cls, a):
        return RoseTree([a])

    def map2[B, C](self, f: Callable[[A, B], C], tb: RoseTree[B]) -> RoseTree[C]:
        new_tree: RoseTree = RoseTree([f(self._value, tb._value)])

        g = lambda sub_b: map(partial(f, self._value), sub_b)
        h = lambda sub_a: map2(f, sub_a, tb)

        ab_cs = map(g, tb._children)
        ab_cs.extend(map(h, self._children))
        new_tree._children = ab_cs

        return new_tree

    def traverse(self, f: type[Applicative], g: Callable[[A], Applicative]) -> Applicative:  # g : a -> f b
        def go(t):
            return map2(RoseTree.make, g(t._value), traverse(go, t._children, f))

        return go(self)

    def itraverse[I](self, f: type[Applicative], g: Callable[[I, A], Applicative]) -> Applicative:  # g : a -> f b
        def go(index, t):
            return map2(RoseTree.make, g(index, t._value),
                        itraverse(lambda i, s: go(index + List.of(i), s), t._children, f))

        return go(List(), self)
