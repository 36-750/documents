#
# The State Monad
#
# newtype State s a = State { runState : s -> (s, a) }
#
#
from __future__   import annotations

from typing       import Callable, TypeGuard

from .Functor     import Functor
from .Applicative import Applicative
from .Monad       import Monad

__all__ = ['State',]


class GetStateDescriptor:  # Enables class data of type State
    def __get__(self, obj, objtype=None):
        return objtype(lambda s: (s, s))

class State[S, A](Monad):
    def __init__(self, state: Callable[[S], tuple[A, S]]):
        self._state = state

    #
    # Utility Constructors
    #

    get: State[S, S] = GetStateDescriptor()

    @classmethod
    def put[S](cls, state: S) -> State[S, tuple[()]]:
        return cls(lambda _s: ((), state))

    @classmethod
    def derive[S, A](cls, derivation: Callable[[S], A]) -> State[S, A]:
        return cls(lambda s: (derivation(s), s))

    @classmethod
    def modify[S](cls, modifier: Callable[[S], S]) -> State[S, S]:
        return cls(lambda s: ((), modifier(s)))

    #
    # ``Running'' State Transformations
    #

    def run[S, A](self, s: S) -> tuple[A, S]:
        return self._state(s)

    def eval[S, A](self, s: S) -> A:
        return self.run(s)[0]

    def exec[S, A](self, s: S) -> S:
        return self.run(s)[1]

    #
    # Functor, Applicative, and Monad Implementations
    #
 
    def map[S, A, C](self, g: Callable[[A], C]) -> State[S, C]:
        def g_state(s):
            a, s_prime = self._state(s)
            return (g(a), s_prime)

        return State(g_state)

    @classmethod
    def pure(cls, a):
        return cls(lambda s: (a, s))

    def map2[S, A, B, C](self, g:Callable[[A, B], C], fb: State[S, B]) -> State[S, C]:
        def g_state(s):
            a, s1 = self._state(s)
            b, s2 = fb._state(s1)
            return (g(a, b), s2)

        return State(g_state)
        
    def bind[S, A, B](self, g: Callable[[A], State[S, B]]) -> State[S, B]:
        def bind_state(s):
            a, s1 = self._state(s)
            st = g(a)
            return st._state(s1)

        return State(bind_state)

    @classmethod
    def __do__(cls, make_generator):
        def threaded(s):
            generator = make_generator()
            f = lambda result: generator.send(result)
            try:
                x = f(None)
                s1 = s
                while True:
                    a, s1 = x._state(s1)
                    x = f(a)
            except StopIteration as finished:
                return (finished.value, s1)

        return cls(threaded)
