
# Incomplete but working

def Backwards(f: type[Applicative]):
    class Backward_f(f):
        "A Backward version of the Applicative f."

        @classmethod
        def pure(cls, a):
            return cls(f.pure(a))

        def map2(self, g, fb):
            return Backward_f(f(fb).map2(flip(g), f(self)))

    return Backward_f
