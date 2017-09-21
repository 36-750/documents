from collections    import defaultdict
from TraversalState import TraversalState, FRESH, VISITED, PROCESSED

class Graph(object):
    """
    An undirected graph, with optional properties on nodes and edges.
    
    """
    
    def __init__(self):
        self._nodes = {}
        self._edges = {}
        self._adj = defaultdict(set)      # nodes adjacent to node
        self._incident = defaultdict(set) # edges incident on node
        self._next_node_id = 0

    # Encapsulate making an edge in case we change the representation later
    @staticmethod
    def make_edge(node_pair):
        if len(node_pair) > 2 or len(node_pair) == 0:
            raise ValueError("Edge must connect two nodes, or a node to itself.")
        return frozenset(node_pair)

    def size(self):
        return len(self._nodes)

    def nodes(self, pred=None):
        return self._nodes.keys()

    def edges(self, nid=None):
        if nid is None:
            return self._edges.keys()
        else:
            return self._incident[nid]
        # also valid: return [eid for eid in self._edges.keys() if nid in eid]
        # also valid: return [self.make_edge([nid,n2]) for n2 in self._adj[nid]]

    def nodes_of(self, eid):
        return eid

    def edge_of(self, nid1, nid2):
        es = filter(lambda e: nid2 in e, self._incident[nid1])
        if es:
            return es[0]
        else:
            return None

    def neighbors(self, nid, nid2=None):
        if nid2 is None:
            return self._adj[nid]
        else:
            return (nid2 in self._adj[nid])

    def add_node(self, **properties):
        if '_id' in properties:
            nid = properties['_id']
            del properties['_id']
        else:
            while self._next_node_id in self._nodes:
                self._next_node_id += 1
            nid = self._next_node_id
            self._next_node_id += 1

        self._nodes[nid] = properties
        return nid

    def add_edge(self, nid1, nid2, **properties):
        if nid1 not in self._nodes or nid2 not in self._nodes:
            raise KeyError("Nodes are not in the graph")
        eid = self.make_edge([nid1,nid2])
        self._edges[eid] = properties
        self._adj[nid1].add(nid2)
        self._adj[nid2].add(nid1)
        self._incident[nid1].add(eid)
        self._incident[nid2].add(eid)
        return eid

    def get_node_properties(self, nid, key=None, default=None):
        if key is None:
            return self._nodes[nid]
        else:
            return self._nodes[nid].get(key, default)

    def get_edge_properties(self, eid, key=None, default=None):
        if key is None:
            return self._edges[eid]
        else:
            return self._edges[eid].get(key, default)

    def update_node_properties(self, nid, **properties):
        self._nodes[nid].update(properties)
        return self._nodes[nid]

    def update_edge_properties(self, eid, **properties):
        self._edges[eid].update(properties)
        return self._edges[eid]

    def remove_node_properties(self, nid, *properties):
        for p in properties:
            del self._nodes[nid][p]
        return self._nodes[nid]

    def remove_edge_properties(self, eid, *properties):
        for p in properties:
            del self._edges[eid][p]
        return self._edges[eid]

    def dfs(self, start, acc, before_node, after_node, on_edge, ts=None):
        time = 0
        if ts is None:
            ts = TraversalState(self.nodes(), acc)
        stack = [(start, True)]
        processing_edges = (on_edge is not None)
     
        while len(stack) > 0 and not ts.finished:
            current_node, is_node = stack[-1]

            if not is_node:
                from_node, to_node = current_node
                if processing_edges:
                    on_edge(self, from_node, to_node, ts)
                stack.pop()
                continue

            # current_node is now a node id
            state = ts.node_state(current_node)
            if state == FRESH:
                time += 1
                ts.visit(current_node, time)

                if before_node is not None:
                    before_node(self, current_node, ts)
                    if ts.finished:
                        continue

                for neighbor in self.neighbors(current_node):
                    # Edge processed before node
                    if ts.fresh(neighbor):
                        ts.parent[neighbor] = current_node
                        stack.append((neighbor, True))
                    if processing_edges:
                        stack.append(((current_node,neighbor), False))
            elif state == VISITED: 
                time += 1
                ts.process(current_node, time)
                if after_node is not None:
                    after_node(self, current_node, ts)
                stack.pop()
            else: # PROCESSED
                stack.pop()

        return ts    

    def dfs_all(self, acc, before_node, after_node, on_edge):
        ts = None
        for node in self.nodes():
            if ts is None or ts.fresh(node):
                ts = self.dfs(node, acc, before_node, after_node, on_edge, ts)
        return ts

    def bfs(self, start, acc, before_node=None, after_node=None,
            on_edge=None, ts=None):
        processing_edges = (on_edge is not None)
        if ts is None:
            ts = TraversalState(self.nodes(), acc)

        time = 0
        queue = [start]
        ts.visit(start, time) # Invariant: Everything on the queue is VISITED
        if before_node is not None:
            before_node(self, start, ts)  # process early when node VISITED

        while len(queue) > 0 and not ts.finished:
            current_node = queue.pop(0)
            for neighbor in self.neighbors(current_node):
                if processing_edges and not ts.processed(neighbor):
                    on_edge(self, current_node, neighbor, ts)
                    if ts.finished:
                        break
                if ts.fresh(neighbor):
                    time += 1
                    ts.parent[neighbor] = current_node
                    queue.append(neighbor)
                    ts.visit(neighbor, time)
                    if before_node is not None:
                        before_node(self, neighbor, ts)
                        if ts.finished:
                            break
            if ts.finished:
                continue

            time += 1
            ts.process(current_node, time)
            if after_node is not None:
                after_node(self, current_node, ts)

        return ts    

    def bfs_all(self, acc=None, before_node=None, after_node=None, on_edge=None):
        ts = None
        for node in self.nodes():
            if ts is None or ts.fresh(node):
                ts = self.bfs(node, acc, before_node, after_node, on_edge, ts)
        return ts

    def __str__(self):
        def show_edge(graph, from_node, to_node, ts):
            ts.accumulator += ("  %s -- %s;\n" % (from_node, to_node))
        ts = self.bfs_all("graph {\n", on_edge=show_edge)
        return ts.accumulator + "}"
