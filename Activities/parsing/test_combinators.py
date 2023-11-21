from __future__ import annotations

import pytest
import enum as E

from combinators import *


#
# Helpers
#

def run(input, parser, pos=0):
    parsed = parse(input, parser, pos)
    if failed(parsed):
        raise ParseError(parsed.message + f' at {parsed.pos}')
    return parsed.result

ident = regex(r'[-A-Za-z_?!]+')


#
# Tests
#

def test_basic():
    assert run('10, 20, 30', char('1')) == '1'
    assert run('10, 20, 30', regex('[0-9]+')) == '10'
    assert run('10, 20, 30', fmap(regex('[0-9]+'), int)) == 10

def test_reps():
    list_of_ints = interleave(fmap(regex('[0-9]+'), int), lexeme(', '), start=char('['), end=char(']'))
    assert run('[10, 20, 30]', list_of_ints) == [10, 20, 30]
    assert run('[10]', list_of_ints) == [10]
    assert run('[]', list_of_ints) == []

    assert run('100', integer) == 100
    assert run('-100', integer) == -100
    assert run('-100.', integer) == -100
    assert run('1009', integer) != 100
    assert run('100.', natural_number) == 100

    assert run('100    a', seq(followedBy(integer, whitespace), char('a'))) == (100, 'a')

    naturals_spaced = repeated(followedBy(natural_number, whitespace), 3, 5)
    assert run('11 12 13 14 15 ', naturals_spaced) == [11, 12, 13, 14, 15]
    assert run('11 12 13 14 15 16 ', naturals_spaced) == [11, 12, 13, 14, 15]
    assert run('11 12 13 a', naturals_spaced) == [11, 12, 13]
    assert parse('11 12 13 a', naturals_spaced).state.point == 9

    with pytest.raises(ParseError):
        run('11 12 a', naturals_spaced)

    n_integers = lambda n: repeated(follows(whitespace, integer), n, n)

    assert run(' -1 10 -3', n_integers(3)) == [-1, 10, -3]
    assert run('3 -1 10 -3', pipe(natural_number, n_integers)) == [-1, 10, -3]

def test_specials():
    assert (run('(a(b(c)d(e)((f))(((g)))))xyz', balanced_delimiters('(', ')'))
            == ('(a(b(c)d(e)((f))(((g)))))', [0, 2, 4, -6, 8, -10, 11, 12, -14, -15, 16, 17, 18, -20, -21, -22, -23, -24]))
    assert (run('uuu(a(b(c)d(e)((f))(((g)))))xyz)', balanced_delimiters('(', ')', seen_opening=True))
            == ('uuu(a(b(c)d(e)((f))(((g)))))xyz)', [3, 5, 7, -9, 11, -13, 14, 15, -17, -18, 19, 20, 21, -23, -24, -25, -26, -27, -31]))

    class RGB(E.Enum):
        Red = "Red"
        Green = "Green"
        Blue = "Blue"
    assert run('Red', enum(RGB)) == RGB.Red
    assert run('Green', enum(RGB)) == RGB.Green
    assert run('Blue', enum(RGB)) == RGB.Blue

def test_lazy():
    @lazy
    def foo():
        a = yield natural_number
        yield whitespace
        b = yield integer
        yield whitespace
        c = yield boolean
        return (a, b, c)

    assert run('10 -20 True', foo) == (10, -20, True)

    @lazy
    def sexp_list():
        return (yield interleave(sexp, whitespace, start=char('('), end=char(')')))

    sexp = alt(alt(ident, integer), sexp_list)
    assert run('(a b (c d 3 (e 10 g (h (i (j))))))', sexp) == ['a', 'b', ['c', 'd', 3, ['e', 10, 'g', ['h', ['i', ['j']]]]]]
    with pytest.raises(ParseError):
        run('(a b (c $ 3 (e 10 g (h (i (j))))))', sexp)


# Experimental    
def test_recursive():
    def sexp_rec(p):
        return alt(ident, interleave(p, whitespace, start=char('('), end=char(')')))

    # S-expression parser to depth 4
    sexp4 = sexp_rec(sexp_rec(sexp_rec(sexp_rec(ident))))
    assert run('(a b (c d (e f g)))', sexp4) == ['a', 'b', ['c', 'd', ['e', 'f', 'g']]]

    # S-expression parser to arbitrary depth
    sexp = fix(sexp_rec)
    assert run('(a b (c d (e f g)))', sexp) == ['a', 'b', ['c', 'd', ['e', 'f', 'g']]]
    assert run('(a b (c d (e f g (h (i (j))))))', sexp) == ['a', 'b', ['c', 'd', ['e', 'f', 'g', ['h', ['i', ['j']]]]]]

    # S-expression with symbols and numbers
    sexp = fix(lambda p: alt(alt(ident, integer), interleave(p, whitespace, start=char('('), end=char(')'))))
    assert run('(a b (c d 3 (e 10 g (h (i (j))))))', sexp) == ['a', 'b', ['c', 'd', 3, ['e', 10, 'g', ['h', ['i', ['j']]]]]]
