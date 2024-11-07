#
# The Reader Monad
#
# newtype Writer w a = Writer { runWriter : Pair a w }
#
#
from __future__   import annotations

from operator     import itemgetter
from typing       import Callable, Optional, TypeGuard

from .Functor     import Functor
from .Applicative import Applicative
from .Monad       import Monad
from .Monoids     import Monoid, Free
from .Profunctor  import Profunctor
from .Pair        import Pair
from .functions   import compose, identity

__all__ = ['Writer', ]


class Writer[W, A](Monad, Profunctor):
    def __init__(self, value: A, annotation: Optional[W] = None, monoid: Monoid = Free):
        self._value = Pair(value, annotation if annotation is not None else monoid.munit)
        self._monoid = monoid

    #
    # ``Running'' Reader with the given environment
    #

    def run(self) -> Pair[A, W]:
        return self._value

    #
    # Functor, Applicative, and Monad Implementations
    #
 
    def map[B](self, g: Callable[[A], B]) -> Writer[B, W]:
        return Writer(g(self._value[0]), self._value[1], self._monoid)

    @classmethod
    def pure(cls, a):
        return cls(a)   # This isn't ideal. Should pure in general accept an optional use=None that takes a self where needed

    #ATTN

    def map2[B, C](self, g:Callable[[A, B], C], fb: Writer[W, B]) -> Writer[W, C]:
        def mapped2_reader(r):
            a = self.run(r)
            b = fb.run(r)
            return g(a, b)

        return Writer(mapped2_reader)
        
    def bind[B](self, g: Callable[[A], Writer[W, B]]) -> Writer[W, B]:
        def bind_reader(r):
            a = self.run(r)
            return g(a).run(r)

        return Writer(bind_reader)

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

    def dimap[C, S](self, f: Callable[[S], R], g: Callable[[A], C]) -> Writer[S, C]:
        return Writer(compose(g, self._reader, f))

#
# Writer Utilties (esp useful in do blocks)
#

def runWriter[W, A](r: Writer[W, A], env: R) -> A:
    return r.run(env)
