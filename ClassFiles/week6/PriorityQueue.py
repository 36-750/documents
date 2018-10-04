import queue


class PriorityQueue(object):
    def __init__(self):
        self.q = queue.PriorityQueue()

    def is_empty(self):
        return self.q.empty()

    def extract_highest(self):
        priority, item = self.q.get_nowait()
        return item

    def insert(self, item, priority):
        self.q.push_nowait((-priority, item))  # min queue want max queue

    def peek_highest(self):
        return (self.q.queue[0])[1]  # ATTN:HACK!!!!
