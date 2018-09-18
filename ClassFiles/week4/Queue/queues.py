#!/usr/bin/env python

import random

from abc import ABC, abstractmethod


class EmptyQueueException(Exception):
    pass


class Queue(object):
    def __init__(self):
        self.queue = []

    def dequeue(self):
        if self.is_empty():
            raise EmptyQueueException("Attempt to dequeue an empty queue")
        return self.queue.pop(0)

    def enqueue(self, obj):
        self.queue.append(obj)
        return self

    def peek(self):
        return self.queue[0]

    def is_empty(self):
        return len(self.queue) == 0


class ArrivalProcess(ABC):
    @property
    @abstractmethod
    def latest(self):
        pass

    @abstractmethod
    def next_event():
        pass


class PoissonProcess(ArrivalProcess):
    def __init__(self, lam):
        self.lam = lam
        self._latest = self.interarrival()

    @property
    def latest(self):
        return self._latest

    def interarrival(self):
        return random.expovariate(self.lam)

    def next_event(self):
        self._latest += self.interarrival()


def find_next_event(events):
    minimum = 1.0e20
    which = None
    index = -1
    for ind, ev in enumerate(events):
        if ev.latest < minimum:
            minimum = ev.latest
            which = ev
            index = ind
    return (which, index)


class MMkGroceryQueue(object):
    """A grocery-style queue with Poisson arrivals and service times."""

    def __init__(self, nqueues, lambda_arrival, lambda_serve):
        self.num_servers = nqueues
        self.lambda_arrival = lambda_arrival
        self.lambda_serve = lambda_serve

        self.servers = [PoissonProcess(lambda_serve) for _ in range(nqueues)]
        self.arrival = [PoissonProcess(lambda_arrival) for _ in range(nqueues)]
        self.station = [None] * nqueues  # entry time into the service station
        self.queues = [Queue() for _ in range(nqueues)]

        self.time = 0.0
        self.served = 0
        self.total_waiting_time = 0.0

    def step(self):
        # ATTN TO BE IMPLEMENTED
        pass
        return self.time

    def run_until(self, time_limit):
        time = self.step()
        while time < time_limit:
            time = self.step()

    def average_waiting_time(self):
        if self.serve > 0:
            return self.total_waiting_time/self.served
        else:
            return None


class MMkBankQueue(object):
    """A bank-style queue with Poisson arrivals and service times."""

    def __init__(self, nservers, lambda_arrivals, lambda_serve):
        self.num_servers = nservers
        self.lambda_arrivals = lambda_arrivals
        self.lambda_serve = lambda_serve

        self.servers = [PoissonProcess(lambda_serve) for _ in range(nservers)]
        self.arrivals = PoissonProcess(lambda_arrivals)
        self.station = [None] * nservers  # entry time into the service station
        self.queue = Queue()

        self.time = 0.0
        self.served = 0
        self.total_waiting_time = 0.0

    def step(self, debug=False):
        next_service, which_s = find_next_event(self.servers)

        # Forward event times for empty servers triggering before next arrival
        while (next_service.latest < self.arrivals.latest and
               self.station[which_s] is None):
            next_service.next_event()
            next_service, which_s = find_next_event(self.servers)

        if self.arrivals.latest < next_service.latest:
            self.time = self.arrivals.latest
            self.arrivals.next_event()

            available = next((i for i in range(self.num_servers)
                              if self.station[i] is None), None)
            if available is None:
                self.queue.enqueue(self.time)
            else:
                self.station[available] = self.time
        else:
            self.time = next_service.latest
            entry_time = self.station[which_s]  # Cannot be None
            waiting_time = self.time - entry_time
            self.served += 1
            self.total_waiting_time += waiting_time

            if self.queue.is_empty():
                self.station[which_s] = None
            else:
                self.station[which_s] = self.queue.dequeue()

        if debug:
            print(self.time)
        return self.time

    def run_until(self, time_limit, debug=False):
        time = self.step()
        while time < time_limit:
            time = self.step()

    def average_waiting_time(self):
        if self.served > 0:
            return self.total_waiting_time/self.served
        else:
            return None

    def report(self):
        print('Served {}, avg wait {}, time {}'.
              format(self.served, self.average_waiting_time(), self.time))


if __name__ == '__main__':
    bank = MMkBankQueue(10, 1.0, 0.001)
    bank.run_until(600.0)
    bank.report()
