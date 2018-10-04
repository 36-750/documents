from Graph import Graph
from thistory import mark_visited, mark_processed, mark_edge


# execfile approximating that in python2
def execfile(filename):
    with open(filename) as f:
        code = compile(f.read(), filename, 'exec')
        exec(code, None, None)
# execfile("thistory.py")


g = Graph()

g.add_node(label='A')
g.add_node(label='B')
g.add_node(label='C')
g.add_node(label='D')
g.add_node(label='E')
g.add_node(label='F')

g.add_edge(0, 1)
g.add_edge(0, 4)
g.add_edge(0, 5)
g.add_edge(1, 2)
g.add_edge(2, 3)
g.add_edge(3, 4)

print("Traversal history with BFS:")
ts0 = g.bfs(0, None, mark_visited, mark_processed, mark_edge)

print("\n--------------\n")

print("Traversal history with DFS:")
ts1 = g.dfs(0, None, mark_visited, mark_processed, mark_edge)
