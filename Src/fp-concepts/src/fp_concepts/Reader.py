#
# The Reader Monad
#
# newtype Reader r a = Reader { runReader : s -> (s, a) }
#
# ruff: noqa: N802, E731

from __future__ import annotations

from collections.abc import Callable
from operator        import itemgetter

from .Monad       import Monad
from .Profunctor  import Profunctor
from .functions   import compose, identity

__all__ = ['Reader', 'ask', 'ask_for', 'runReader']


class GetReaderDescriptor:  # Enables class data of type Reader
    def __get__(self, obj, objtype=None):
        return objtype(lambda r: r)

class Reader[R, A](Monad, Profunctor):
    def __init__(self, reader: Callable[[R], A]):
        self._reader = reader

    #
    # Utility Constructors
    #

    ask: Reader[R, R] = GetReaderDescriptor()

    #
    # ``Running'' Reader with the given environment
    #

    def run[R, A](self, r: R) -> A:
        return self._reader(r)

    #
    # Functor, Applicative, and Monad Implementations
    #

    def map[B](self, g: Callable[[A], B]) -> Reader[R, B]:
        return Reader(compose(g, self._reader))

    @classmethod
    def pure(cls, a):
        return cls(lambda _r: a)

    def map2[B, C](self, g:Callable[[A, B], C], fb: Reader[R, B]) -> Reader[R, C]:
        def mapped2_reader(r):
            a = self.run(r)
            b = fb.run(r)
            return g(a, b)

        return Reader(mapped2_reader)

    def bind[B](self, g: Callable[[A], Reader[R, B]]) -> Reader[R, B]:
        def bind_reader(r):
            a = self.run(r)
            return g(a).run(r)

        return Reader(bind_reader)

    @classmethod
    def __do__(cls, make_generator):
        def threaded(r):
            generator = make_generator()
            f = lambda result: generator.send(result)
            try:
                x = f(None)
                while True:
                    a = x.run(r)
                    x = f(a)
            except StopIteration as finished:
                return finished.value

        return cls(threaded)

    def dimap[C, S](self, f: Callable[[S], R], g: Callable[[A], C]) -> Reader[S, C]:
        return Reader(compose(g, self._reader, f))

#
# Reader Utilties (esp useful in do blocks)
#

ask = Reader(identity)
ask_for = compose(Reader, itemgetter)

def runReader[R, A](r: Reader[R, A], env: R) -> A:
    return r.run(env)
