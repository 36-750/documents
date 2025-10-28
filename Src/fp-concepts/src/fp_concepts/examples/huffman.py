# pylint: disable=too-few-public-methods

import heapq

from fp_concepts.Trees import LeafyBinaryTree

class PriorityQueue:
    def __init__(self):
        self.queue = []
        heapq.heapify(self.queue)

    def insert(self, item):
        heapq.heappush(self.queue, item)
        return self

    def pop_min(self):
        return heapq.heappop(self.queue)

class BTree:
    pass

class Branch(BTree):
    def __init__(self, freq, left, right):
        self.freq = freq
        self.left = left
        self.right = right

class Leaf(BTree):
    def __init__(self, freq, leaf):
        self.freq = freq
        self.leaf = leaf

def huffman(tokens, freqs):
    q = PriorityQueue()
    for f, t in zip(freqs, tokens):
        q.insert((f, LeafyBinaryTree.leaf(t)))

    n = len(tokens)
    for _ in range(1, n):
        freq1, min1 = q.pop_min()
        freq2, min2 = q.pop_min()
        new_freq = freq1 + freq2
        q.insert((freq1 + freq2, LeafyBinaryTree.branch(min1, min2)))
    return q.pop_min()[1]
