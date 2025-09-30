# Graph CC in python

import numpy as np

class Graph:
    def __init__(self, nodes: list=[], edge: list[tuple]=[]):
        self.nodes = nodes.copy()
        self.edges = set(edges)
        

    def _build_adj_matrix():
        adj_matrix = {node: [], for node in self.nodes}
        
    def add_node(self, node):
        if node not in nodes:
            self.nodes.append(node)


    def add_edge(self, edge:tuple):
        self.edges.add(edge)
        for node in edge:
            self.add_node(node)

    def connected_components(self) -> list[list]:
        union_find = FastObjectSets(len(self.nodes))
        for edge in self.edges:
            index_1 = self.nodes.index(edge[0])
            index_2 = self.nodes.index(edge[1])
            union_find.union(index_1, index_2)
        reps_list = [] * len(self.nodes)
        for node_index in range(0, len(self.nodes)):
            reps_list[union_find.representative(node_index)].append(self.nodes[node_index])
        # connected components are non-empty elements of reps_list
        components = []
        for i in reps_list:
            if len(i) > 0:
                components.append(i)

        #forest = union_find.forest()
        
# g = Graph()
# g.add_edge(1, 3)
#  .add_edge(2, 4)
