from __future__    import annotations

from typing        import Callable, cast

from ..Either      import Either, Left, Right
from ..Functor     import Functor
from ..Maybe       import Some
from ..Profunctor  import dilift
from ..functions   import Function, compose

from .Choice       import Choice
from .Costrong     import Costrong
from .profunctors  import ForgetM

__all__ = ['Tagged', 'review', 'preview', 'preview_with']

def absurd(*args, **kwargs):
    raise TypeError('Builder is write only; lmap component is a phantom.')


class Tagged[A, B](Choice, Costrong, Functor):
    def __init__(self, b: B):
        self._value = b

    @classmethod
    def run(cls, p):
        return p._value    # pylint: disable=protected-access

    def map[C](self, g: Callable[[B], C]) -> Tagged[A, C]:
        return Tagged(g(self._value))

    def dimap[C, D](self, f: Callable[[C], A], g: Callable[[B], D]) -> Tagged[C, D]:
        return cast(Tagged[C, D], Tagged(g(self._value)))

    def into_left[C](self) -> Tagged[Either[A, C], Either[B, C]]:
        return cast(Tagged[Either[A, C], Either[B, C]], Tagged(Left(self._value)))

    def into_right[C](self) -> Tagged[Either[C, A], Either[C, B]]:
        return cast(Tagged[Either[C, A], Either[C, B]], Tagged(Right(self._value)))

    def unfirst(self) -> Tagged[A, B]:
        return cast(Tagged[A, B], Tagged(self._value[0]))   # type: ignore

    def unsecond(self) -> Tagged[A, B]:
        return cast(Tagged[A, B], Tagged(self._value[1]))   # type: ignore

def review(opt):
    def reviewed(b):
        return Tagged.run(opt(Tagged(b)))

    return Function(reviewed)

def preview_with(opt, f):
    def previewed(s):
        h = ForgetM.run(opt(ForgetM(compose(Some, f))))
        return h(s)

    return Function(previewed)

def preview(opt):
    def previewed(s):
        h = ForgetM.run(opt(ForgetM(Some)))
        return h(s)

    return Function(previewed)

def builder[B, T](f: Callable[[B], T]):
    return dilift(cast(Callable[[T], B], absurd), Function(f))
