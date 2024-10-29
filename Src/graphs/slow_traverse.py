from Graph          import Graph
from TraversalState import TraversalState
from NodeStore      import node_store_factory

# Graph -> NodeId -> TraversalState -> TraversalState
def node_noop(graph, node, state):
    return state

def traverse(
        graph: Graph,
        start: NodeId,
        acc: Any,
        *,
        before_node=node_noop,
        after_node=node_noop,
        state: TraversalState | None = None,
        node_store='Stack',
        node_priority='priority'
) -> TraversalState:
    if state is None:
        state = TraversalState(graph.nodes, acc)
    remaining_nodes = node_store_factory(node_store)

    priority = graph.node_properties(start, node_priority, None)
    remaining_nodes.insert(start, priority)

    while not remaining_nodes.is_empty():
        current_node = remaining_nodes.current_node

        if state.fresh(current_node):
            state.visit(current_node, 0)
            before_node(graph, current_node, state)

            for neighbor in graph.neighbors(current_node):
                if state.fresh(neighbor):
                    state.node_has_parent(neighbor, current_node)
                    priority = graph.node_properties(neighbor, node_priority, None)
                    remaining_nodes.insert(neighbor, priority)
        elif state.visited(current_node):
            state.process(current_node, 0)
            after_node(graph, current_node, state)
            remaining_nodes.remove_current()
        else:
            remaining_nodes.remove_current()

    return state
