from __future__ import annotations

import pytest

from parse_regexp_rich import (parse_regexp, RegExp,
                               Literal, Dot, EscapeSequence, CharacterClass, Assertion,
                               Concat, Group, Alternation, Repetition, Lookaround,
                               Intersection,
                               RegexModifier, RegexGroup)


#
# Helpers
#

# EXERCISE. This works but is ugly. A better approach is to make
# each class responsible for its own output. This is related
# to the s-expression exercise in the parse_regexp.py file.
# Implement an interface within the classes (moving the methods as
# far up the inheritance chain as possible) that makes as_tree
# easy to write and easy to extend or generalize.

def as_tree(r: RegExp) -> list | tuple:
    "A simple recursive conversion from RegExp to list-based tree."
    match r:
        # Leaf Nodes
        case Literal(text=txt):
            return ('Literal', txt)
        case Dot():
            return ('Dot',)
        case EscapeSequence(text=txt):
            return ('EscapeSequence', txt)
        case CharacterClass(chars=cs, complement=compl):
            return ('CharacterClass', ':not-in' if compl else ':in', cs)
        case Assertion(assertion=a):
            return ('Assertion', a)
        # Branch nodes
        case Concat(children=rs):
            return ['Concat', *[as_tree(r) for r in rs]]
        case Group(child=r, type=gtype, name=name):
            return ['Group', str(gtype), as_tree(r), name]
        case Group(child=r, type=gtype):
            return ['Group', str(gtype), as_tree(r)]
        case Alternation(children=rs):
            return ['Alternation', *[as_tree(r) for r in rs]]
        case Intersection(children=rs):
            return ['Intersection', *[as_tree(r) for r in rs]]
        case Repetition(child=r, type=mtype, minimum=mn, maximum=mx, lazy=lz):
            pars = [{'min': mn, 'max': mx}] if mtype == RegexModifier.RANGE else []
            return ['Repetition', str(mtype), ':lazy' if lz else ':eager', as_tree(r), *pars]
        case Lookaround():
            raise ValueError('Lookaround currently unsupported')
        case other:
            raise ValueError(f'Unexpected RegExp node {other}.')

#
# Tests
#
# (ATTN: More needed here)

def test_basic():
    "simple regexes"
    r = as_tree(parse_regexp('abc'))
    assert r == ('Literal', 'abc')

    r = as_tree(parse_regexp(r'ab\*c'))
    assert r == ('Literal', 'ab*c')

    r = as_tree(parse_regexp('abc*'))
    assert r[0] == 'Concat' and len(r) == 3
    assert r[1] == ('Literal', 'ab')
    assert r[2] == ['Repetition', 'Many', ':eager', ('Literal', 'c')]

    r = as_tree(parse_regexp('[abc]|[^def]+'))
    assert r[0] == 'Alternation' and len(r) == 3
    assert r[1] == ('CharacterClass', ':in', 'abc')
    assert r[2] == ['Repetition', 'Some', ':eager', ('CharacterClass', ':not-in', 'def')]

    r = as_tree(parse_regexp('[abc]|[^def]+?'))
    assert r[0] == 'Alternation' and len(r) == 3
    assert r[1] == ('CharacterClass', ':in', 'abc')
    assert r[2] == ['Repetition', 'Some', ':lazy', ('CharacterClass', ':not-in', 'def')]

    r = as_tree(parse_regexp('(a|b){2,5}'))
    assert r == ['Repetition', 'Range', ':eager',
                 ['Group', 'Capturing',
                  ['Alternation', ('Literal', 'a'), ('Literal', 'b')]],
                 {'min': 2, 'max': 5}]

    r = as_tree(parse_regexp('(a|b){2}'))
    assert r == ['Repetition', 'Range', ':eager',
                 ['Group', 'Capturing',
                  ['Alternation', ('Literal', 'a'), ('Literal', 'b')]],
                 {'min': 2, 'max': 2}]

    r = as_tree(parse_regexp('(?:a|b){2,5}'))
    assert r == ['Repetition', 'Range', ':eager',
                 ['Group', 'NonCapturing',
                  ['Alternation', ('Literal', 'a'), ('Literal', 'b')]],
                 {'min': 2, 'max': 5}]

    r = as_tree(parse_regexp('(?P<foo>a|b){2,5}'))
    assert r == ['Repetition', 'Range', ':eager',
                 ['Group', 'Named',
                  ['Alternation', ('Literal', 'a'), ('Literal', 'b')], 'foo'],
                 {'min': 2, 'max': 5}]

    r = as_tree(parse_regexp('(?:-?[1-9][0-9]*|0)'))
    assert r == ['Group', 'NonCapturing',
                 ['Alternation',
                  ['Concat',
                   ['Repetition', 'Optional', ':eager', ('Literal', '-')],
                   ('CharacterClass', ':in', '1-9'),
                   ['Repetition', 'Many', ':eager', ('CharacterClass', ':in', '0-9')]],
                  ('Literal', '0')]]

def test_intersect():
    r = as_tree(parse_regexp('abc&def'))
    assert r == ['Intersection', ('Literal', 'abc'), ('Literal', 'def')]

    r = as_tree(parse_regexp('x&[xyz]+'))
    assert r == ['Intersection', ('Literal', 'x'), ['Repetition', 'Some', ':eager', ('CharacterClass', ':in', 'xyz')]]

    r = as_tree(parse_regexp('abc&def|[xyz]+&x|(?:u&u??)'))
    assert r == ['Alternation',
                 ['Intersection', ('Literal', 'abc'), ('Literal', 'def')],
                 ['Intersection', ['Repetition', 'Some', ':eager', ('CharacterClass', ':in', 'xyz')], ('Literal', 'x')],
                 ['Group', 'NonCapturing',
                  ['Intersection', ('Literal', 'u'), ['Repetition', 'Optional', ':lazy', ('Literal', 'u')]]]]
