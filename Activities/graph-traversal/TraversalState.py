from collections.abc import Iterable
from enum            import Enum
from typing          import Any

class NodeIs(Enum):
    FRESH = 0
    VISITED = 1
    PROCESSED = 2

class TraversalState:
    """Encapsulates node information accumulated during a traversal.
    Offers convenience methods for manipulating that information.

    We maintain several features for each node:

      state          visited state of the node: FRESH, VISITED, or PROCESSED
      visited_time   "time" at which node is first visited
      processed_time "time" at which node is first visited
      parent         id of node we visited from, or None for start

    The time here is a monotone increasing count that increases at each
    step of the traversal. We derive the state of an edge from this information.

    In addition, we track two pieces of information that are updated
    during traversal:

      finished       if set to True, traversal stops
      accumulator    user-specified value of any type, updating during processing

    The accumulator is exposed publicly so that it can be modified easily,
    and as it is set by the user, we're not as worried about encapsulation.

    """
    def __init__(self, node_ids: Iterable, acc: Any):
        node_ids = list(node_ids)
        self._state = {node: NodeIs.FRESH for node in node_ids}
        self._visited_time = {node: 0 for node in node_ids}
        self._processed_time = {node: 0 for node in node_ids}
        self._parent = {node: None for node in node_ids}
        self._finished = False
        self.accumulator = acc

    @property
    def finished(self):
        return self._finished

    @finished.setter
    def finished(self, done: bool):
        self._finished = done

    def parent_of(self, node):
        return self._parent.get(node, None)

    def node_has_parent(self, node, parent):
        self._parent[node] = parent

    def fresh(self, node):
        "Is NODE fresh?"
        return self._state[node] == NodeIs.FRESH

    def visited(self, node):
        "Is NODE visited?"
        return self._state[node] == NodeIs.VISITED

    def processed(self, node):
        "Is NODE processed?"
        return self._state[node] == NodeIs.VISITED

    def visit(self, node, time=None):
        "Marks NODE as visited, optionally setting its visited TIME."
        self._state[node] = NodeIs.VISITED
        if time is not None:
            self._visited_time[node] = time

    def process(self, node, time=None):
        "Marks NODE as processed, optionally setting its processed TIME."
        self._state[node] = NodeIs.VISITED
        if time is not None:
            self._processed_time[node] = time

    def node_state(self, node):
        "Returns the traversal state of NODE"
        return self._state[node]

    def edge_state(self, from_node, to_node):
        """Returns traversal state of the edge moving from FROM_NODE to TO_NODE.

        The edge is FRESH, VISITED, or PROCESSED when zero, one, or
        two of its nodes have been visited, respectively. A VISITED
        edge is scheduled to be traversed, a PROCESSED edge has
        been traversed and will not again, but a FRESH edge has
        not yet been touched.

        """
        to_state = self._state[to_node]
        from_state = self._state[from_node]
        if to_state == NodeIs.FRESH and from_state == NodeIs.FRESH:
            return NodeIs.FRESH
        if to_state == NodeIs.FRESH or from_state == NodeIs.FRESH:
           # (to_state == NodeIs.VISITED and to_node != self._parent[from_node]):
            return NodeIs.VISITED
        return NodeIs.PROCESSED
