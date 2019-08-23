(FRESH,VISITED,PROCESSED) = 0, 1, 2

class TraversalState(object):
    """
    Encapsulates node information accumulated during a traversal,
    with convenience methods for manipulating that information.

    The following data fields are intended to be accessed directly.

      state          dict mapping node id to FRESH, VISITED, or PROCESSED
      visited_time   dict mapping node id to its visited time
      processed_time dict mapping node id to its processed time
      parent         dict mapping node id to its parent id, or None for the start
      finished       if set to True, dfs search stops
      accumulator    user-specified value of any type, updating during processing

    The edgeState and nodeState methods are also notably useful.

    """
    def __init__(self, node_ids, acc):
        self._state = { node: FRESH for node in node_ids }
        self.visited_time = { node: 0 for node in node_ids }
        self.processed_time = { node: 0 for node in node_ids }
        self.parent = { node: None for node in node_ids }
        self.finished = False
        self.accumulator = acc

    def fresh(self, node):
        "Is NODE fresh?"
        return self._state[node] == FRESH

    def visited(self, node):
        "Is NODE visited?"
        return self._state[node] == VISITED

    def processed(self, node):
        "Is NODE processed?"
        return self._state[node] == PROCESSED

    def visit(self, node, time=None):
        "Marks NODE as visited, optionally setting its visited TIME."
        self._state[node] = VISITED
        if time is not None:
            self.visited_time[node] = time

    def process(self, node, time=None):
        "Marks NODE as processed, optionally setting its processed TIME."
        self._state[node] = PROCESSED
        if time is not None:
            self.processed_time[node] = time

    def node_state(self, node):
        "Returns the state of NODE"
        return self._state[node]
    
    def edge_state(self, from_node, to_node):
        """
        Return the traversal state of the edge moving from FROM_NODE to TO_NODE.
        The edge is FRESH, VISITED, or PROCESSED when zero, one, or two
        of its nodes have been visited, respectively.
     
        """
        to_state = self._state[to_node]
        from_state = self._state[from_node]
        if to_state == FRESH and from_state == FRESH:
            return FRESH
        if to_state == FRESH or \
           (to_state == VISITED and to_node != self.parent[from_node]):
            return VISITED
        else:
            return PROCESSED
        
