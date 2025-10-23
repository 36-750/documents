import math

from typing import Callable

from lazy   import LazyIteration, LazyStream, iterate, split_at, take

#
# Selectors
#

def absolute(tol, lazy: LazyIteration):
    first2, rest = split_at(2, lazy)
    a0, a1 = first2

    if abs(a1 - a0) <= tol:
        return a1

    return absolute(tol, rest.cons(a1))

def relative(tol, lazy: LazyIteration):
    first2, rest = split_at(2, lazy)
    a0, a1 = first2

    if abs(a1 / a0 - 1) <= tol:
        return a1

    return relative(tol, rest.cons(a1))

def within(rel_tol, abs_tol, lazy: LazyIteration):
    first2, rest = split_at(2, lazy)
    a0, a1 = first2

    if math.isclose(a0, a1, rel_tol=rel_tol, abs_tol=abs_tol):
        return a1

    return within(abs_tol, rel_tol, rest.cons(a1))

def within_by[A](close: Callable[[A, A], bool], lazy: LazyIteration[A]):
    first2, rest = split_at(2, lazy)
    a0, a1 = first2

    if close(a0, a1):
        return a1

    return within_by(close, rest.cons(a1))


#
# Newton-Raphson Square Roots
#

def sqrt_recurrence(start: float) -> Callable[[float], float]:
    def rec(a):
        return 0.5 * (a + start / a)

    return rec

def a_sqrt(x, init=1, tol=1e-7):
    return absolute(tol, iterate(sqrt_recurrence(x), init))

def r_sqrt(x, init=1, tol=1e-7):
    return relative(tol, iterate(sqrt_recurrence(x), init))

def w_sqrt(x, init=1, rel_tol=1e-7, abs_tol=1e-7):
    return within(rel_tol, abs_tol, iterate(sqrt_recurrence(x), init))

#
# Taylor Series
#

def taylor_close(rel_tol=1e-7, abs_tol=1e-7):
    "Points are represented by (approx, (x - x_0)**n/n!, n)."
    def small_dist(x, y):
        return math.isclose(x[0], y[0], rel_tol=rel_tol, abs_tol=abs_tol)

    return small_dist

def w_exp(x, rel_tol=1e-9, abs_tol=0.0):
    close = taylor_close(rel_tol, abs_tol)

    def series(state):
        current, term, n = state
        term_prime = term * x / (n + 1)
        return (current + term_prime, term_prime, n + 1)

    return within_by(close, iterate(series, (1, 1, 0)))[0]

def w_sin(x, rel_tol=1e-9, abs_tol=0.0):
    close = taylor_close(rel_tol, abs_tol)
    x_red = x % (2 * math.pi)

    def series(state):
        current, term, sign, tn_m_1 = state
        term_prime = term * x_red * x_red / ((tn_m_1 + 1) * (tn_m_1 + 2))
        return (current - sign * term_prime, term_prime, -sign, tn_m_1 + 2)

    return within_by(close, iterate(series, (x_red, x_red, 1, 1)))[0]

def w_cos(x, rel_tol=1e-9, abs_tol=0.0):
    close = taylor_close(rel_tol, abs_tol)
    x_red = x % (2 * math.pi)

    def series(state):
        current, term, sign, tn_m_1 = state
        term_prime = term * x_red * x_red / ((tn_m_1 + 1) * (tn_m_1 + 2))
        return (current - sign * term_prime, term_prime, -sign, tn_m_1 + 2)

    return within_by(close, iterate(series, (1, 1, 1, 0)))[0]


#
# Derivatives
#

def div_diff(f, x):
    def _diff(h):
        return (f(x + h) - f(x)) / h

    return _diff

def halve(x):
    return x / 2

def derivative(f, x, h_0):
    hs = iterate(halve, h_0)
    # dv = LazyStream(lambda: next(hs), hs.all_realized())
    return hs.to_stream().map(div_diff(f, x))

def order(seq):
    a, b, c = take(3, seq)
    return max(1, round(math.log2((a - c) / (b - c) - 1)))

# def sharpen(n, seq: LazyStream):
#     ab, rest = split_at(2, seq)
#     a, b = ab
#     two_n = 2 ** n
#     adjust = (b * two_n - a) / (two_n - 1)
#     tail = rest.cons(b)
#
#     # sharpen(n, tail)
#     pass
