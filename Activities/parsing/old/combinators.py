#
# A quick implementation of parser combinators
#

from __future__ import annotations

import re
import enum as E

from dataclasses       import dataclass
from functools         import partial, wraps
from typing            import Callable, cast, Generic, TypeVar
from typing_extensions import Any, TypeAlias, TypeGuard

#
# Types
#

A = TypeVar("A")
B = TypeVar("B")

class ParseError(Exception):
    def __init__(self, message, data=None):
        super().__init__(message)
        self.data = data or {}

Position: TypeAlias = int
ErrorMesg: TypeAlias = str

@dataclass(frozen=True)   # Can add slots=True here to make more efficient
class ParseState:
    source: str
    point: Position
    start: Position   # Set to point if not supplied

    def __init__(self, source="", point=0, start=-1):
        n = len(source)
        object.__setattr__(self, 'source', source)
        object.__setattr__(self, 'point', min(point, n) if point >= 0 else max(n + point, 0))
        object.__setattr__(self, 'start', start if start >= 0 else self.point)

    # def __post_init__(self):
    #     if self.start < 0:
    #         self.start = self.point

    def view(self, maxlen: int = -1) -> str:
        "Returns a view of the remaining input, optionally bounded in length."
        n = len(self.source)
        if maxlen < 0:
            end = n
        else:
            end = min(self.point + maxlen, n)
        return self.source[self.point:end]

    def require(self, size: int) -> tuple[str, bool]:
        """Like view, but if required number of characters not available indicates failure.

        Returns (view, True) or (message, False), the latter only if
        the required number of characters are not available.

        """
        n = len(self.source)
        if self.point + size > n:
            return (f'Required {size} characters but only {n - self.point} remain.', False)
        return (self.view(size), True)

    def advance(self, by: int) -> ParseState:
        if by == 0:
            return self
        return ParseState(self.source, self.point + by, self.start)

@dataclass
class Success(Generic[A]):
    """Result of a successful parsing step."""
    result: A
    state: ParseState

@dataclass
class Failure:
    """Result of a failed parsing step."""
    message: ErrorMesg
    pos: Position
    data: dict | None = None

ParseResult: TypeAlias = Success[A] | Failure

# type Parser a = Parser (ParserState -> ParseResult a)
#
# Note: In Python, it would be useful to make Parser an class with a
# __call__ method. This would accept the function and label in the
# constructor, can allow for nice operator overloads, supports forward
# references, and more.
#
# We keep it simple here for the moment, just using functions and
# assigning the parser label for each parser. But adjust this
# in the next stage.

Parser: TypeAlias = Callable[[ParseState], ParseResult[A]]

# decorator for a parser that sets a label
def parser(label="?", f=None):
    "A decorator that attaches a label to a parser"
    if f is None:
        return partial(parser, label)
    set_label(f, label)
    return f


#
# Helpers
#

def merge_data(data1: dict | None, data2: dict | None) -> dict | None:
    if data1 is None:
        return data2
    if data2 is None:
        return data1
    return data1 | data2


#
# Infrastructure
#

def failed(parse: ParseResult[A]) -> TypeGuard[Failure]:
    return isinstance(parse, Failure)

def succeeded(parse: ParseResult[A]) -> TypeGuard[Success[A]]:
    return isinstance(parse, Success)

def set_label(parser, label: str) -> None:
    setattr(parser, 'parser_label', label)

def get_label(parser) -> str:
    if parser is None:
        return ""
    return getattr(parser, 'parser_label') or "?"

@parser('void')
def void(state: ParseState) -> ParseResult[A]:
    "Parser that always fails"
    return Failure("Void parser", state.point)

def failure(reason: str) -> Parser[A]:
    "Returns a void parser that fails with stated reason."
    def fails(state: ParseState) -> ParseResult[A]:
        return Failure(reason, state.point)
    return parser(f'fails({reason})', fails)

def pure(x: A) -> Parser[A]:
    "Returns a parser that just returns x on the empty string."
    @parser(f'pure({x})')
    def pureP(state: ParseState) -> ParseResult[A]:
        return Success(x, state)
    return pureP

def fmap(p: Parser[A], f: Callable[[A], B]) -> Parser[B]:
    "Transforms the parse result by a function."
    @parser(f'fmap({get_label(p)})')
    def mapped(state: ParseState) -> ParseResult[B]:
        parse_A = p(state)
        match parse_A:
            case Success(resA, stateA):
                return Success(f(resA), stateA)
            case _:  # Failure
                return parse_A
    return mapped

def pipe(p: Parser[A], f: Callable[[A], Parser[B]]) -> Parser[B]:
    "Creates a parser pipeline where the second stage depends on the result of the first."
    @parser(f'pipe({get_label(p)})')
    def piped(state: ParseState) -> ParseResult[B]:
        parse_A = p(state)
        match parse_A:
            case Success(resA, stateA):
                return f(resA)(stateA)
            case _:  # Failure
                return parse_A
    return piped


#
# Higher-Order Combinators
#

def seq(p: Parser[A], q: Parser[B]) -> Parser[tuple[A, B]]:
    "Executes two parsers in sequence, collecting results, short-circuiting on failure."
    sequenced = pipe(p, lambda x: pipe(q, lambda y: pure((x, y))))   # type: ignore
    return parser(f'seq({get_label(p)}, {get_label(q)})', sequenced)

def followedBy(p: Parser[A], q: Parser[B]) -> Parser[A]:
    "Executes two parsers in sequence, ignoring the result of the second."
    sequenced = pipe(p, lambda x: pipe(q, lambda y: pure(x)))   # type: ignore
    return parser(f'followedBy({get_label(p)}, {get_label(q)})', sequenced)

def follows(p: Parser[A], q: Parser[B]) -> Parser[B]:
    "Executes two parsers in sequence, ignoring the result of the first."
    sequenced = pipe(p, lambda x: pipe(q, lambda y: pure(y)))   # type: ignore
    return parser(f'follows({get_label(p)}, {get_label(q)})', sequenced)

def between(p: Parser[B], q: Parser[A], r: Parser[B]) -> Parser[A]:
    "Executes three parsers in sequence, ignoring the first and last."
    sequenced = followedBy(follows(p, q), r)
    return parser(f'between({get_label(p)}, {get_label(q)}, {get_label(r)})', sequenced)

def chain(*ps: Parser) -> Parser[list]:
    """Returns a parser that runs a list of parsers in success, failing if any fail.

    The value of the parser is the list of values returned by the component parsers
    in the same order as specified.

    """
    @parser(f'chain({", ".join(map(get_label, ps))})')
    def chained(state: ParseState) -> ParseResult[list]:
        state1 = state
        results = []
        for p in ps:
            match p(state1):
                case Success(res, next_state):
                    results.append(res)
                    state1 = next_state
                case parsed:  # Failure
                    assert isinstance(parsed, Failure)
                    return Failure(f': {parsed.message}', parsed.pos, parsed.data)
        return Success(results, state1)
    return chained

def alt(p: Parser[A], q: Parser[B]) -> Parser[A | B]:
    "Returns a parser that parses p, or q if p fails."
    label = f'alt({get_label(p)}, {get_label(q)})'

    @parser(label)
    def alternative(state: ParseState) -> ParseResult[A | B]:
        parse_A = p(state)
        match parse_A:
            case Success():
                return cast(ParseResult[A | B], parse_A)
            case _:  # Failure
                parse_B = q(state)
                if failed(parse_B):
                    point = max(parse_A.pos, parse_B.pos)
                    mesg = f'{label} failed: {parse_A.message} and {parse_B.message}'
                    data = merge_data(merge_data(parse_A.data, parse_B.data),
                                      {'failure-positions': (parse_A.pos, parse_B.pos)})
                    return Failure(mesg, point, data)
                return cast(ParseResult[A | B], parse_B)
    return alternative

def alts(*ps: Parser) -> Parser:
    "Matches the first of a list of parsers to succeed. See also `alt`."
    @parser(f'alts({", ".join(map(get_label, ps))})')
    def alternatives(state: ParseState) -> ParseResult:
        farthest = state.point
        data = None
        positions = []
        mesg = ''
        for p in ps:
            parsed = p(state)
            match parsed:
                case Success():
                    return parsed
                case _:  # Failure
                    if parsed.pos > farthest:
                        farthest = parsed.pos
                        data = parsed.data
                        mesg = parsed.message
                    positions.append(parsed.pos)
        return Failure(f'All alternatives failed: {mesg}', farthest, merge_data(data, {'failure-positions': positions}))
    return alternatives

def optional(p: Parser[A]) -> Parser[A | None]:
    "Matches a parser zero or one times."
    opt = alt(p, pure(None))
    return parser(f'{get_label(p)}?', opt)

def many(p: Parser[A]) -> Parser[list[A]]:
    "Returns a parser that matches p zero or more times."
    @parser(f'{get_label(p)}*')
    def p_star(state: ParseState) -> ParseResult[list[A]]:
        results = []
        parsed = p(state)
        state1 = state
        while True:
            match parsed:
                case Success(res, next_state):
                    results.append(res)
                    state1 = next_state
                    parsed = p(state1)
                case _:  # Failure
                    break
        return Success(results, state1)
    return p_star

def some(p: Parser[A]) -> Parser[list[A]]:
    "Returns a parser that matches p one or more times."
    @parser(f'{get_label(p)}+')
    def p_plus(state: ParseState) -> ParseResult[list[A]]:
        parsed = p(state)

        if failed(parsed):
            return parsed

        results = [cast(Success[A], parsed).result]  # grrr Python typing...
        state1 = state
        parsed = p(state1)
        while True:
            match parsed:
                case Success(res, next_state):
                    results.append(res)
                    state1 = next_state
                    parsed = p(state1)
                case _:  # Failure
                    break
        return Success(results, state1)
    return p_plus

def repeated(p: Parser[A], minimum: int, maximum: int) -> Parser[list[A]]:
    "Returns a parser that matches p from minimum to maximum times, inclusive."
    if minimum < 0 or minimum > maximum or maximum < 0:
        raise ValueError('repeated parser requires non-negative minimum <= maximum')

    @parser(f'{get_label(p)}{{{minimum},{maximum}}}')
    def p_rep(state: ParseState) -> ParseResult[list[A]]:
        state1 = state
        reps = 0
        results = []
        while reps < minimum:
            match p(state1):
                case Success(res, next_state):
                    results.append(res)
                    reps += 1
                    state1 = next_state
                case _:  # Failure
                    return Failure(f'repeated({get_label(p)}) parsed fewer than minimum ({minimum}) items',
                                   state.point)
        while reps < maximum:
            match p(state1):
                case Success(res, next_state):
                    results.append(res)
                    reps += 1
                    state1 = next_state
                case _:  # Failure
                    break
        return Success(results, state1)

    return p_rep

def interleave(
        item: Parser[A],
        sep: Parser[Any],
        *,
        end: Parser[Any] | None = None,
        start: Parser[Any] | None = None,
        allow_empty=True
) -> Parser[list[A]]:
    """Parser interleaving items with separators and optional start/end delimiters.

    Separator, start, and end results are ignored.
    Returns list of item results.

    """
    @parser((f'interleave{"" if allow_empty else "1"}'
             f'({get_label(start)} {get_label(item)} {get_label(sep)} {get_label(end)})'))
    def interleaving(state: ParseState) -> ParseResult[list[A]]:
        state1 = state
        if start:
            match start(state):
                case Success(_, next_state):
                    state1 = next_state
                case parsed:  # Failure
                    return parsed

        results = []
        item_state: ParseState | None = None
        while True:
            match item(state1):
                case Success(res, next_state):
                    results.append(res)
                    state1 = next_state
                    item_state = state1
                case parsed:  # Failure
                    assert isinstance(parsed, Failure)
                    if item_state is None and not allow_empty:
                        return Failure(f'Expected items ({get_label(item)}) in interleave: {parsed.message}',
                                       parsed.pos, parsed.data)
                    break

            match sep(state1):
                case Success(_, next_state):
                    state1 = next_state
                case _:  # Failure
                    break

        if end is not None:
            match end(item_state or state1):
                case Success(_, next_state):
                    return Success(results, next_state)
                case parsed:  # Failure
                    return parsed

        return Success(results, item_state or state1)

    return interleaving

def peek(p: Parser[A]) -> Parser[A]:
    "Returns a parser that parses ahead without advancing the state."
    @parser(f'peek({get_label(p)})')
    def peek_ahead(state: ParseState) -> ParseResult[A]:
        match p(state):
            case Success(result, _):
                return Success(result, state)
            case parsed:  # Failure
                return parsed
    return peek_ahead


#
# Basic Combinators
#

@parser('eof')
def eof(state: ParseState) -> ParseResult[bool]:
    "Parser that only succeeds at the end of the input."
    _, more = state.require(1)
    if more:
        return Failure('Expected end of input', state.point)
    return Success(True, state)

def any_char() -> Parser[str]:
    "Returns a parser that expects any single character."
    @parser('any_char')
    def this_char(state: ParseState) -> ParseResult[str]:
        input, enough = state.require(1)
        if enough:
            return Success(input, state.advance(1))
        return Failure("Expected a character", state.point)
    return this_char

def char(c) -> Parser[str]:
    "Returns a parser that expects a specific character."
    @parser(f'char({c})')
    def this_char(state: ParseState) -> ParseResult[str]:
        input, enough = state.require(1)
        if enough and c == input:
            return Success(c, state.advance(1))
        return Failure(f"Expected character {c}", state.point, {'expected': c})
    return this_char

def char_in(chars) -> Parser[str]:
    "Returns a parser that expects a character in a given set."
    @parser(f'char_in({chars})')
    def this_char(state: ParseState) -> ParseResult[str]:
        input, enough = state.require(1)
        if enough and input[0] in chars:
            return Success(input, state.advance(1))
        return Failure(f"Expected character in [{chars}]", state.point, {'expected': chars})
    return this_char

def char_satisfies(pred, description='predicate') -> Parser[str]:
    "Returns a parser that expects a character satisfying a predicate."
    @parser(f'char_satisfies({description})')
    def good_char(state: ParseState) -> ParseResult[str]:
        input, enough = state.require(1)
        if enough and pred(input):
            return Success(input, state.advance(1))
        return Failure(f"Expected character satisfying {description}", state.point)
    return good_char

def lexeme(s: str) -> Parser[str]:
    "Returns a parser that expects a specific string."
    n = len(s)

    @parser(f'lexeme({s})')
    def this_str(state: ParseState) -> ParseResult[str]:
        input, enough = state.require(n)
        if enough and s == input:
            return Success(s, state.advance(n))
        return Failure(f"Expected string {s}", state.point)

    return this_str

def string_in(strs: list[str]) -> Parser[str]:
    "Returns a parser that matches a fixed set of strings"
    sorted_strs = sorted(strs, key=lambda s: len(s), reverse=True)  # longest first
    joined = "|".join(map(re.escape, sorted_strs))

    @parser(f'string_in({", ".join(strs)})')
    def words(state: ParseState) -> ParseResult[str]:
        input = state.view()
        m = re.match(joined, input)
        if m:
            matched = m.group(0)
            return Success(matched, state.advance(len(matched)))
        return Failure(f'Expected one of {", ".join(strs)}', state.point, {'expected': strs})

    return words

@parser('whitespace')
def whitespace(state: ParseState) -> ParseResult[str]:
    "This has type Parser str"
    m = re.match(r'\s+', state.view())
    if m:
        matched = m.group(0)
        return Success(matched, state.advance(len(matched)))
    return Failure("Expected whitespace", state.point)

def regex(re_in: str, flags: re.RegexFlag = re.NOFLAG, group=0) -> Parser[str]:
    pattern = re_in[1] if re_in.startswith('^') else re_in

    @parser(f'regex(/{pattern}/{flags}[{group}])')
    def regexP(state: ParseState) -> ParseResult[str]:
        input = state.view()
        m = re.match(pattern, input, flags)
        if m:
            matched = m.group(group)
            return Success(matched, state.advance(len(m.group(0))))
        return Failure(f'Expected match of regex /{pattern}/ with flags {flags}', state.point,
                       {'pattern': pattern, 'flags': flags, 'group': group})

    return regexP

def strings(ps: list[Parser[str]], sep="") -> Parser[str]:
    """Runs string parsers in succession returning string joined by `sep`."""

    @parser(f'strings({", ".join(map(get_label, ps))})')
    def stringsP(state: ParseState) -> ParseResult[str]:
        state1 = state
        concat = []
        for p in ps:
            parsed = p(state1)
            match parsed:
                case Success(res, next_state):
                    concat.append(res)
                    state1 = next_state
                case _:  # Failure
                    return Failure('In strings, {get_label(p)} failed: {parsed.message}',
                                   parsed.pos, parsed.data)
        joined = sep.join(concat)
        return Success(joined, state.advance(len(joined)))

    return stringsP

letter = char_satisfies(str.isalpha)
digit = char_satisfies(str.isdigit)
natural_number = fmap(regex(r'(?:[1-9][0-9]*|0)'), int)
integer = fmap(regex(r'(?:-?[1-9][0-9]*|0)'), int)
boolean = fmap(regex(r'true|false|yes|no|0|1', re.IGNORECASE),
               lambda s: True if s[0].lower() in ['t', 'y', '1'] else False)  # type: ignore

def enum(enum_cls: type[E.Enum]) -> Parser[E.Enum]:
    "Parses the string repr of a value in a specified enum class"
    e_vals = {str(e.value): e for e in enum_cls}
    enum_val = fmap(string_in(list(e_vals.keys())), lambda s: e_vals[s])
    return parser(f'enum({enum_cls})', enum_val)

def balanced_delimiters(opening: str, closing: str, seen_opening=False) -> Parser[tuple[str, list[int]]]:
    """Matches a string that is balanced with respect to specified delimiters.

    If `seen_opening` is True, the opening delimiter is assumed to have been
    previously seen and processed (and not be present in the string).

    The delimiters must be distinct.

    Parsed value is a tuple consisting of the balanced string
    and a list of delimiter indices with signs indicating
    opening (+) or closing (-).

    """
    @parser(f'balanced("{opening}", "{closing}")')
    def balancedP(state: ParseState) -> ParseResult[tuple[str, list[int]]]:
        input = state.view()
        point = state.point
        n = len(input)
        len_open = len(opening)
        len_close = len(closing)

        if n < (len_close if seen_opening else len_close + len_open):
            return Failure(f'Expected balanced delimiters {opening}..{closing}: insufficient input.', point)
        if not seen_opening and not input.startswith(opening):
            return Failure(f'Expected balanced delimiters {opening}..{closing}: missing {opening}.', point)

        index = 0 if seen_opening else len_open
        count = 1
        positions = [] if seen_opening else [0]

        while count > 0 and point + index < n:
            if input[index:].startswith(opening):
                count += 1
                positions.append(index)
                index += len_open
            elif input[index:].startswith(closing):
                count -= 1
                positions.append(-index)
                index += len_close
            else:
                index += 1

        if count != 0:
            return Failure(f'Expected balanced delimiters {opening}..{closing}', point)

        return Success((input[:index], positions), state.advance(index))

    return balancedP


#
# Convenient Entry Point
#

def parse(input: str, p: Parser[A], start=0) -> ParseResult[A]:
    """Parses an input string with a given parser and optional start position."""
    return p(ParseState(input, start))


#
# Experimental
#

def lazy(fn, label=""):
    """Constructs a lazy parser from a generator function.

    If `fn` is a string, acts as a decorator with the string
    as label. Otherwise, `fn` must be a generator function
    with at least one yield.

    This is useful for a do-notation like specification
    of a parser that can handle recursive definitions.
    See test_lazy in test_combinators.py for examples.

    """
    if isinstance(fn, str):
        return lambda f: lazy(f, fn)

    @wraps(fn)
    def lazily(state: ParseState) -> ParseResult[A]:
        generator = fn()

        state1 = state
        result = None

        try:
            while True:
                parser = generator.send(result)
                match parser(state1):
                    case Success(res, next_state):
                        result = res
                        state1 = next_state
                    case parsed:  # Failure
                        return parsed
        except StopIteration as finished:
            if callable(finished.value):  # A parser, so parse it
                p = finished.value
                return p(state1)
            # A value constructed from the parse
            return Success(finished.value, state1)
    return parser(f'lazy({label})', lazily)
