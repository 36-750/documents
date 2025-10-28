# pylint: disable=too-few-public-methods

"""Implements simple Huffman encoding/decoding of tokens from a known distribution.

Example:
  >>> import fp_concepts.examples.huffman
  >>> from fp_concepts.examples.huffman import huffman, encode, decode, make_code
  >>> h0 = huffman(['a', 'b', 'c','d','e','f'], [0.45, 0.13, 0.12, 0.16, 0.09, 0.05])
  >>> print(h0.code_tree)
  •
  ├─ a
  └─ •
     ├─ •
     │  ├─ c
     │  └─ b
     └─ •
        ├─ •
        │  ├─ f
        │  └─ e
        └─ d
  >>> h0.code_words
  {'a': '0', 'c': '100', 'b': '101', 'f': '1100', 'e': '1101', 'd': '111'}
  >>> encode(h0, "abcdef")
  '010110011111011100'
  >>> make_code(h0.code_tree)
  [('a', '0'), ('c', '100'), ('b', '101'), ('f', '1100'), ('e', '1101'), ('d', '111')]
  >>> decode(h0,'010110011111011100')
  ['a', 'b', 'c', 'd', 'e', 'f']

Decoding can accept input from a string or a text stream. When decoding
completes mid-codeword an IncompleteCodeword warnign is raised. But this
warning includes the decoded input so far, so the warning can be ignored
as follows:

  >>> try:
  ...     decode(h0,'011111')
  ... except IncompleteCodeword as d:
  ...     d.decoded


"""
__all__ = [
    'IncompleteCodeword',
    'HuffmanCode',
    'decode',
    'encode',
    'huffman',
    'huffman_tree',
    'make_code',
]

import heapq

from collections.abc import Collection, Iterable
from io              import TextIOBase, StringIO   # Move first to Reader in 3.14+
from typing          import Literal, NamedTuple

from fp_concepts.Either    import Left, Right
from fp_concepts.List      import NonEmptyList
from fp_concepts.Trees     import LeafyBinaryTree
from fp_concepts.functions import identity
from fp_concepts.ops       import foldMap, Collect

class PriorityQueue:
    def __init__(self):
        self.queue = []
        heapq.heapify(self.queue)

    def insert(self, item):
        heapq.heappush(self.queue, item)
        return self

    def pop_min(self):
        return heapq.heappop(self.queue)

class IncompleteCodeword(UserWarning):
    """Warning that decoding completed mid-codeword.

    The decoded input up to this point is passed as
    the second argument so that it can be used
    by the user if this warning is caught and ignored.

    """
    def __init__(self, message, decoded=None):
        super().__init__(message)
        self.decoded = decoded


def step_down[A](tree: LeafyBinaryTree[A]):
    """Generator for successive steps left or right down a tree

    If gen is the returned generator, start with gen.send(None),
    then on successive gen.send(x) where x is either 0, 1, '0', '1',
    False, or True (with '0', 0, False for left and the others for
    right), yields a Node or returns the leaf value, as the
    the value of the StopIteration exception.

    An error is raised if trying to step from a leaf, and the caller
    should check that a leaf is not returned too early.

    Returns a generator object.

    """
    subtree = tree
    while True:
        step: Literal['0', '1', 0, 1, False, True] = yield subtree
        match subtree.root:
            case Left(a_leaf):
                raise ValueError(f'step_down: Moving down at a leaf {a_leaf} in a LeafyBinaryTree')
            case Right((left, right)):
                subtree = left if int(step) == 0 else right
                match subtree.root:
                    case Left(leaf):
                        return leaf
                    case _:
                        pass

def huffman_tree(tokens: Collection, probs: Iterable) -> LeafyBinaryTree:
    "Computes a Huffman Code tree for a distribution on a set of tokens."
    q = PriorityQueue()
    for f, t in zip(probs, tokens):
        q.insert((f, LeafyBinaryTree.leaf(t)))

    n = len(tokens)
    for _ in range(1, n):
        prob1, min1 = q.pop_min()
        prob2, min2 = q.pop_min()
        new_prob = prob1 + prob2
        q.insert((new_prob, LeafyBinaryTree.branch(min1, min2)))
    return q.pop_min()[1]

def make_code[A](bt: LeafyBinaryTree[A]) -> NonEmptyList[tuple[A, str]]:
    "Returns token-codeword pairs for a binary tree representing a prefix code."
    def code_pair(index: list[Literal[0, 1]], value: A) -> tuple[A, str]:
        index_str = "".join(map(str, index))
        return (value, index_str)

    return NonEmptyList(foldMap(identity, bt.imap(code_pair), Collect))

class HuffmanCode[A](NamedTuple):
    code_tree: LeafyBinaryTree[A]
    code_words: dict[A, str]

def huffman[A](tokens: Collection[A], probs: Iterable[float]) -> HuffmanCode[A]:
    """Computes a Huffman code for a distribution on a given set of tokens.

    Parameters
    ----------
    tokens - a sequence of distinct token objects of any type
    probs  - a sequence of token probabilities in the same order
        as tokens. Must sum to 1.

    Returns a pair:
        1. The tree representing the code
        2. A dictionary mapping tokens to codewords.

    See `encode` and `decode` below.

    """
    htree = huffman_tree(tokens, probs)
    hcode = dict(make_code(htree))
    return HuffmanCode(code_tree=htree, code_words=hcode)

def encode[A](code: HuffmanCode[A], tokens: Iterable[A]) -> str:
    """Encodes a series of tokens with a compatible Huffman code.

    Unrecognized tokens are raise an error.

    Returns an encoded string.

    """
    code_words = code.code_words
    encoded = []
    for token in tokens:
        encoded.append(code_words[token])

    return "".join(encoded)

def decode[A](code: HuffmanCode[A], encoded: str | TextIOBase) -> Iterable[A]:
    """Decodes a text stream encoded with a given Huffman code.

    If a string is passed instead of a stream, it is converted
    to a stream. This allows input from a variety of sources.

    Returns the sequence of tokens.

    """
    if isinstance(encoded, str):  # Convert to a stream
        encoded = StringIO(encoded)

    code_tree = code.code_tree
    decoded = []
    start_word = True

    while (zero_one := encoded.read(1)):
        if start_word:
            gen = step_down(code_tree)
            gen.send(None)
            start_word = False
        try:
            gen.send(zero_one)
        except StopIteration as e:
            decoded.append(e.value)
            start_word = True

    if not start_word:  # Stopped mid-codeword
        raise IncompleteCodeword('Decoding completed in the middle of a codeword', decoded)
    return decoded
