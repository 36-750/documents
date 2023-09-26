# A Generic Traversal Recipe

from typing         import Any

from Graph          import Graph
from TraversalState import TraversalState
from NodeStore      import node_store_factory

def node_noop(graph, node, state):
    return state

def edge_noop(graph, current_node, neighbor_node, state):
    return state

def traverse(
        graph: Graph,
        start,
        acc: Any = None,
        *,
        before_node=node_noop,
        after_node=node_noop,
        on_edge=edge_noop,
        state: TraversalState | None = None,
        node_store='Stack',
        node_priority='priority'
) -> TraversalState:
    if state is None:
        state = TraversalState(graph.nodes, acc)
    remaining_nodes = node_store_factory(node_store)

    time = 0  # Tick the clock with every move
    remaining_nodes.insert(start)

    while not remaining_nodes.is_empty() and not state.finished:
        current_node = remaining_nodes.current

        if state.fresh(current_node):
            # First visit to this node node, mark it
            state.visit(current_node, time)
            time += 1
            if (parent := state.parent_of(current_node)) is not None:
                on_edge(graph, parent, current_node, state)
                if state.finished:
                    break
            before_node(graph, current_node, state)
            if state.finished:
                break

            # Schedule visit to all fresh neighbors
            for neighbor in graph.neighbors(current_node):
                if state.fresh(neighbor):
                    state.node_has_parent(neighbor, current_node)
                    priority = graph.node_properties(neighbor, node_priority, None)
                    remaining_nodes.insert(neighbor, priority)
        elif state.visited(current_node):
            # Neighbors all visited, process this node
            state.process(current_node, time)
            time += 1
            after_node(graph, current_node, state)
            remaining_nodes.remove_current()
        else:
            # The current node is processed, move on
            remaining_nodes.remove_current()

    return state
