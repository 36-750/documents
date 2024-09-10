from typing    import Protocol, runtime_checkable

#
# Monoids
#
# While we have several choices, including having monoid objects *wrap*
# values, here we use monoid objects as *interpreters* of values.
# This eliminates one level of wrapping/unwrapping as we process the data.
#
# Each monoid has an `munit` property, an `mdot` method, and a label,
# but we exclude `label` from the protocol. We also include
# a `conforms` method in our implementations for checking valid inputs
# but we do not use it inside mdot, say, or include it in the protocol.
#
# For those who like typed Python, we could define a TypeVar A
# and then have Monoid inherit from Protocol[A]. I'm leaving that
# off here for simplicity.
#

class Semigroup(Protocol):   # You could put this in Monoid, but this doesn't hurt
    def mdot(self, x, y): ...

@runtime_checkable
class Monoid(Semigroup, Protocol):
    @property
    def munit(self): ...

    @property
    def label(self):
        return self.__class__.__name__.rstrip('M')

    def __str__(self):
        return str(self.label)

    def __repr__(self):
        return f'{self.__class__.__name__}()'

def munit(m):
    return m.munit

def mdot(m, x, y):
    return m.mdot(x, y)


# Here's the Sum definition from the text

class SumM(Monoid):
    @property
    def munit(self):
        return 0

    def mdot(self, x, y):
        return x + y

Sum = SumM()
