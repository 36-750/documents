#
# A simple implementation of van Laarhoven optics: Lenses, Prisms, Traversals, and Folds
# 
# alias Functor f =>     Lens a b s t = (a -> f b) -> s -> f t
# alias Applicative f => Traversal a b s t = (a -> f b) -> s -> f t
#
# ...
#

from __future__   import annotations

from copy         import copy
from functools    import partial
from operator     import itemgetter

from .Applicative import Applicative, ap
from .Const       import Const, makeConst, runConst 
from .Functor     import lift, map
from .Identity    import Identity
from .List        import List
from .Trees       import complete_btree
from .utils       import Collect
from .functions   import compose, identity, partial2, pair, triple

__all__ = [
    'lens', 'view', 'collect', 'over', 'put',
    'mapped',
    'first', 'second', 'third', 'fourth', 'fifth', 'sixth',
    'both', 'all3', 'all4',
    'chars', 'at', 'last', 'at_', 'last_',
]


#
# Exceptions
#

class LensException(Exception):
    pass


#
# Ergonomic Infrastructure
#

class Pipeable:
    "Class wrapping functions that support pipe and composition operators."

    def __init__(self, f):
        self._f = f

    def __call__(self, *args, **kwds):
        return self._f(*args, **kwds)

    def __rrshift__(self, other):
        return self._f(other)

    def __matmul__(self, other):
        if not callable(other):
            return NotImplemented

        if isinstance(other, Pipeable):
            return Pipeable(compose(self._f, other._f))
        return Pipeable(compose(self._f, other))


#
# Helpers
#

def itemsetter(k):
    def set_at_k(s, b):
        s[k] = b
        return s
    return set_at_k

def itemsetter_immutable(k):
    def set_at_k(s, b):
        t = copy(s)
        t[k] = b
        return t
    return set_at_k


#
# Simplified construction from a getter and a setter
#
# Note that ideally the setter is immutable, like most below,
# but mutable changes are supported (see itemsetter).
#   
#   lens : (s -> a) -> (s -> b -> t) -> (a -> f b) -> s -> f t  
#
def lens(getter, setter):
    """Constructs a lens from a getter and setter function.

    The getter has type s -> a, taking the structure and returning
    the focus.

    The setter has type s -> b -> t, taking the structure and a
    new focus (which may be of a different type) and returns
    a new structure (which may be of a different type).

    """
    def lens_of(a_fb):
        def lens_at(s):
            a = getter(s)
            fb = a_fb(a)
            return map(partial(setter, s), fb)

        return lens_at

    return lens_of

#
# Basic Operations
#

def view(setter):
    return compose(runConst, setter(Const))

def collect(setter, monoid=Collect):
    return compose(runConst, setter(makeConst(monoid)))

def over(setter, f):
    return compose(Identity.run, setter(compose(Identity, f)))

def put(setter, val):
    return compose(Identity.run, setter(lambda _: Identity(val)))


#
# Traversal over Functors
#

def mapped(f):
    "Lens on the values mapped over in a functor."
    return compose(Identity, lift(compose(Identity.run, f)))


#
# Component/Field Accessors
#

def chars(f):
    "Lens that maps over the characters of a string, returning a new string of the same length."
    str_map_f = lambda s: "".join([Identity.run(f(c)) for c in s])
    return compose(Identity, str_map_f)

def char(k):
    "Lens on a specific character of a string."
    def char_set(s, c):
        return s[:k] + c + s[(k+1):]
    return lens(itemgetter(k), char_set)

def at(k):
    """Lens on the element of an indexible object at a specific key.

    This works for any object that can be indexed with a __getitem__
    method, including List, dicts, tuples, and so forth.

    This lens preserves immutability of the list, though it shares
    elements. See `at_` for the mutating version.

    """
    return lens(itemgetter(k), itemsetter_immutable(k))

last = at(-1)

def at_(k):
    """Like at, but mutating and so avoids a shallow copy.

    But note that with pyrsistent immutable vectors and maps,
    this is both more efficient and immutable.

    """
    return lens(itemgetter(k), itemsetter(k))

last_ = at_(-1)

def first(f):
    "Lens on the first element of a tuple."
    def fst(s):
        a, *b = s
        return map(lambda x: (x, *b), f(a))

    return fst

def second(f):
    "Lens on the second element of a tuple."
    def snd(s):
        a, b, *c = s
        return map(lambda x: (a, x, *c), f(b))

    return snd

def third(f):
    "Lens on the third element of a tuple."
    def thd(s):
        a, b, c, *d = s
        return map(lambda x: (a, b, x, *d), f(c))

    return thd

def fourth(f):
    "Lens on the fourth element of a tuple."
    def fth(s):
        a, b, c, d, *e = s
        return map(lambda x: (a, b, c, x, *e), f(d))

    return fth

def fifth(f):
    "Lens on the fifth element of a tuple."
    def fth(s):
        a, b, c, d, e, *g = s
        return map(lambda x: (a, b, c, d, x, *g), f(e))

    return fth

def sixth(f):
    "Lens on the sixth element of a tuple."
    def sth(s):
        a, b, c, d, e, g, *h = s
        return map(lambda x: (a, b, c, d, e, x, *h), f(g))

    return sth

# ATTN: seventh, eighth, ... ?

def both(f):
    "Lens on both elements of a pair."
    def bth(s):
        a, b = s
        return ap(pair, f(a), f(b))

    return bth

def all3(f):
    "Lens on all elements of a 3-tuple."
    def a3(s):
        a, b, c = s
        return ap(triple, f(a), f(b), f(c))

    return a3

def all4(f):
    "Lens on all elements of a 4-tuple."
    def a4(s):
        a, b, c, d = s
        return ap(lambda w, x, y, z: (w, x, y, z), f(a), f(b), f(c), f(d))

    return a4


#
# Other useful Lenses
#

def seq(optic1, optic2):
    """Optic that activates two optics in sequence, from the same input.

    Requires that the two types are compatible and that the
    Applicative both work with is a Monad. This cannot be checked in
    advance, but a Type error is raised if the sequencing goes
    wrong.

    optic1: Monad m => (a -> m b) -> (s -> m t)
    optic2: Monad m => (a -> m b) -> (t -> m u)

    """
    def in_seq(a_fb):
        ell1 = optic1(a_fb)
        ell2 = optic2(a_fb)
        def activate(s):
            ft1 = ell1(s)

            try:
                return ft1.bind(ell2)
            except Exception as e:
                raise TypeError(f'seq optic valid Monad instances with compatible types: {e}')
        return activate

    return in_seq

#
# Optics Utilities
#

def on(predicate, t, f=identity):
    def do_on(x, *_, **__):
        if predicate(x):
            return t(x)
        return f(x)
    return do_on

def is_string(s) -> TypeGuard[str]:
    return isinstance(s, str)

def uppercase(s: str) -> str:
    return s.upper()

def lowercase(s: str) -> str:
    return s.lower()

def capitalize(s: str) -> str:
    return s.capitalize()

#
# Common Optics
#



# ATTN: Example results out of date
if __name__ == '__main__':
    c = compose
    inc = lambda x: x + 1

    # Examples for putting into tests

    collect(at(1))(List.of(1, 2, 3, 4))
    #=> 2
    view(at(1))(List.of(1, 2, 3, 4))
    #=> 2
    view(fourth)((1, 2, 3, 4, 5))
    #=> 4
    view(c(second, first, fourth))([1, [[1, 2, 3, 4, 5], 6, 7]])
    #=> 4

    lens1 = over(c(mapped, first), inc)
     
    examp1 = List.of((1, [2, 3, 4]), (5, [6]), (7, "a"))
    lens1(examp1)
      #=> [(2, [2, 3, 4]), (6, [6]), (8, 'a')]

    over(at(1), inc)(List.of(1, 9, 3, 4))
    #=> [1, 10, 3, 4]
    over(last, inc)(List.of(1, 9, 3, 4))
    #=> [1, 10, 3, 5]
    
    ell1 = List.of(List.of(99, 98), List.of(1, 9, 3, 4), List.of(101, 102, 103))
    over(c(mapped, at(1)), inc)(ell1)
    #=> [[99, 99], [1, 10, 3, 4], [101, 103, 103]]
    
    ell1 = List.of(List.of(99, 98), List.of(1, 9, 3, 4), List.of(101, 102, 103))
    over(c(mapped, last), inc)(ell1)
    #=> [[99, 99], [1, 9, 3, 5], [101, 102, 104]]
    
    put(last, 1000)(List.of(1, 9, 3, 4))
    #=> [1, 9, 3, 1000]
    
    ell1 = List.of(List.of(99, 98), List.of(1, 9, 3, 4), List.of(101, 102, 103), List([9, 8, 7, 6, 5]))
    put(c(mapped, last), -11)(ell1)
    #=> [[99, -11], [1, 9, 3, -11], [101, 102, -11], [9, 8, 7, 6, -11]]
    
    ell1 = List.of(List.of(99, 98), List.of(1, 9, 3, 4), List.of(101, 102, 103), List([9, 8, 7, 6, 5]))
    view(c(mapped, at(1)))(ell1)
    #=> [[98], [9], [102], [8]]
    
    view(c(mapped, last))(ell1)
    #=> [[98], [4], [103], [5]]
    
    view(last)(List.of(1, 9, 3, 4))
    #=> [4]
    
    u = map(lambda k: (list(range(k + 1)), "(" + str(k) + ")"), complete_btree(3))
    print(over(c(mapped, first, last), lambda k: k * 1000)(u))
    # ([0], '(0)')
    # ├─ ([0, 1000], '(1)')
    # │  ├─ ([0, 1, 2, 3000], '(3)')
    # │  │  ├─ ([0, 1, 2, 3, 4, 5, 6, 7000], '(7)')
    # │  │  └─ ([0, 1, 2, 3, 4, 5, 6, 7, 8000], '(8)')
    # │  └─ ([0, 1, 2, 3, 4000], '(4)')
    # │     ├─ ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9000], '(9)')
    # │     └─ ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10000], '(10)')
    # └─ ([0, 1, 2000], '(2)')
    #    ├─ ([0, 1, 2, 3, 4, 5000], '(5)')
    #    │  ├─ ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11000], '(11)')
    #    │  └─ ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12000], '(12)')
    #    └─ ([0, 1, 2, 3, 4, 5, 6000], '(6)')
    #       ├─ ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13000], '(13)')
    #       └─ ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14000], '(14)')
    
    cc = "abcdefghijklmnopqrstuvwxyz"
    view(char(2))(cc)
    #=> 'c'
    collect(char(2), First)(cc)
    #=> 'c'
    
    over(c(mapped, chars), lambda c: c.upper())( List.of(cc, 'uvwxyz', '123@a@ccc', 'thank you ccc') )
    #=> ['ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'UVWXYZ', '123@A@CCC', 'THANK YOU CCC']

    over(c(mapped, chars), on(lambda c: c in 'abcdef', lambda c: c.upper()))( List.of(cc, 'uvwxyz', '123@g@ccc', 'thank you ccc') )
    #=> ['ABCDEFghijklmnopqrstuvwxyz', 'uvwxyz', '123@g@CCC', 'thAnk you CCC']

    put(char(9), "!")(cc)
    #=> 'abcdefghi!klmnopqrstuvwxyz'
    
    over(char(9), lambda c: c.upper())(cc)
    #=> 'abcdefghiJklmnopqrstuvwxyz'

    # Saving for later
    def folded(a_to_Cma, m=Collect):
        def folded_on(s):
            return Const(foldMap(c(runConst, a_to_Cma), s, m=m), monoid=m)
        return folded_on

    def folded(a_to_Cma, m=Collect):
        f = get_effect(a_to_Cma)
        monoid = getattr(f, 'monoid', None) or m or Collect
        def folded_on(s):
            return Const(foldMap(c(runConst, a_to_Cma), s, m=m), monoid=monoid)
        return folded_on

    def folded(a_to_Cma, use={Monoid: Collect}):
        def folded_on(s):
            return Const(foldMap(c(runConst, a_to_Cma), s, m=m), monoid=use[Monoid])
        return folded_on
     
    def foldMapOf(l, f, m=Collect):
        return c(runConst, l(c(makeConst(m), f)))

    def collect(x):
        return maybe(List(), List.of, x)

    collect_maybes = lambda f: folded(c(f, collect))

    view(collect_maybes)( List.of(Some(4), None_(), Some(10), None_(), Some(16)) )
    #=> [4, 10, 16]

    def keep(predicate, transform=identity):
        return lambda f: folded(c(f, lambda x: List.of(transform(x)) if predicate(x) else List()))

    fromSome = lambda x: x._value  # example
    view(keep(isSome, fromSome))( List.of(Some(4), None_(), Some(10), None_(), Some(16)) )
    #=> [4, 10, 16]
    somes = keep(isSome, fromSome)
    view(somes)( List.of(Some(4), None_(), Some(10), None_(), Some(16)) )
    #=> [4, 10, 16]
    x = RoseTree([1, [2, [3], [4], [5]], [6, [7, [8, [9], [10]]]]])
    us = map(lambda x: Some(x) if x % 2 == 0 else None_(), x)
    view(somes)(us)
    #=> [4, 10, 16]

    is_string = lambda s: isinstance(s, str)
    view(keep(is_string))( List.of(4, Some(5), "foo", Some("bar"), "bar", {}, "zap") )
    #=> ['foo', 'bar', 'zap']

    x = RoseTree([1, [2, [3], [4], [5]], [6, [7, [8, [9], [10]]]]])
    ts = map(lambda x: f'u({x})' if x % 2 == 0 else x, x)
    is_string = lambda s: isinstance(s, str)
    view(keep(is_string))(ts)
    #=> ['u(2)', 'u(4)', 'u(6)', 'u(8)', 'u(10)']
    strings = keep(is_string)
    view(strings)(ts)
    #=> ['u(2)', 'u(4)', 'u(6)', 'u(8)', 'u(10)']
