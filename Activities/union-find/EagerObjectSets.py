#!/usr/bin/env python

from collections import defaultdict


class EagerObjectSets:
    def __init__(self, n):
        self._size = n
        self._root = list(range(n))

    @property
    def size(self):
        "Returns the total size of all the sets."
        return self._size

    def representative(self, id1):
        "Returns the representative object associated with an object."
        return self._root[id1]

    def connected(self, id1, id2) -> bool:
        "Are objects id1 and id2 connected?"
        return self._root[id1] == self._root[id2]

    def union(self, id1, id2) -> None:
        "Connect objects id1 and id2."
        root1 = self._root[id1]
        root2 = self._root[id2]
        for id in range(self._size):
            if self._root[id] == root1:
                self._root[id] = root2

    def forest(self):
        """
        Return the current forest as a list of lists.
        Each entry is of the form [root children...].

        """
        disjoint_sets = defaultdict(list)
        for id, root in enumerate(self._root):
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
    print(ds.connected(9, 5))
    print(ds.size)
    print('-----')
    print(ds)
