#
# A variety of commo and useful functions and function combinators.
#
# ruff: noqa: PLR2004


from __future__ import annotations

from typing          import Self, TypeGuard

from collections.abc import Callable, Iterable, Sequence
from functools       import partial, update_wrapper, wraps
from inspect         import signature, Parameter

__all__ = [
    'identity', 'const',
    'pair', 'fst', 'snd', 'with_fst', 'with_snd',
    'triple', 'quadruple', 'swap',
    'is_iterable', 'is_sequence',
    'compose', 'flip', 'fn_eval', 'eval_on',
    'curry', 'uncurry', 'partial2',
    'Function',
]


#
# Helpers
#

def count_pos_parameters(f, *, include_defaults=False):
    "Counts"
    n = 0
    for p in signature(f).parameters.values():
        if (p.kind in {Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD}
           and (include_defaults or p.default == Parameter.empty)):
            n += 1
    return n

def do_curry(fn, n):
    # ATTN: why are _xs and _kw here?? To catch uncurried args? Should they be dropped?
    def curried(x, *_xs, **_kw):
        if n > 1:
            return do_curry(partial(fn, x), n - 1)
        return partial(fn, x)
    return curried

def compose2(after: Callable, before: Callable) -> Callable:
    "Returns the composition of two functions, before then after."
    def composed(*x):
        return after(before(*x))

    return update_wrapper(composed, before, assigned=('__module__', '__annotations__', '__type_params__'))


#
# Useful Functions and Function Factories
#

def identity[A](x: A) -> A:
    "The identity function that returns its input as is."
    return x

def const(x):
    "Returns the constant function that always returns `x`."
    def f(*_y):
        return x
    return f

def pair(x, y):
    "Returns a pair whose components are the arguments."
    return (x, y)

def fst(x_y):
    "Returns the first component of a tuple."
    x, _y, *_ = x_y
    return x

def snd(x_y):
    "Returns the second component of a tuple."
    _x, y, *_ = x_y
    return y

def with_fst(x):
    "Returns a function y :-> (x, y)."
    return lambda y: (x, y)

def with_snd(y):
    "Returns a function x :-> (x, y)."
    return lambda x: (x, y)

def triple(x, y, z):
    "Returns a 3-tuple whose components are the arguments."
    return (x, y, z)

def quadruple(w, x, y, z):
    "Returns a 4-tuple whose components are the arguments."
    return (w, x, y, z)

def swap(xs):
    """Swaps the first two elements of a sequence, returning an object of the same class.

    Works for classes (e.g., tuples and lists) whose constructor takes only an
    interable of the contents.

    """
    return xs.__class__([xs[1], xs[0], *xs[2:]])


#
# Useful Function Combinators
#

def compose(*fs: Callable) -> Callable:
    "Returns the composition of zero or more functions, in order from last applied to first."
    if len(fs) == 0:
        return identity

    if len(fs) == 1:
        return fs[0]

    if len(fs) == 2:
        return compose2(fs[0], fs[1])

    if len(fs) == 3:
        h, g, f = fs

        def composed3(*x):
            return h(g(f(*x)))

        return update_wrapper(composed3, f,
                              assigned=('__module__', '__annotations__', '__type_params__'))

    if len(fs) == 4:
        k, h, g, f = fs

        def composed4(*x):
            return k(h(g(f(*x))))

        return update_wrapper(composed4, f,
                              assigned=('__module__', '__annotations__', '__type_params__'))

    f = compose2(fs[-2], fs[-1])
    for g in fs[-3::-1]:
        f = compose2(g, f)
    return f

def curry(f: Callable, n: int | None = None):
    """Returns a curried version of `f`, taking a single argument.

    If f has p parameters, the curried function will take a single
    argument and return a function of a single parameter p - 1
    successive times before returning the value.

    Parameter `n` indicates the number of parameters to assume,
    so there will be n successive functions of one argument.
    Thus if n <= 1, f is returned as is.

    If n is None, this is automatically determined by inspection
    using the positional parameters without defaults.

    Otherwise, n should be non-negative. The primary use cases are
    if one wants to include arguments with defaults or if you have a
    varargs parameter to be treated as some fixed arity.

    """
    if n is None:
        p = count_pos_parameters(f)
    else:
        p = n

    if p <= 1:
        return f

    return update_wrapper(do_curry(f, p - 1), f)

def uncurry(f):
    """Converts a function of multiple arguments to take a single tuple.

    uncurry : (a -> b -> c) -> (a, b) -> c
              (a -> b -> c -> d) -> (a, b, c) -> d
              and similarly for higher arities.

    """
    def uf(args_tuple):
        return f(*args_tuple)
    return uf

def partial2(f, y):
    "Returns partial evaluation of f with second argument: f(__, y, ...)."
    return lambda x, *args, **kwds: f(x, y, *args, **kwds)

def flip(f):
    "Returns a new function with the order of the first two arguments swapped."
    @wraps(f)  # change attributes
    def f_flipped(x, y, *args, **kwds):
        return f(y, x, *args, **kwds)
    return f_flipped

def fn_eval[A, B](g: Callable[[A], B], a: A) -> B:
    "Evaluates its first argument on its second, returning the results."
    return g(a)

def eval_on[A, B](a: A) -> Callable[[Callable[[A], B]], B]:
    """Partial function evaluation given the first argument.

    Takes a value a: A to use as the first argument and returns a
    function A -> B that evaluates its argument at the given value.

    The returned function accepts optional additional arguments
    (positional and keyword) that are passed to the input
    function.

    Returns a function.

    """
    def eval_on_a(g: Callable[[A], B], *args, **kwds) -> B:
        return g(a, *args, **kwds)

    return eval_on_a


#
# Common checks made easy
#

def is_iterable(x) -> TypeGuard[Iterable]:
    """Tests for an Iterable collection that is not a primitive (str or bytes).

    """
    return isinstance(x, Iterable) and not isinstance(x, (str, bytes))

def is_sequence(x) -> TypeGuard[Sequence]:
    """Tests for an Iterable collection that is not a primitive (str or bytes).

    """
    return isinstance(x, Sequence) and not isinstance(x, (str, bytes))


#
# A Function Wrapper Class to support nice operations
#
# Examples include:
#  - building pipelines
#  - composing optics
#  - predicate objects
#

# To make this an actual profunctor, put Function in its own module
# from .Profunctor     import Profunctor

class Function:
    """A class that wraps functions to support pipe and composition operators.

    Calls are simply delegated to the function. The original function can
    be obtained, if needed, from the .run property.

    Example use cases include:
      - building pipelines
      - composing optics
      - predicate objects


    """
    def __init__(self, f):
        self._fn = f

        # Mimic properties of the underlying function
        self.__doc__ = getattr(f, '__doc__', '')
        self.__name__ = getattr(f, '__name__', 'anonymous')
        self.__qualname__ = getattr(f, '__qualname__', self.__name__)
        self.__module__ = getattr(f, '__module__', None)
        self.__annotations__ = getattr(f, '__annotations__', None)
        self.__defaults__ = getattr(f, '__defaults__', None)
        self.__kwdefaults__ = getattr(f, '__kwdefaults__', None)
        self.__type_params__ = getattr(f, '__type_params__', None)
        self.__dict__ = getattr(f, '__dict__', {}) | self.__dict__

        super().__init__()

    def __str__(self):
        return f'Function {self.__name__}'

    def __call__(self, *args, **kwds):
        return self._fn(*args, **kwds)

    @classmethod
    def as_function(cls, f):
        if isinstance(f, Function):
            return f
        if callable(f):
            return cls(f)
        raise TypeError('as_function can only convert a callable to a Function.')

    @property
    def run(self):  # Controlled access when needed
        return self._fn

    def partial(self, x) -> Self:
        return self.__class__(partial(self._fn, x))

    def partial2(self, y) -> Self:
        return self.__class__(partial2(self._fn, y))

    def __rrshift__(self, other):
        "Pipeline evaluation: value >> f ==> f(value)"
        return self._fn(other)

    def __rshift__(self, other):
        """Pipeline composition: self *then* other.

        f >> g ==> g . f

        Fortunately, because >> is left associative, a chain like

             x >> f >> g >> h

        with a value on the very left will call the __rrshift__
        method that will compute as h(g(f(x)) rather than first
        computing h . g . f and then evaluating. That is the most
        common case and more efficient, but having this method is
        still valuable as it allows separate pipeline style
        composition where a value is not involved, which is nice and
        clear.

        """
        # We cannot just use @ here because other may not be a Function
        if not callable(other):
            return NotImplemented

        if isinstance(other, Function):
            return self.__class__(compose(other._fn, self._fn))
        return self.__class__(compose(other, self._fn))

    def __matmul__(self, other):
        "Function composition: self after other"
        if not callable(other):
            return NotImplemented

        if isinstance(other, Function):
            return self.__class__(compose(self._fn, other._fn))
        return self.__class__(compose(self._fn, other))

    def __rmatmul__(self, other):
        "Function composition: self then other"
        if not callable(other):
            return NotImplemented

        if isinstance(other, Function):
            return self.__class__(compose(other._fn, self._fn))
        return self.__class__(compose(other, self._fn))

    #
    # Profunctor Methods. See optics/* for formal instances.
    #
    # These are treated as protocol methods here without formally
    # declaring a subclass relationship, as this is the more
    # basic type.
    #

    # Profunctor instance via Protocol

    def dimap(self, f, g) -> Self:
        return self.__class__(compose(g, self._fn, f))

    def lmap(self, f) -> Self:
        return self.__class__(compose(self._fn, f))

    def rmap(self, g) -> Self:
        return self.__class__(compose(g, self._fn))

    # Strong instance via Protocol

    def into_first(self):
        def annotated(a_c):
            a, c = a_c
            return (self._fn(a), c)
        return self.__class__(annotated)

    def into_second(self):
        def annotated(c_a):
            c, a = c_a
            return (c, self._fn(a))
        return self.__class__(annotated)
