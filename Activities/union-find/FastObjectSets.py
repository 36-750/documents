#!/usr/bin/env python


class FastObjectSets:
    def __init__(self, n):
        self._size = n
        self._parent = list(range(n))
        self._sizes = [1] * n

    @property
    def size(self):
        return self._size

    def representative(self, id):
        "Find root of the tree to which id is connected"
        while self._parent[id] != id:
            self._parent[id] = self._parent[self._parent[id]]
            id = self._parent[id]
        return id

    def connected(self, id1, id2):
        "Are objects id1 and id2 connected?"
        # ATTN:IMPLEMENT Same as before

    def union(self, id1, id2):
        "Connect objects id1 and id2."
        # ATTN:IMPLEMENT: check and update sizes

    def forest(self):
        """
        Return the current forest as a list of lists.
        Each entry is of the form [root [children]...].

        """
        base = [[k] for k in range(self._size)]
        roots = [False] * self._size
        for id in range(self._size):
            if self._parent[id] != id:
                base[self._parent[id]].append(base[id])
            else:
                roots[id] = True
        return [tree for id, tree in enumerate(base) if roots[id]]

    def __str__(self):
        return "\n".join(map(str, self.forest()))


if __name__ == '__main__':
    ds = FastObjectSets(10)
    ds.union(3, 4)
    ds.union(4, 9)
    ds.union(0, 7)
    ds.union(3, 5)
    ds.union(7, 9)
    print(ds.connected(9, 5))
    print(ds._parent)
    print('-----')
    print(ds)
