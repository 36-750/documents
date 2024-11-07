#
# A variety of commo and useful functions and function combinators.
#

from __future__ import annotations

from functools       import partial, update_wrapper, wraps
from inspect         import signature, Parameter
from typing          import Callable, Optional

__all__ = [
    'identity', 'const',
    'pair', 'fst', 'snd', 'with_fst', 'with_snd',
    'triple', 'quadruple',
    'compose', 'flip', 'fn_eval', 'eval_on',
    'curry', 'uncurry', 'partial2',
    'Function', 'EffectfulFunction',
    'TypedFunction',  # Provisional
]


#
# Helpers
#

def count_pos_parameters(f, include_defaults=False):
    "Counts"
    n = 0
    for p in signature(f).parameters.values():
        if ((p.kind == Parameter.POSITIONAL_ONLY or p.kind == Parameter.POSITIONAL_OR_KEYWORD)
            and (include_defaults or p.default == Parameter.empty)):
            n += 1
    return n
        
def do_curry(fn, n):
    def curried(x, *xs, **kw):
        if n > 1:
            return do_curry(partial(fn, x), n - 1)
        return partial(fn, x)
    return curried

def compose2(after: Callable, before: Callable) -> Callable:
    "Returns the composition of two functions, before then after."
    def composed(*x):
        return after(before(*x))

    return update_wrapper(composed, before, assigned=('__module__', '__annotations__','__type_params__'))


#
# Useful Functions and Function Factories
#

def identity[A](x: A) -> A:
    "The identity function that returns its input as is."
    return x

def const(x):
    "Returns the constant function that always returns `x`."
    def f(*y):
        return x
    return f

def pair(x, y):
    return (x, y)

def fst(x_y):
    x, _y, *_ = x_y
    return x

def snd(x_y):
    _x, y, *_ = x_y
    return y

def with_fst(x):
    "Returns a function y :-> (x, y)."
    return lambda y: (x, y)

def with_snd(y):
    "Returns a function x :-> (x, y)."
    return lambda x: (x, y)

def triple(x, y, z):
    return (x, y, z)

def quadruple(w, x, y, z):
    return (w, x, y, z)


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
                              assigned=('__module__', '__annotations__','__type_params__'))

    if len(fs) == 4:
        k, h, g, f = fs
        def composed4(*x):
            return k(h(g(f(*x))))

        return update_wrapper(composed4, f,
                              assigned=('__module__', '__annotations__','__type_params__'))

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
# A Function Wrapper Class to support nice operations 
#
# Examples include: 
#  - building pipelines
#  - composing optics
#  - predicate objects
#

class Function:
    """A class that wraps functions to support pipe and composition operators.

    Calls are simply delegated to the function. The original function can
    be obtained, if needed, from the .raw property.

    Example use cases include: 
      - building pipelines
      - composing optics
      - predicate objects


    """
    def __init__(self, f):
        self._fn = f

        # Mimic properties of the raw function object
        self.__doc__ = getattr(f, '__doc__', '')
        self.__name__ = getattr(f, '__name__', 'anonymous')
        self.__qualname__ = getattr(f, '__qualname__', self.__name__)
        self.__module__ = getattr(f, '__module__', None)
        self.__annotations__ = getattr(f, '__annotations__', None)
        self.__defaults__ = getattr(f, '__defaults__', None)
        self.__kwdefaults__ = getattr(f, '__kwdefaults__', None)
        self.__type_params__ = getattr(f, '__type_params__', None)
        self.__dict__ = getattr(f, '__dict__', {}) | self.__dict__

    def __str__(self):
        return f'Function {self.__name__}'

    def __call__(self, *args, **kwds):
        return self._fn(*args, **kwds)

    @property
    def raw(self):  # Controlled access when needed
        return self._fn

    def partial(self, x) -> Function:
        return self.__class__(partial(self._fn, x))

    def partial2(self, y) -> Function:
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

class EffectfulFunction(Function):
    "Class representing a function that produces an Applicative Functor."

    def __init__(self, f, ap: Applicative):
        self._applicative = ap
        super().__init__(f)

    @property
    def effect(self):
        return self._applicative

def get_effect(f) -> Optional[type]:
    "If f is an effectful function returns its Applicative, else None"
    if hasattr(f, 'effect'):
        return f.effect
    return None

# ATTN: Provisional, might be useful with using()
# This is a potential alternative to having a use= argument
# or it can supplement that.
class TypedFunction(Function):
    "Class representing a function with associated types in its signature."

    def __init__(self, f, **types):
        self._types = { k: t for k, t in types.items() }
        super().__init__(f)

    def has(self, associated_type):
        return self._types.get(associated_type, None)
