#!/usr/bin/env python

from collections import defaultdict


class EagerObjectSets(object):
    def __init__(self, n):
        self.n = n
        self.root = list(range(n))

    def find(self, id1, id2):
        "Are objects id1 and id2 connected?"
        return self.root[id1] == self.root[id2]

    def union(self, id1, id2):
        "Connect objects id1 and id2."
        root1 = self.root[id1]
        root2 = self.root[id2]
        for id in range(self.n):
            if self.root[id] == root1:
                self.root[id] = root2

    def forest(self):
        """
        Return the current forest as a list of lists.
        Each entry is of the form [root children...].

        """
        disjoint_sets = defaultdict(list)
        for id, root in enumerate(self.root):
            if id == root:
                disjoint_sets[root].insert(0, root)
            else:
                disjoint_sets[root].append(id)
        return [aset for aset in disjoint_sets.values()]

    def __str__(self):
        return "\n".join(map(str, self.forest()))


if __name__ == '__main__':
    ds = EagerObjectSets(10)
    ds.union(3, 4)
    ds.union(4, 9)
    ds.union(0, 7)
    ds.union(3, 5)
    print(ds.find(9, 5))
    print(ds.root)
    print('-----')
    print(ds)
