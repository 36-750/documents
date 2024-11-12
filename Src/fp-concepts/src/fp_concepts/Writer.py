#
# The Reader Monad
#
# newtype Writer w a = Writer { runWriter : Pair a w }
#
#
from __future__      import annotations

from operator        import itemgetter
from collections.abc import Callable
from typing          import TypeGuard

from .Functor        import Functor
from .Applicative    import Applicative
from .Maybe          import Maybe, None_, Some, maybe
from .Monad          import Monad
from .Monoids        import Monoid, Free
from .Pair           import Pair, pair
from .functions      import compose, identity

__all__ = ['Writer', 'runWriter', 'execWriter', 'tell']

class WriterBase[A, W](Monad):
    _monoid = Free
 
    def __init__(self, value: A, annotation: W | None = None):
        self._value = Pair(value, annotation or self._monoid.munit)
 
    #
    # ``Running'' Reader with the given environment
    #

    @property
    def run(self) -> Pair[A, W]:
        return self._value
 
    #
    # Functor, Applicative, and Monad Implementations
    #
 
    def map[B](self, g: Callable[[A], B]) -> Writer[B, W]:
        return self.__class__(g(self._value[0]), self._value[1])
 
    @classmethod
    def pure(cls, a):
        return cls(a)

    @classmethod
    def writer(cls, a: A, w: W | None = None):
        return cls(a, w or cls._monoid.munit)

    def map2[B, C](self, g:Callable[[A, B], C], fb: Writer[B, W]) -> Writer[C, W]:
        a1, w1 = self.run
        a2, w2 = fb.run

        return self.__class__(g(a1, a2), self._monoid.mcombine(w1, w2))
        
    def bind[B](self, g: Callable[[A], Writer[W, B]]) -> Writer[W, B]:
        a1, w1 = self.run
        a2, w2 = g(a1).run
 
        return self.__class__(a2, self._monoid.mcombine(w1, w2))
 
    @classmethod
    def __do__(cls, make_generator):
        generator = make_generator()

        def as_writer(x):
            if isinstance(x, WriterBase):
                return x
            if isinstance(x, tuple):
                return cls.writer(x[0], x[1])
            return cls.writer(x)

        f = lambda result: as_writer(generator.send(result))

        try:
            x = f(None)
            log = cls._monoid.munit
            while True:
                a, w = x.run
                log = cls._monoid.mcombine(log, w)
                x = f(a)
        except StopIteration as finished:
            return cls(finished.value, log)
 
    def dimap[C, S](self, f: Callable[[S], R], g: Callable[[A], C]) -> Writer[S, C]:
        return Writer(compose(g, self._reader, f))

writers_registry = {Free: WriterBase}

def make_writer(monoid: Monoid):
    if monoid in writers_registry:
        return writers_registry[monoid]

    class Writer_[A, W](WriterBase):
        _monoid = monoid

    writers_registry[monoid] = Writer_
    return Writer_

def Writer(monoid: Monoid = Free, value: Maybe[A] = None_(), annotation: Maybe[W] = None_()):
    w_class = make_writer(monoid)

    if not value:
        return w_class

    return w_class(value.get(None), annotation.get(w_class._monoid.munit))

#
# Writer Utilties (esp useful in do blocks)
#

def runWriter[W, A](w: Writer[W, A]) -> Pair[A, W]:
    return w.run

def execWriter[W, A](w: Writer[W, A]) -> W:
    return w.run[1]

def tell(w, which=WriterBase):
    monoid = Free
    if isinstance(which, Monoid):
        monoid = which
    elif hasattr(which, '_monoid'):
        monoid = getattr(which, '_monoid')
        
    wc = make_writer(monoid)
    return wc((), w)
