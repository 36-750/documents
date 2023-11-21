class BoundedQueue:
    "A queue with bounded size, enqueuing when full dequeues oldest"
    def __init__(self, size):
        self._queue = [None] * (size + 1)
        self._front = 0
        self._back = 0   # Where to put the *next* item
        self.max_size = size

    @property
    def size(self):
        if self._back >= self._front:
            return self._back - self._front
        return self._back + self.max_size + 1 - self._front

    def enqueue(self, item):
        leaving = None
        if self.size == self.max_size:
            leaving = self.dequeue()
        self._queue[self._back] = item
        if self._back == self.max_size:
            self._back = 0
        else:
            self._back += 1
        return leaving

    def dequeue(self):
        if self._back == self._front:
            raise Exception('Cannot dequeue empty queue.')
        item = self._queue[self._front]
        if self._front == self.max_size:
            self._front = 0
        else:
            self._front += 1
        return item

    def peek(self):
        if self._back == self._front:
            return None
        return self._queue[self._front]
