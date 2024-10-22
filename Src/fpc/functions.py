#
# A variety of commo and useful functions and function combinators.
#

from __future__ import annotations

from functools       import partial, update_wrapper
from inspect         import signature, Parameter
from typing          import Callable

__all__ = ['identity', 'const', 'compose', 'curry', 'uncurry',]


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
# Useful Functions, Function Factories, and Function Combinators
#

def identity[A](x: A) -> A:
    "The identity function that returns its input as is."
    return x

def const(x):
    "Returns the constant function that always returns `x`."
    def f(*y):
        return x
    return f

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

def fn_eval[A, B](g: Callable[[A], B], a: A) -> B:
    return g(a)

def pair(x, y):
    return (x, y)

def triple(x, y, z):
    return (x, y, z)
