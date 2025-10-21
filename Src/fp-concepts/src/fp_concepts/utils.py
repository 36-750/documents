#
# Various utilities and useful pieces for the implementation
#
# ruff: noqa: EM102

from __future__   import annotations

from .Applicative import Applicative
from .Monoids     import Monoid
from .Identity    import Identity
from .List        import List
from .Maybe       import Maybe, maybe
from .functions   import compose
from .wrappers    import EffectfulFunction

__all__ = [
    'MissingMonoid', 'Free', 'Collect', 'CollectMaybe', 'eff',
]


#
# Monoid Placeholder that alerts when useda
#

class MissingMonoid(Monoid):
    "No monoid supplied, only causes a problem if it is used."

    def __init__(self, mesg):
        self._mesg = mesg

    @property
    def munit(self):
        raise TypeError(f'A monoid is required here but not supplied: {self._mesg}.')

    def mcombine(self, _x, _y):
        raise TypeError(f'A monoid is required here but not supplied: {self._mesg}.')

    def conforms(self, x) -> bool:
        return False


#
# Other Monoids (avoid circular modules)
#

class FreeM(Monoid):
    "The free monoid: a monoid that collects values in Lists."

    def mcombine(self, x, y):
        return List([*x, *y])

    @property
    def munit(self):
        return List()

    def conforms(self, x) -> bool:
        "Accepts List[Any]"
        return isinstance(x, list)

Free = FreeM()

class CollectM(Monoid):
    "A monoid that collects values in Lists, upcasting non-lists with pure."

    def mcombine(self, x, y):
        mx = x if isinstance(x, List) else List.of(x)
        my = y if isinstance(y, List) else List.of(y)
        return List([*mx, *my])

    @property
    def munit(self):
        return List([])

    def conforms(self, _x) -> bool:
        "Accepts Any"
        return True

Collect = CollectM()

class CollectMaybeM(Monoid):
    "A monoid that collects non-None Maybe values in Lists, unwrapping."

    @staticmethod
    def collect(x):
        return maybe(List(), List.of, x)

    @property
    def munit(self):
        return List()

    def mcombine(self, x, y):
        return [self.collect(x), self.collect(y)]

    def conforms(self, x) -> bool:
        return isinstance(x, Maybe)

CollectMaybe = CollectMaybeM()


def eff(f, *fs, effect=Identity) -> EffectfulFunction:
    """Tags and returns a function of type a -> f b with its Applicative class.

    Parameters

    f - Either a function returning an object that is an instance of Applicative
        or an applicative type constructor. In the former case,
        f has type a -> e b for some applicative functor e equal to that
        given in effect..

    fs - a sequence of functions that are composed with f, with f being
        last in the sequence. This is optional.

    effect [=Identity] - an Applicative type constructor that is used
        to tag the given function. However, if f is itself an
        Applicative type constructor, this is ignored.

    Returns an EffectfulFunction whose return value is the return
    value of the given f.

    Examples:

    + eff(f, g, h, effect=Const)

      Returns f . g . h, where f : a -> Const b

    + eff(Identity, f)

      Returns Identity . f and tagged with Identity

    """
    if isinstance(f, type) and issubclass(f, Applicative):
        return EffectfulFunction(compose(f, *fs), f)

    if not issubclass(effect, Applicative):
        raise TypeError('An effectful function needs at least an Applicative')

    return EffectfulFunction(compose(f, *fs), effect)
