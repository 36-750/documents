from __future__   import annotations

import re

from enum         import StrEnum

from ..functions  import Function, compose

__all__ = ['Optic', 'OpticIs', 'OpticTypeError', 'composed_optic_is', 'cast_optic_is']

class OpticTypeError(Exception):
    "Exception that indicates incompatible optic types for cast or composition."

class OpticIs(StrEnum):
    "Optic types"
    ISO = "Iso"
    LENS = "Lens"
    PRISM = "Prism"
    SETTER = "Setter"
    GETTER = "Getter"
    REVIEW = "Review"
    AFFINE_TRAVERSAL = "Affine Traversal"
    TRAVERSAL = "Traversal"
    AFFINE_FOLD = "Affine Fold"
    FOLD = "Fold"

class Optic(Function):
    """ATTN:FILL in here

    """
    # ATTN: Add index type here as optional argument with NoIx = Unit
    def __init__(self, f, o_type: OpticIs, **data):
        self._type = o_type
        self._data = data    # ATTN: needed? how used? e.g., Monoid to use etc.
        super().__init__(f)

    def __str__(self):
        return f'{_optic_desc(self._type)} Optic {repr(self)}'

    # ATTN: add data accessor, e.g., to wrap with the right Monoid

    def __matmul__(self, other):
        "Composes two optics."
        if isinstance(other, Optic):
            opt_type = composed_optic_is(self._type, other._type)
            opt_data = self._data | other._data

            # ATTN: Need to standardize the args to the non-trivial optic classes
            # We will have them take **data in second argument but not a type
            # and instead of .__class__ get the class from the composition
            # return self.__class__(compose(self._fn, other._fn), opt_type, **opt_data)
            return self.__class__(compose(self._fn, other._fn), opt_type)

        if callable(other):  # Viable case?
            return self.__class__(compose(self._fn, other), self._type, **self._data)

        return NotImplemented

    def __rmatmul__(self, other):
        "Composes two optics."
        if callable(other):  # Viable case?
            return self.__class__(compose(other, self._fn), self._type, **self._data)
        return NotImplemented

    def cast_as(self, o_type: OpticIs):
        return Optic(self._fn, cast_optic_is(self._type, o_type), **self._data)

def _optic_desc(o_type: OpticIs, start_sentence=True) -> str:
    a = 'A' if start_sentence else 'a'
    n = ''
    if re.match(r'[AEIOU]', o_type.name, re.IGNORECASE):
        n = 'n'
    return f'{a}{n} {o_type.name}'

def composed_optic_is(opt1: OpticIs, opt2: OpticIs) -> OpticIs:
    "Returns the type of a composed optics with given constituent types."
    # ATTN: This is just an example, need more systematic approach
    if opt1 == OpticIs.LENS and opt2 == OpticIs.PRISM:
        return OpticIs.ISO

    return opt1  # ATTN: THIS IS WRONG

def cast_optic_is(opt_from: OpticIs, opt_to: OpticIs) -> OpticIs:
    """Checks compatibility of optic types, raising an error if invalid.

    Returns the target type, which will then be valid.

    """
    # ATTN: This is just an example, need more systematic approach
    if opt_to == OpticIs.LENS and opt_from == OpticIs.TRAVERSAL:
        # ATTN: OpticTypeError to be caught by operation to give
        # a better error message
        raise OpticTypeError('cannot convert a traversal to a lens')

    return opt_to
