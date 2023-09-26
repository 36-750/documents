import queue

#
# Unified interface for storing nodes
#

class NodeStore:
    @property
    def current(self):
        ...

    def is_empty(self):
        ...

    def insert(self, item, priority=None):
        ...

    def remove_current(self):
        ...

#
# Basic Stores
#

class Stack(NodeStore):
    def __init__(self):
        self.q = []

    def is_empty(self):
        ...

    # Implement...

    # NodeStore Interface
    @property
    def current(self):
        ...

    def insert(self, item, priority=None):
        ...

    def remove_current(self):
        ...

class Queue(NodeStore):
    def __init__(self):
        self.q = queue.SimpleQueue()
    # Implement

class PriorityQueue(NodeStore):
    def __init__(self):
        self.q = queue.PriorityQueue()

    def is_empty(self):
        "Is the queue empty?"
        return self.q.empty()

    def dequeue(self):
        "Dequeues and returns highest priority item."
        priority, item = self.q.get_nowait()
        return item

    def enqueue(self, item, priority):
        "Inserts an item with a specified priority into the queue."
        self.q.push_nowait((-priority, item))  # min queue want max queue
        return self

    def peek(self):
        "Returns highest priority item without changing the queue."
        return (self.q.queue[0])[1]  # ATTN:HACK!!!!

    # NodeStore Interface
    @property
    def current(self):
        return self.peek()

    def insert(self, item, priority=None):
        priority = priority if priority is not None else 0
        return self.enqueue(item, priority)

    def remove_current(self):
        return self.dequeue()


# What's needed here?

def node_store_factory(type='Stack'):
    # Implement
    if type == 'Stack':
        return Stack()

    if type == 'Queue':
        return Queue()

    return PriorityQueue()
