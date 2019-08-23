#!/usr/bin/env python


class FastObjectSets(object):
    def __init__(self, n):
        self.n = n
        self.parent = list(range(n))
        self.size = [1] * n

    def root(self, id):
        "Find root of the tree to which id is connected"
        while self.parent[id] != id:
            self.parent[id] = self.parent[self.parent[id]]
            id = self.parent[id]
        return id

    def find(self, id1, id2):
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
        base = [[k] for k in range(self.n)]
        roots = [False] * self.n
        for id in range(self.n):
            if self.parent[id] != id:
                base[self.parent[id]].append(base[id])
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
    print(ds.find(9, 5))
    print(ds.parent)
    print('-----')
    print(ds)
