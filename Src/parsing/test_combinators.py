from __future__ import annotations

import pytest
import enum as E

from combinators import (ParseError, parse, failed,
                         pure, fmap, use, pipe, fix, do,
                         eof, space, hspace, vspace,
                         seq, chain, follows, followedBy, between, interleave,
                         alt, alts, many, some, optional, repeated,
                         any_char, char, char_in, char_not_in, char_satisfies,
                         string, istring, strings, string_in, sjoin, regex, symbol,
                         natural_number, integer, boolean,
                         letter, letters, digit, newline,
                         balanced_delimiters, enum,
                         str_cat)


#
# Helpers
#

def run(input, parser, pos=0):
    parsed = parse(input, parser, pos)
    if failed(parsed):
        raise ParseError(parsed.message + f' at {parsed.pos}')
    return parsed.result

ident = regex(r'[A-Za-z_][-A-Za-z_0-9?!]*')


#
# Tests
#
# EXERCISE. Expand these tests to include some property tests. Many of
#     these parsers/combinators are just begging for good property tests.
#     You can add any other tests that seem warranted as well.
#

def test_basic():
    "tests of basic parsers"
    assert run('abc', pure(4)) == 4
    assert parse('abc', pure(4)).state.point == 0
    assert run('abc', use(char('a'), 10)) == 10
    assert run('', eof) is True
    with pytest.raises(ParseError):
        run('a', eof)

    assert run('10, 20, 30', char('1')) == '1'
    assert run('10, 20, 30', regex('[0-9]+')) == '10'
    assert run('10, 20, 30', fmap(regex('[0-9]+'), int)) == 10

    assert run('xyz', char_in('uax')) == 'x'
    assert run('xyz', char_in(['u', 'x', 'a'])) == 'x'
    assert run('yxz', char_not_in('uax')) == 'y'
    assert run('yxz', char_not_in(['u', 'x', 'a'])) == 'y'

    assert run('A', char_satisfies(str.isupper)) == 'A'
    assert run('!', char_satisfies(str.isprintable)) == '!'

    assert run('abc', string('abc')) == 'abc'
    assert run('aBc', istring('abc')) == 'aBc'
    assert run('bar', strings('foo', 'bar', 'zap')) == 'bar'

    assert run('   ', hspace) == '   '
    assert run('\n',  vspace) == '\n'
    with pytest.raises(ParseError):
        run("\n  ", hspace)

    assert run('100', integer) == 100
    assert run('-100', integer) == -100
    assert run('-100.', integer) == -100
    assert run('1009', integer) != 100
    assert run('100.', natural_number) == 100

    assert run('true', boolean) is True
    assert run('yes', boolean) is True
    assert run('no', boolean) is False
    assert run('FALSE', boolean) is False

def test_seqs():
    "test of sequencing combinators"
    assert run('abbbbb', seq(any_char, regex('b+'))) == ('a', 'bbbbb')
    assert run('100    a', seq(followedBy(integer, space), char('a'))) == (100, 'a')
    assert run('100yes-10a', chain(natural_number, boolean, integer, any_char)) == [100, True, -10, 'a']

    assert run('[abc]', between(char('['), sjoin(char('a'), char('b'), char('c')), char(']'))) == 'abc'
    assert run('a, b, crg', interleave(fmap(letters, str_cat), symbol(',', hspace))) == ['a', 'b', 'crg']
    assert run('a, b, crg', interleave(string_in(['a', 'x', 'b', 'bb', 'c', 'crg']), symbol(','))) == ['a', 'b', 'crg']

    list_of_ints = interleave(natural_number, string(', '), start=char('['), end=char(']'), allow_empty=True)
    assert run('[10, 20, 30]', list_of_ints) == [10, 20, 30]
    assert run('[10]', list_of_ints) == [10]
    assert run('[]', list_of_ints) == []

def test_alts():
    "test of alternating combinators"
    assert run('abbbbb', alt(char('a'), char('c'))) == 'a'
    assert parse('abbbbb', alt(char('a'), char('c'))).state.point == 1
    assert run('cbbbbb', alt(char('a'), char('c'))) == 'c'
    assert run('X', alts(letter, digit, newline)) == 'X'
    assert run('9', alts(letter, digit, newline)) == '9'
    assert run('\n', alts(letter, digit, newline)) == '\n'
    with pytest.raises(ParseError):
        run(' ', alts(letter, digit, newline))

def test_reps():
    "Tests of repetition combinators"
    assert run('', many(string('ab'))) == []
    assert run('ababab', many(string('ab'))) == ['ab', 'ab', 'ab',]
    assert run('ababab', some(string('ab'))) == ['ab', 'ab', 'ab',]
    assert run('aaa', seq(some(char('a')), optional(char('b'), 'c'))) == (['a', 'a', 'a'], 'c')
    assert run('aaac', seq(some(char('a')), optional(char('b'), 'c'))) == (['a', 'a', 'a'], 'c')

    naturals_spaced = repeated(followedBy(natural_number, space), 3, 5)
    assert run('11 12 13 14 15 ', naturals_spaced) == [11, 12, 13, 14, 15]
    assert run('11 12 13 14 15 16 ', naturals_spaced) == [11, 12, 13, 14, 15]
    assert run('11 12 13 a', naturals_spaced) == [11, 12, 13]
    assert parse('11 12 13 a', naturals_spaced).state.point == 9

    with pytest.raises(ParseError):
        run('11 12 a', naturals_spaced)

    n_integers = lambda n: repeated(follows(space, integer), n, n)

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

def test_do():
    @do
    def foo():
        a = yield natural_number
        yield space
        b = yield integer
        yield space
        c = yield boolean
        return (a, b, c)

    assert run('10 -20 True', foo) == (10, -20, True)

    @do
    def sexp_list():
        return (yield interleave(sexp, space, start=char('('), end=char(')')))

    sexp = alt(alt(ident, integer), sexp_list)
    assert run('(a b (c d 3 (e 10 g (h (i (j))))))', sexp) == ['a', 'b', ['c', 'd', 3, ['e', 10, 'g', ['h', ['i', ['j']]]]]]
    with pytest.raises(ParseError):
        run('(a b (c $ 3 (e 10 g (h (i (j))))))', sexp)

def test_recursive():
    "Tests of fixed-point recursive parsers"
    opar = char('(')
    cpar = char(')')
    sexp = fix(lambda sexp: lambda state: alt(ident, interleave(sexp, space, start=opar, end=cpar))(state))

    assert run('(a b (c r g) ((d)) (e (f (g))))', sexp) == ['a', 'b', ['c', 'r', 'g'], [['d']], ['e', ['f', ['g']]]]

    err = parse('(a b (c r g) (($)) (e (f (g))))', sexp)
    assert failed(err)
    assert err.pos == 12
