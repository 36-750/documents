from __future__   import annotations

from collections.abc import MutableSequence, Sequence
from typing          import Callable, cast

from .Optic  import Optic, OpticIs
from .Strong import Strong

__all__ = [
    'Lens',
    'lens',
    'at',
    't_0',
    't_1',
    't_2',
    't_3',
    't_4',
    't_5',
    't_6',
    't_7',
    't_8',
    't_9',
]


class Lens[A, B, S, T](Optic):
    def __init__(self, sab_to_sst: Callable[[Strong[A, B]], Strong[S, T]]):
        self._sab_to_sst: Callable[[Strong[A, B]], Strong[S, T]] = sab_to_sst
        super().__init__(sab_to_sst, OpticIs.LENS)

def lens[A, B, S, T](
        getter: Callable[[S], A],
        setter: Callable[[S, B], T]
) -> Optic:
    def the_lens(p_ab: Strong[A, B]) -> Strong[S, T]:
        p_ac_bc: Strong[tuple[A, S], tuple[B, S]] = p_ab.into_first()
        p = p_ac_bc.dimap(lambda s: (getter(s), s),
                          lambda b_s: setter(b_s[1], b_s[0]))
        return cast(Strong[S, T], p)

    return Optic(the_lens, OpticIs.LENS)

# ATTN: Not really needed, right?
def simple_lens[A, S](
        getter: Callable[[S], A],
        setter: Callable[[S, A], S]
) -> Optic:
    def the_lens(p_ab: Strong[A, A]) -> Strong[S, S]:
        p_ac_bc: Strong[tuple[A, S], tuple[A, S]] = p_ab.into_first()
        p = p_ac_bc.dimap(lambda s: (getter(s), s),
                          lambda b_s: setter(b_s[1], b_s[0]))
        return cast(Strong[S, S], p)

    return Optic(the_lens, OpticIs.LENS)


#
# Some commonly used lenses
#

def at(*idx: int | slice):
    "ATTN"
    # Handling slices introduces unneeded complexity, but it fun and convenient
    if len(idx) == 1 and isinstance(idx[0], int):
        k = idx[0]

        def _at_getter(xs: Sequence):
            return xs[k]

        def _at_setter(xs: Sequence, v):
            xs_prime: MutableSequence = cast(MutableSequence, xs[:])
            xs_prime[k] = v
            return xs_prime
    else:
        def _at_getter(xs: Sequence):
            ys: MutableSequence = []
            for i in idx:
                if isinstance(i, slice):
                    ys.extend(xs[i])
                else:
                    ys.append(xs[i])

            return ys

        def _at_setter(xs: Sequence, v):
            xs_prime: MutableSequence = cast(MutableSequence, xs[:])
            m = 0
            vlen = len(v)
            for i in idx:
                if isinstance(i, slice):
                    n = len(xs_prime[i])
                    m_prime = m + n
                    if vlen >= m_prime:
                        xs_prime[i] = v[m:m_prime]
                    elif vlen > m:
                        u = xs_prime[i]
                        u[:(vlen - m)] = v[m:]
                        xs_prime[i] = u
                else:
                    n = 1
                    xs_prime[i] = v[m]
                m += n
            return xs_prime

    return lens(_at_getter, _at_setter)

# # A super simple version
# def at(k: int):
#     return lens(lambda xs: xs[k], lambda xs, val: xs[:k] + [val] + xs[(k + 1):])  # type: ignore

t_0 = lens(lambda xs: xs[0], lambda xs, x_prime: (x_prime, *xs[1:]))            # type: ignore
t_1 = lens(lambda xs: xs[1], lambda xs, x_prime: (xs[0], x_prime, *xs[2:]))     # type: ignore
t_2 = lens(lambda xs: xs[2], lambda xs, x_prime: (*xs[:2], x_prime, *xs[3:]))   # type: ignore
t_3 = lens(lambda xs: xs[3], lambda xs, x_prime: (*xs[:3], x_prime, *xs[4:]))   # type: ignore
t_4 = lens(lambda xs: xs[4], lambda xs, x_prime: (*xs[:4], x_prime, *xs[5:]))   # type: ignore
t_5 = lens(lambda xs: xs[5], lambda xs, x_prime: (*xs[:5], x_prime, *xs[6:]))   # type: ignore
t_6 = lens(lambda xs: xs[6], lambda xs, x_prime: (*xs[:6], x_prime, *xs[7:]))   # type: ignore
t_7 = lens(lambda xs: xs[7], lambda xs, x_prime: (*xs[:7], x_prime, *xs[8:]))   # type: ignore
t_8 = lens(lambda xs: xs[8], lambda xs, x_prime: (*xs[:8], x_prime, *xs[9:]))   # type: ignore
t_9 = lens(lambda xs: xs[9], lambda xs, x_prime: (*xs[:9], x_prime, *xs[10:]))  # type: ignore
