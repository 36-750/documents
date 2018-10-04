from TraversalState import TraversalState
from PriorityQueue import PriorityQueue


def noop(graph, node, state):
    pass


def priority(time):
    pass  # e.g., return time  or return -time


def traverse(graph, start, acc, before_node=noop, after_node=noop,
             on_edge=noop, state=None):
    if state is None:
        state = TraversalState(graph.nodes(), acc)

    time = 0
    remaining_nodes = PriorityQueue()
    remaining_nodes.insert(start, priority(time))

    while not remaining_nodes.is_empty() and not state.finished:
        current_node = remaining_nodes.peek_highest()

        if state.fresh(current_node):
            state.visit(current_node, time)
            before_node(graph, current_node, state)

            for neighbor in graph.neighbors(current_node):
                if state.fresh(neighbor):
                    time += 1
                    remaining_nodes.insert(neighbor, priority(time))
        elif state.visited(current_node):
            time += 1
            state.process(current_node, time)
            after_node(graph, current_node, state)
            remaining_nodes.extract_highest()
        else:  # PROCESSED
            remaining_nodes.extract_highest()

    return state
