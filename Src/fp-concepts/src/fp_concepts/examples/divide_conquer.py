from __future__         import annotations
from abc                import ABC, abstractmethod
from typing             import Callable
from fp_concepts.Either import Either, Left, Right
from fp_concepts.Trees  import LeafyBinaryTree
from fp_concepts.Unit   import Unit

class DivideAndConquer[P, S](ABC):
    """Abstract base class for divide-and-conquer problem specification."""

    @abstractmethod
    def is_trivial(self, problem: P) -> S:
        "Tests if a problem instance is directly solvable (base case)."
        ...

    @abstractmethod
    def divide(self, problem: P) -> Either[P, tuple[P, P]]:
        """Splits a problem into two subproblems if not directly solvable

        Returns either the original problem in the base case
        or two subproblems if the original needs to be split.
        """
        ...

    @abstractmethod
    def conquered(self, problem: P) -> S:
        "Solves a directly solvable problem (base case)."
        ...

    @abstractmethod
    def conquer(self, solution1: S, solution2: S) -> S:
        "Combines the solutions of two subproblems into a solution for the larger problem."
        ...

# We maintain the invariant here that branch nodes have values of Unit type.
# However, the Python type system cannot enforce that requirement.
# We could alternatively use Maybe[A] as the value type for the tree.

def unfold[A, B](gen: Callable[[B], Either[A, tuple[B, B]]], seed: B) -> LeafyBinaryTree[A | Unit]:
    "Creates a binary tree by repeatedly unfolding a generating function from a starting seed."
    match gen(seed):
        case Left(base):
            return LeafyBinaryTree.leaf(base)
        case Right((seed_l, seed_r)):
            return LeafyBinaryTree.branch(unfold(gen, seed_l), unfold(gen, seed_r))
        case _:
            raise ValueError('Invalid form for generated value in unfold.')

def fold[A, S](trivial: Callable[[A], S], combine: Callable[[S, S], S], tree: LeafyBinaryTree[A | Unit]) -> S:
    "Reduce a D-and-C binary tree to a single solution by solving trivial cases and combining others."
    match tree.contents:
        case Left(value):
            return trivial(value)
        case Right((left, right)):
            return combine(fold(trivial, combine, left), fold(trivial, combine, right))
        case _:
            raise ValueError('Invalid binary tree contents')

def divide_and_conquer[P, S](spec: DivideAndConquer[P, S], initial: P) -> S:
    subproblems = unfold(spec.divide, initial)
    return fold(spec.conquered, spec.conquer, subproblems)


#
# Specific Examples
#
# For each problem instance, we create a concrete subclass of DivideAndConquer.
# Then for each relevant problem, we solve with divide_and_conquer().
#

# ATTN
