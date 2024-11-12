# First Attempt ParserF

from __future__ import annotations

import fp_concepts
from   fp_concepts.all import *


#
# Helpers
#


#
# ParserF Decorator
#

def parser(f=None, label=""):
    """Converts a function to a valid parser.

    This can be used either directly or as a decorator on a parsing
    function definition. If `f` is a string or is missing, returns a
    decorating function that attaches the given label to the parser.
    (The label defaults to the functions name or "?" if the function
    is unnamed.) Otherwise, `f` should be a function and label a
    string.

    """
    if isinstance(f, str) or f is None:  # use as a decorator
        return lambda g: parser(g, f)

    return ParserF(f, label)


#
# Types
#

type Unit = ()
type Char = str
type ParseState = str
type ParseResult[A] = Maybe[A]
type ParseRun[A] = Pair[ParseState, ParseResult[A]]
type ParseFn[A] = Callable[[ParseState], ParseRun[A]]

class ParserF[A](Functor):
    """A Functorial Parser, first attempt.

    newtype ParserF a = ParserF (String -> Pair String (Maybe a))

    """
    def __init__(self, parser: ParseFn[A], label=''):
        self._parser = parser
        self._label = label or parser.__name__ or 'Parser?'

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    def __str__(self):
        return self._label 

    @staticmethod
    def with_label(parser, label):
        "Changes label on the given parser and returns it."
        parser._label = label
        return parser

    def map[B](self, f: Callable[[A], B]) -> ParserF[B]:
        return self.__class__(compose(lift(lift(f)), self._parser))

    def run(self, input: ParseState) -> ParseRun[A]:
        return self._parser(input)


#
# Utilities
#

with_label = ParserF.with_label  # More convenient without breaking encapsulation

def failed[A](run: ParseRun[A]) -> bool:
    return not run[1]

def parsed[A](
        f: Callable[[ParseRun[A]], ParseRun[A]],
        run: ParseRun[A],
        give: ParseRun[A] | None = None
) -> ParseRun[A]:
    if failed(run):
        return run if give is None else give
    return f(run)


#
# Starter Parsers
#

@parser
def void(input: ParseState) -> ParseRun[Unit]:
    return Pair(input, None_())

@parser
def empty(input: ParseState) -> ParseRun[Unit]:
    return Pair(input, Some(()))

@parser
def any_char(input: ParseState) -> ParseRun[str]:
    if not input:
        return (input, None_())
    return Pair(input[1:], Some(input[0]))

def char(c: Char) -> ParserF[Char]:
    @parser(f'char({c})')
    def char_c(input: ParseState) -> ParseRun[str]:
        if input and input[0] == c:
            return Pair(input[1:], Some(c))
        return Pair(input, None_())

    return char_c

def char_in(cs: str) -> ParserF[Char]:
    @parser(f'char_in({cs})')
    def char_in_set(input: ParseState) -> ParseRun[str]:
        if input and input[0] in cs:
            return Pair(input[1:], Some(input[0]))
        return Pair(input, None_())

    return char_in_set

# What is the type of digit?
digit = map(lambda x: ord(x) - ord('0'), char_in("0123456789"))
digit = with_label(digit, 'digit')

@parser
def natural(input: ParseState) -> ParseRun[str]:
    def go(current):
        updated = lambda m: map2(lambda x, y: 10 * x + y, current[1], m)
        recurse = lambda r: go(map(updated, r))
        return parsed(recurse, digit.run(current[0]), current)

        # # A direct approach
        # state1, result = digit.run(current[0])
        # if not result:
        #     return current
        # updated = map2(lambda x, y: 10 * x + y, current[1], result)
        # return go(Pair(state1, updated))

    return parsed(go, digit.run(input))    # Note: Elimination Form!

# Should this have been easier?
# What about use? alt? optional? seq?
# Consider that we may want to convert to many different types


if __name__ == '__main__':
    results = [
        (Some('f'),  any_char.run('foo')),
        (None_(),    any_char.run('')),
        (Some('f'),  char('f').run('foo')),
        (None_(),    char('f').run('')),
        (Some('c'),  char_in('abcdefg').run('crg')),
        (None_(),    char_in('abcdefg').run('xyz')),
        (Some(8),    digit.run('8')),
        (None_(),    digit.run('u')),
        (Some(1024), natural.run('1024c')),
    ]

    # Labels
    print(any_char)
    print(char('f'))
    print(char_in('mnopqrs'))
    print(digit)

    # Results
    for a, b in results:
        if a == b[1]:
            expect = '\u001b[1;32mExpecting\u001b[0m:'
        else:
            expect = '\u001b[1;31mExpecting\u001b[0m:'
        print( f'{expect} {repr(a)} in {repr(b)}' )
