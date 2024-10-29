from TraversalState import NodeIs

# DFS processing functions to print a traversal history
# Import these functions and use them in dfs and bfs
#
# Example use:
#   print('Traversal History:')
#   g.dfs(start, None, mark_visited, mark_processed, mark_edge)

def mark_visited(gr, n, ts):
    print('  Visiting Node', gr.node_properties(n, 'label') or n)

def mark_processed(gr, n, ts):
    print('  Processing Node', gr.node_properties(n, 'label') or n)

def mark_edge(gr, a, b, ts):
    labels = list(map(lambda n: gr.node_properties(n, 'label') or n, [a, b]))
    labels.sort()
    if ts.edge_state(a, b) == NodeIs.VISITED:
        print('  Visiting Edge', labels)
    else:
        print('  Processing Edge', labels)

def mark_visited_x(gr, n, ts):
    print(ts.accumulator, 'Visiting Node   ',
          gr.node_properties(n, 'label') or n, sep='')
    ts.accumulator += '|'

def mark_processed_x(gr, n, ts):
    ts.accumulator = ts.accumulator[:-1]
    print(ts.accumulator, 'Processing Node ',
          gr.node_properties(n, 'label') or n, sep='')

def mark_edge_x(gr, a, b, ts):
    labels = map(lambda n: gr.node_properties(n, 'label') or n, [a, b])
    labels.sort()
    if ts.edge_state(a, b) == NodeIs.VISITED:
        print(ts.accumulator, 'Visiting Edge   ', labels, sep='')
        ts.accumulator += '|'
    else:
        ts.accumulator = ts.accumulator[:-1]
        print(ts.accumulator, 'Processing Edge ', labels, sep='')
