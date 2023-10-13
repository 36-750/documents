from functools import reduce

def identity(x):
    return x

def compose(f, g):
    def f_after_g(x):
        return f(g(x))
    return f_after_g


class Fold:
    def __init__(self, wrap, step, initial, finish, dynamic=False):
        self.wrap = wrap
        self.step = step     # Keep original to facilitate transformation
        self.init = initial
        self.done = finish
        self.dynamic = dynamic

        def rf(r, w):        # The effective step function
            return step(r, wrap(w))
        self._rf = rf

    def fold(self, foldable, re_init=None):
        if re_init is not None:
            init = re_init
        elif self.dynamic and callable(self.init):
            init = self.init()
        else:
            init = self.init

        return self.done(reduce(self._rf, foldable, init))

    def extract(self):
        return self._done(self._init)

    def duplicate(self):
        return Fold(self.wrap, self.step, self.init,
                    lambda a: Fold(self.wrap, self.step, a, self.done))

    def premap(self, f):
        return Fold(compose(self.wrap, f), self.step, self.init, self.done)

    def postmap(self, g):
        return Fold(self.wrap, self.step, self.init, compose(g, self.done))

    def rewrap(self, new_wrap):
        return Fold(new_wrap, self.step, self.init, self.done)

    # def extend(self, f, sa):
    #     # fmap f . duplicate
    #     ...

def make_fold(step, *, initial=None, wrap=identity, finish=identity, dynamic=False):
    return Fold(wrap, step, initial, finish, dynamic)
