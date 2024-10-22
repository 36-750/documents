#!/usr/bin/env python3.12
#
# Examples and Tests of FP Traits
#
# To run examples, enter
#
#   python fpc_examps.py
#
# To run the tests, enter
#
#   python -m pytest -v fpc_examps.py 
#
# python 3.12 is expected here because
# of the typing syntax.
#
# You should put all the files
#
# Applicative.py, Bifunctor.py, Functor.py, Monad.py, fpc.py, fpc_examps.py
#
# in your working directory for this.
#

from enum        import Enum
from functools   import partial
from operator    import add, mul

import Monoid as Monoids

from Functor     import map, lift
from Applicative import map2, ap
from Monad       import bind, do, do_fn
from Bifunctor   import bimap
from functions   import compose, identity, triple
from utils       import Collect
from ops         import foldMap

from Either      import *
from List        import *
from Maybe       import *
from Pair        import *
from State       import *
from Trees       import *

#
# Helpers
#

def check_assertions(examples):
    for a, b, eq in examples():
        if eq is None:
            assert a == b
        else:
            assert eq(a, b)

c = compose   # shorthand


#
# Applicative
#

def applicative_examples():
    return [
        # shows autocurrying applicative style
        (ap(triple, List.of(1, 2), List.of(3, 4), List.of(5, 6)),
         [(1, 3, 5), (1, 3, 6), (1, 4, 5), (1, 4, 6), (2, 3, 5), (2, 3, 6), (2, 4, 5), (2, 4, 6)],
         None),
        (ap(c(sum, triple), List.of(1, 2), List.of(3, 4), List.of(5, 6)),
         [9, 10, 10, 11, 10, 11, 11, 12],
         None)
    ]

def test_applicative():
    check_assertions(applicative_examples)


#
# Maybe
#

def maybe_examples():
    inc = lambda v: v + 1

    x = Some(10)
    y = None_()

    @do_fn(Maybe)
    def add3_maybes(mx, my, mz):
        x = yield mx
        y = yield my
        z = yield mz
        return x + y + z

    @do_fn(Maybe)
    def fold_maybes(f, init, maybes):
        acc = init
        for mx in maybes:
            x = yield mx
            acc = f(acc, x)
        return acc

    @do(Maybe)
    def got20a():
        xs = yield Some([10, 20, 30, 40])
        ind = xs.index(20)
        if ind < 0:
            return None_()
        return ind

    @do(Maybe, Some([10, 20, 30, 40]))
    def got20b(mxs):
        xs = yield mxs
        ind = xs.index(20)
        if ind < 0:
            return None_()
        return ind

    # Pattern matching works nicely
    def match_maybe(m):
        match m:
            case None_():
                return 'None'
            case Some(x):
                return f'Some {x}'
            case _:
                return 'oops'

    return [
        (x.get(0), 10, None),
        (y.get(0), 0, None),
        (map(inc, x), Some(11), None),
        (map(inc, y), None_(),  None),
        (add3_maybes(Some(10), Some(20), Some(30)), Some(60), None),
        (add3_maybes(Some(10), None_(), Some(30)), None_(), None),
        (add3_maybes(None_(), None_(), Some(30)), None_(), None),
        (add3_maybes(None_(), Some(200), Some(100)), None_(), None),
        (add3_maybes(Some(300), Some(200), None_()), None_(), None),
        (add3_maybes(Some(300), Some(200), Some(100)), Some(600), None),
        (fold_maybes(add, 0, [Some(300), Some(200), Some(100)]), Some(600), None),
        (fold_maybes(add, 0, [Some(300), None_(), Some(100)]), None_(), None),
        (got20a, Some(1), None),
        (got20b, Some(1), None),
        (match_maybe(None_()), 'None', None),
        (match_maybe(Some(16)), 'Some 16', None),
        (match_maybe(Some("foo")), 'Some foo', None),
    ]

def test_maybes():
    check_assertions(maybe_examples)


#
# Lists
#

def list_examples():
    def eq(ma, mb):
        return len(ma) == len(mb) and all(a == b for a, b in zip(ma, mb))

    inc = lambda v: v + 1
    incF = lift(inc)
    parenthesize = lambda s: '(' + s + ')'

    z = List.of(1, 2, 3, 4, 5)
    u = List.of(Some(1), None_(), Some(2), None_(), Some(3))
    w = ['a', 'b', 'c']

    @do_fn(List)
    def pairs_from(xs, ys):
        x = yield xs
        y = yield ys
        return (x, y)

    @do_fn(List)
    def segs(xs):
        x = yield xs
        y = yield [x - 1, x, x + 1]
        return (x, y)

    @do(List, [1, 2, 3, 4])
    def contingent(xs):
        x = yield xs
        if x % 2 == 0:
            y = yield [x, 2 * x, 10 * x]
        else:
            y = yield []
        return y

    return [
        (map(inc, z), List.of(2, 3, 4, 5, 6), eq),
        (map(incF, u), List.of(Some(2), None_(), Some(3), None_(), Some(4)), eq),
        (map(parenthesize, List(w)), List(['(a)', '(b)', '(c)']), eq),
        (pairs_from([1, 2, 3], [4, 5, 6]), List([(1, 4), (1, 5), (1, 6), (2, 4), (2, 5), (2, 6), (3, 4), (3, 5), (3, 6)]), eq),
        (pairs_from([1, 2, 3], [10, 20]), List([(1, 10), (1, 20), (2, 10), (2, 20), (3, 10), (3, 20)]), eq),
        (pairs_from([], [10, 20]), List([]), None),
        (pairs_from([10, 20], []), List([]), None),
        (segs([1, 2, 3]), List([(1, 0), (1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (3, 2), (3, 3), (3, 4)]), eq),
        (segs([]), List([]), None),
        (ap(List.of(lambda x: x + 1, lambda y: 2 * y), List.of(10, 20, 30)), List([11, 21, 31, 20, 40, 60]), eq),
        (contingent, List([2, 4, 20, 4, 8, 40]), eq),
    ]

def test_lists():
    check_assertions(list_examples)


#
# Either
#

def either_examples():
    def all_eq(la, lb):
        return len(la) == len(lb) and all(a == b for a, b in zip(la, lb))

    @do_fn(Either)
    def sum3(mx, my, mz):
        x = yield mx
        y = yield my
        z = yield mz
        return x + y + z

    @do(Either, Right(4), Right(5), Right(23))
    def summed3m(mx, my ,mz):
        x = yield mx
        y = yield my
        z = yield mz
        return x + y + z

    def match_either(m):
        match m:
            case Left(a):
                return f'Left {a}'
            case Right(b):
                return f'Right {b}'
            case _:
                return 'oops'

    return [
        (sum3(Right(4), Right(5), Right(23)), Right(32), None),
        (sum3(Right(4), Left(5), Right(23)),  Left(5),   None),
        (sum3(Left(4),  Left(5), Right(23)),  Left(4),   None),
        (sum3(Right(4), Right(5), Right(23)), Right(32), None),
        (summed3m, Right(32), None),
        (map(lambda k: k ** 2, Right(10)), Right(100), None),
        (map(lambda k: k ** 2, Left(-1)),  Left(-1),   None),
        (map2(mul, Right(-1), Right(10)),  Right(-10), None),
        (map2(mul, Left(-1), Right(10)),   Left(-1),   None),
        (map2(mul, Right(-1), Left(10)),   Left(10),   None),
        (bimap(lambda k: k + 10, lambda j: j * 100, Left(4)),  Left(14),   None),
        (bimap(lambda k: k + 10, lambda j: j * 100, Right(4)), Right(400), None),
        ([m.bind(lambda v: Right(1000 + v)) for m in List.of(Right(10), Left(0), Right(7))],
         List.of(Right(1010), Left(0), Right(1007)),
         all_eq),
        (match_either(Left(4)),    'Left 4', None),
        (match_either(Right('a')), 'Right a', None),
        (match_either(Right(0)),   'Right 0', None),
    ]
    

def test_eithers():
    check_assertions(either_examples)


#
# Trees
#

def tree_examples():
    add = lambda a, b: a + b

    t = BinaryTree([1, [2, [3, None, None], [4, None, None]], [5, None, None]])
    u = map(partial(add, 10), t)
    v = complete_btree(3)

    label = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K",
             "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
             "W", "X", "Y", "Z", "AA", "BB", "CC", "DD", "EE", "FF",]
    w = v.map(lambda k: label[k])

    x = RoseTree([1, [2, [3], [4], [5]], [6, [7, [8, [9], [10]]]]])
    y = x.map(lambda k: k ** 2)

    return [t, u, v, w, x, y]

def test_trees():
    t, u, v, w, x, y, *_ = tree_examples()

    assert t.to_sexp() == [1, [2, [3, None, None], [4, None, None]], [5, None, None]]
    assert u.to_sexp() == [11, [12, [13, None, None], [14, None, None]], [15, None, None]]

    v_sexp = [0, [1, [3, [7, None, None], [8, None, None]], [4, [9, None, None], [10, None, None]]],
                 [2, [5, [11, None, None], [12, None, None]], [6, [13, None, None], [14, None, None]]]]
    
    w_sexp = ["A", ["B", ["D", ["H", None, None], ["I", None, None]], ["E", ["J", None, None], ["K", None, None]]],
                 ["C", ["F", ["L", None, None], ["M", None, None]], ["G", ["N", None, None], ["O", None, None]]]]

    assert v.to_sexp() == v_sexp
    assert w.to_sexp() == w_sexp

    x_sexp = [1, [2, [3], [4], [5]], [6, [7, [8, [9], [10]]]]]
    y_sexp = [1, [4, [9], [16], [25]], [36, [49, [64, [81], [100]]]]]
    
    assert x.to_sexp() == x_sexp
    assert y.to_sexp() == y_sexp


#
# State
#

def state_examples():
    def eq0(ma, mb):
        return len(ma) == len(mb) and all(a == b for a, b in zip(ma, mb))

    def eq(ma, mb):
        ma1, ma2 = ma
        mb1, mb2 = mb
        return eq0(ma1, mb1) and ma2 == mb2

    class TsStates (Enum):
        LOCKED = 0
        UNLOCKED = 1

    class TsOutput(Enum):
        WARN = 10
        THANK = 20
        OPEN = 30

    # Example based on https://en.wikibooks.org/wiki/Haskell/Understanding_monads/State

    @State    
    def coin(_any: TsStates) -> tuple[TsOutput, TsStates]:
        return (TsOutput.THANK, TsStates.UNLOCKED)

    @State
    def push(st: TsStates)  -> tuple[TsOutput, TsStates]:
        if st == TsStates.LOCKED:
            return (TsOutput.WARN, TsStates.LOCKED)
        return (TsOutput.OPEN, TsStates.LOCKED)

    @do(State)
    def ts_action():
        out1 = yield coin
        out2 = yield push
        out3 = yield push
        out4 = yield coin
        out5 = yield push
        return [out1, out2, out3, out4, out5]

    @do(State)
    def ts_putget():
        _ = yield State.put(TsStates.UNLOCKED)
        out1 = yield push
        out2 = yield push
        out3 = yield State.get
        return [out1, out2, out3]

    return [
        (ts_action.run(TsStates.LOCKED),
         ([TsOutput.THANK, TsOutput.OPEN, TsOutput.WARN, TsOutput.THANK, TsOutput.OPEN], TsStates.LOCKED),
         eq),
        (ts_action.eval(TsStates.LOCKED), [TsOutput.THANK, TsOutput.OPEN, TsOutput.WARN, TsOutput.THANK, TsOutput.OPEN], eq0),
        (ts_action.exec(TsStates.LOCKED), TsStates.LOCKED, None),
        (ts_putget.run(TsStates.LOCKED), ([TsOutput.OPEN, TsOutput.WARN, TsStates.LOCKED], TsStates.LOCKED), eq),
        (ts_putget.eval(TsStates.LOCKED), [TsOutput.OPEN, TsOutput.WARN, TsStates.LOCKED], eq0),
        (ts_putget.exec(TsStates.LOCKED), TsStates.LOCKED, None),
    ]

def test_state():
    check_assertions(state_examples)


#
# Combinations
#

def combined_examples():
    t = RoseTree([1, [2, [3], [4], [5]], [6, [7, [8, [9], [10]]]]])

    return [
        (foldMap(identity, t, Monoids.Sum), 55, None),
        (foldMap(identity, t, Monoids.Product), 3628800, None),
        (foldMap(identity, t, Collect), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], None),
        (foldMap(lambda a: Pair(a, a), t, Monoids.mtuple(Monoids.Sum, Monoids.Product)),
         (55, 3628800), None),
    ]

def test_combined():
    check_assertions(combined_examples)

#
# Output
#

def print_comparisons(cmps):
    for a, b, eq in cmps():
        same = eq(a, b) if eq is not None else a == b

        if same:
            print(f'    \u001b[1;32mCORRECT\u001b[0m: {a} equals {b}')
        else:
            print(f'    \u001b[1;31mFAILED\u001b[0m:  {a} does not equal {b}')


#
# Examples
#

if __name__ == '__main__':
    print('Applicative examples:')
    print_comparisons(applicative_examples)
    print('')

    print('List examples:')
    print_comparisons(list_examples)
    print('')

    print('Maybe examples:')
    print_comparisons(maybe_examples)
    print('')

    print('Either examples:')
    print_comparisons(either_examples)
    print('')

    print('State examples:')
    print_comparisons(state_examples)
    print('')

    print('Combined examples:')
    print_comparisons(state_examples)
    print('')

    print('Tree examples:')
    for tree in tree_examples():
        print(tree)
    print('')
