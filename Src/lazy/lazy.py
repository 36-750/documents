from __future__ import annotations
from copy       import deepcopy
from typing     import Callable, Self, cast


#
# Helpers
#

def identity(x):
    return x

def compose(f, g):
    "Returns the composition f after g, for unary functions f."
    def f_after_g(*args, **kwargs):
        return f(g(*args, **kwargs))

    return f_after_g

class Chunked[A]:
    "Marker for function that returns a list of values in one chunk."
    def __init__(self, f: Callable[..., list[A]]):
        self._fn = f

    def __call__(self, *args, **kwargs):
        return self._fn(*args, **kwargs)

    @property
    def raw(self):
        return self._fn

#
# Abstract Base Class
#

class BaseLazyList[A]:
    def __init__(self, f: Callable, init: list[A] = []):
        self.realized: list[A] = init[:]  # Copy in case of default
        self.pushback: list[A] = []       # Stored in reverse order
        self.waiting: list[A] = []
        self.seen = len(init)
        self.original_fn = f

    def __str__(self):
        so_far = []
        so_far.extend(reversed(self.pushback))
        so_far.extend(self.realized)
        return "[" + ", ".join(map(str, so_far)) + ", ...]"

    def __repr__(self):
        so_far = []
        so_far.extend(reversed(self.pushback))
        so_far.extend(self.realized)
        return str(self.__class__.__name__) + "(" + str(self.original_fn) +\
            ", init=[" + ", ".join(map(str, so_far)) + "])"

    def __next__(self):
        # This must be overridden
        raise StopIteration

    def cons(self, a: A) -> Self:
        self.pushback.append(a)
        self.seen += 1
        return self

    def split_at(self, n) -> tuple[list[A], Self]:
        if n <= 0:
            return ([], self)

        m = self.seen
        if m <= n:
            # Realize the needed values (this could be more efficiently chunked)
            # Do one more than needed so dropped has at least one realized
            _ = [next(self) for _ in range(n - m + 1)]

        p = len(self.pushback)
        head: list[A] = []
        dropped = self.__class__(self.original_fn, init=[self.pushback[-1] if p > 0 else self.realized[0]])

        if p > 0:
            head.extend(reversed(self.pushback[(p - min(p, n)):]))
        if p >= n:
            dropped.realized = list(reversed(self.pushback[:(p - n)]))
            dropped.realized.extend(self.realized)
        else:
            head.extend(self.realized[:(n - p)])
            dropped.realized = self.realized[(n - p):]
        dropped.seen = max(m - n, 0)

        return (head, dropped)

    def copy(self):
        cp = self.__class__(self.original_fn, init=[self.pushback[-1] if self.pushback else self.realized[0]])
        cp.realized = deepcopy(self.realized)
        cp.pushback = deepcopy(self.pushback)
        cp.waiting = deepcopy(self.waiting)
        cp.seen = self.seen

        return cp

    def all_realized(self) -> list[A]:
        all_seen = list(reversed(self.pushback))
        all_seen.extend(self.realized)
        return all_seen

#
# General Lazy Sequence, the supplied code is nullary
#

class LazyList[A](BaseLazyList[A]):
    def __init__(self, f: Callable[[], A] | Chunked[A], init: list[A]):

        # Stored function always A -> A and handles internal state
        if isinstance(f, Chunked):
            def my_fn():
                new_items = f()
                if not new_items:
                    raise StopIteration  # No values, then stop if iterating

                next_item = new_items[0]
                self.realized.append(new_items[0])
                self.waiting.extend(new_items[1:])
                self.seen += 1

                return next_item
        else:
            def my_fn():
                next_item = f()
                self.realized.append(next_item)
                self.seen += 1
                return next_item

        self.function = my_fn
        super().__init__(f, init)

    def __next__(self):
        if self.waiting:
            next_item = self.waiting[0]
            self.realized.append(next_item)
            self.waiting = self.waiting[1:]
            self.seen += 1
            return next_item

        return self.function()

    def map[B](self, f: Callable[[A], B]) -> LazyList[B]:
        mapped = self.__class__(compose(f, self.original_fn),
                                init=[self.pushback[-1] if self.pushback else self.realized[0]])
        mapped.realized = list(map(f, self.realized))    # type: ignore
        mapped.pushback = list(map(f, self.pushback))    # type: ignore
        mapped.waiting = list(map(f, self.waiting))      # type: ignore
        mapped.seen = self.seen

        return cast(LazyList[B], mapped)


#
# Iteration
#

class LazyIteration[A](BaseLazyList[A]):
    def __init__(self, f: Callable[[A], A] | Chunked[A], init: list[A]):
        if not init:
            raise ValueError('LazyIteration requires at least one initial value.')

        # Stored function always A -> A and handles internal state
        if isinstance(f, Chunked):
            def my_fn(a: A):
                new_items = f(a)
                if not new_items:
                    raise StopIteration  # No values, then stop if iterating

                next_item = new_items[0]
                self.realized.append(new_items[0])
                self.waiting.extend(new_items[1:])
                self.seen += 1

                return next_item
        else:
            def my_fn(a: A):
                next_item = f(a)
                self.realized.append(next_item)
                self.seen += 1
                return next_item

        self.function = my_fn
        super().__init__(f, init)

    def __next__(self):
        if self.waiting:
            next_item = self.waiting[0]
            self.realized.append(next_item)
            self.waiting = self.waiting[1:]
            self.seen += 1
            return next_item

        return self.function(self.realized[-1])

    def to_stream(self) -> LazyList[A]:
        hs = self.copy()
        return LazyList(lambda: next(hs), hs.all_realized())

def iterate[A](f: Callable[[A], A], x: A) -> LazyIteration[A]:
    return LazyIteration(f, init=[x])

def cons(x, lazy: BaseLazyList):
    return lazy.copy().cons(x)

def take(n, lazy: BaseLazyList):
    head, _ = lazy.split_at(n)
    return head

def drop(n, lazy: BaseLazyList):
    _, tail = lazy.split_at(n)
    return tail

def split_at(n, lazy: BaseLazyList):
    return lazy.split_at(n)
