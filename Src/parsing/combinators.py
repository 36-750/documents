"""A quick parser combinator implementation.

A wide range of combinators are implemented. This includes recursive
(fixpoint) parsers and some other goodies.

Parsers are implemented as a function type with decorators that can
convert suitable functions to parsers.

A variety of exercises are included in comments sprinkled throughout
the code. These points to extensions, applications, and alternatives.

"""

# The following pylint warnings are annoying and repeated noise,
# so I'm disabling them for a little peace and quiet.
# pylint: disable=invalid-name, redefined-outer-name

from __future__ import annotations

import re
import enum as E

from collections.abc   import Iterable
from dataclasses       import dataclass
from functools         import wraps
from typing            import Callable, cast
from typing_extensions import Any, TypeGuard

#
# Types
#

class ParseError(Exception):
    """Custom error thrown on parsing errors."""
    def __init__(self, message, data=None):
        super().__init__(message)
        self.data = data or {}

type Position = int
type ErrorMesg = str

# EXERCISE. ParseState takes source to be type str. Adjust the implementation
#     to handle types str and bytes so that binary files can be parsed.
#     What needs to change? What is coupled here? Note that this does not
#     require that you change str parsers below to handle both, just that
#     you can parse sources that can be bytes or text.
#
# EXERCISE. We are using strings here as the source, but better still would
#     be to read input from a stream, either one character at a time
#     or in specified chunks. Adjust this code in Python to handle use
#     StringIO and BytesIO streams  from the io package, without holding
#     the entire string in memory.  This requires changing adjusting
#     the ParserState approach (for instance, you do not have to keep
#     already processed input after a successful parse as it does now).
#     Anything that uses the view() needs to be reconsidered, but all
#     except the regexp parser can be easily adjusted.  You can drop
#     the regexp parser in this case, or offer a method for reading
#     the entire stream and put a warning in the documentation.
#
#     Note that the primitive `single` described in class is relevant
#     in this case. As is the `peek` primitive. This is a good one
#     to try; come talk to me with questions.

@dataclass(frozen=True)   # Can add slots=True here to make more efficient
class ParseState:
    """Current, immutable state of a parser.

    source :: an input source, currently the entire input string
        (Note: can include `bytes` as a valid source type with a little work.)
    point :: an integer giving the current index into the source string
        If initialized as negative, converted to a position counting from
        the end of the input source.
    start :: the starting position in the source, for tracking progress.
        Defaults to point.

    """
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
        """Advances the input pointer by the specified amount."""
        if by == 0:
            return self
        return ParseState(self.source, self.point + by, self.start)

    def available(self) -> int:
        """Returns the number of tokens remaining in source."""
        n = len(self.source)
        if self.point < n:
            return n - self.point
        return 0

@dataclass
class Success[A]:
    """Result of a successful parsing step with its associated parser state."""
    result: A
    state: ParseState

@dataclass
class Failure:
    """Result of a failed parse with message, pos, and data describing the failure."""
    message: ErrorMesg
    pos: Position
    data: dict | None = None


type ParseResult[R] = Success[R] | Failure

# type Parser a = Parser (ParserState -> ParseResult a)
#
# We keep it simple here for the moment, just using functions and
# assigning the parser label for each parser. The label is attached
# with the @parser(label) decorator. (The function parser can also
# be used directly.)
#
# EXERCISE: Define Parser as a generic class.
# The class should be callable (i.e., have a __call__ method) and a
# constructor that takes a parsing function and a label and return
# an instance of the class. Using the `inspect` module and
# `inspect.isgeneratorfunction`, this can subsume the functionality
# of the @do decorator below, making this more generally friendly
# and useful.
#
# This change should require only localized changes to the decorator
# and code for the class, without changing almost any other code.
#
# Among the advantages of having a Parser class: we can overload
# operators for commonly used operations. For instance, we can
# overload '|' to alt, '+' to seq, '>>' and '<<' to fmap (in both
# directlys), '>>=' and '<<=' to pipe (in both directions), or
# something similar (e.g., '^' and '&' for fmap in both directions,
# '>>' and '<<' for pipe, and say '@' for use).
#
# A second advantage is that we can make recursive definitions
# easier by defining proxy references, where we define an empty
# "forward reference" instance of the Parser that gives a reference
# to use in a later definition and a method that "fills in" the
# object the properties of another parser.
#
# EXERCISE: Define overloading of operators in the Parser class.
# Don't overdo it; the operators should make sense and have
# precedence that seems natural. Only use the main operations; you
# don't need to cover every operator. Be sure to handle both the
# regular and r* versions. See
#
#   https://docs.python.org/3/reference/datamodel.html
#
# for details.
#
# EXERCISE: Implement a proxy() class method on Parser and a
# replicate() method on a special subtype of the Parser class. The
# proxy method should make a special instance of the Parser class
# (suggestion: use a special subclass) that is "empty" (or optinally
# labeled) and that raises an error if used for parsing. The
# replicate method (defined on the proxy only) should take a
# (non-proxy) parser and assume its identity: taking on its parser
# and label while maintaining its original object reference. Use
# this to define a recursive parser like sexp in the test examples.
#

type Parser[R] = Callable[[ParseState], ParseResult[R]]

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
    set_label(f, label or f.__name__ or "?")
    return f


#
# Helpers
#

def identity(x):
    "The identity function"
    return x

def str_cat(strs: list[str], sep=""):
    """Joins a list of strings with the given separator."""
    return sep.join(strs)

def merge_data(data1: dict | None, data2: dict | None) -> dict | None:
    """Merges the data fields of a Failure into a valid data field.

    Returns a merged dictionary or None, treating None as empty data.

    """
    if data1 is None:
        return data2
    if data2 is None:
        return data1
    return data1 | data2


#
# Infrastructure
#

# EXERCISE: Convert this code to use the FPC types and structures.
# This would, for example change the Parser type to a wrapping
# but callable! class that inherits from Monad among other
# things. Notice that ParseResult a is just Either Failure (Success a)
# but as done here does not have the advantages of this structure.
# This is a worthwhile exercise, and feel free to talk with me
# if you are considering it.

def failed[A](parse: ParseResult[A]) -> TypeGuard[Failure]:
    "Tests whether the result of a parse is a Failure"
    return isinstance(parse, Failure)

def succeeded[A](parse: ParseResult[A]) -> TypeGuard[Success[A]]:
    "Tests whether the result of a parse is a Success"
    return isinstance(parse, Success)

def set_label(parser, label: str) -> None:
    "Assigns a label attribute to a parsing function, returning the function."
    setattr(parser, 'parser_label', label)
    return parser

def get_label(parser, default="?") -> str:
    "Returns a parsing function's label attribute or default if none."
    if parser is None:
        return ""
    return getattr(parser, 'parser_label', default)

@parser('void')
def void[A](state: ParseState) -> ParseResult[A]:
    "Parser that always fails"
    return Failure("Void parser", state.point)

def failure[A](reason: str) -> Parser[A]:
    "Parser that fails with the stated reason."
    def fails(state: ParseState) -> ParseResult[A]:
        return Failure(reason, state.point)
    return parser(fails, f'fails({reason})')

def pure[A](x: A) -> Parser[A]:
    "Parser that always succeeds without advancing point, returning `x`."
    @parser(f'pure({x})')
    def pureP(state: ParseState) -> ParseResult[A]:
        return Success(x, state)
    return pureP

def fmap[A, B](p: Parser[A], f: Callable[[A], B]) -> Parser[B]:
    "Parser whose result is the transforms a parser `p` by a function `f`."
    @parser(f'fmap({get_label(p)})')
    def mapped(state: ParseState) -> ParseResult[B]:
        parse_A = p(state)
        match parse_A:
            case Success(resA, stateA):
                return Success(f(resA), stateA)
            case _:  # Failure
                return parse_A
    return mapped

def pipe[A, B](p: Parser[A], f: Callable[[A], Parser[B]]) -> Parser[B]:
    "Parser that runs a parser than another parser that depends on the result of the first."
    @parser(f'pipe({get_label(p)})')
    def piped(state: ParseState) -> ParseResult[B]:
        parse_A = p(state)
        match parse_A:
            case Success(resA, stateA):
                return f(resA)(stateA)
            case _:  # Failure
                return parse_A
    return piped

def use[A, B](p: Parser[A], value: B) -> Parser[B]:
    "Parser that yields a specified value when the given parser succeeds."
    return fmap(p, lambda _: value)


#
# Higher-Order Combinators
#
# EXERCISE. Implement additional parser combinators or factories that
#     are usable (and reusable) in practical situations. For instance,
#     parsing LaTeX commands, parsing R statistical model expressions,
#     combinators for expressing command line options, ....

def seq[A, B](p: Parser[A], q: Parser[B]) -> Parser[tuple[A, B]]:
    """Parser runs two parsers in sequence, collecting results in a tuple.

    This fails immediately when either parser fails.

    """
    sequenced = pipe(p, lambda x: pipe(q, lambda y: pure((x, y))))   # type: ignore
    return parser(sequenced, f'seq({get_label(p)}, {get_label(q)})')

def followedBy[A, B](p: Parser[A], q: Parser[B]) -> Parser[A]:
    "Parser that runs two parsers in sequence, giving the result of the first."
    sequenced = pipe(p, lambda x: pipe(q, lambda y: pure(x)))   # type: ignore
    return parser(sequenced, f'followedBy({get_label(p)}, {get_label(q)})')

def follows[A, B](p: Parser[A], q: Parser[B]) -> Parser[B]:
    "Parser that runs two parsers in sequence, giving the result of the second."
    sequenced = pipe(p, lambda x: pipe(q, pure))
    return parser(sequenced, f'follows({get_label(p)}, {get_label(q)})')

def between[A, B](p: Parser[B], q: Parser[A], r: Parser[B]) -> Parser[A]:
    "Parser that runs three parsers in sequence, returning the second result."
    sequenced = followedBy(follows(p, q), r)
    return parser(sequenced, f'between({get_label(p)}, {get_label(q)}, {get_label(r)})')

def chain(*ps: Parser) -> Parser[list]:
    """Parser that runs a list of parsers in sequence, failing if any fail.

    The parser returns a list of the results of the component parsers,
    in order. The parser fails immediately if any parser fails.

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
                    assert isinstance(parsed, Failure), f'Expected a failure: {parsed}'
                    return Failure(f'chained parsed failed: {parsed.message}', parsed.pos, parsed.data)
        return Success(results, state1)
    return chained

def alt[A, B](p: Parser[A], q: Parser[B]) -> Parser[A | B]:
    "Parser that runs one parser, or another if the first fails."
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
    "Parser that tries given parsers in order until one succeeds and fails if all fail."
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

def optional[A](p: Parser[A], default: A | None = None) -> Parser[A | None]:
    """Parser that runs a parser, returning its result on success or a default on failure.

    This always succeeds, so beware making this the sole target of an infinite repetition.

    """
    opt = alt(p, pure(default))
    return parser(opt, f'{get_label(p)}?')

def many[A](p: Parser[A]) -> Parser[list[A]]:
    """Parser that runs given parser zero or more times, returning list of results.

    This always succeeds. Warning: If the given parser succeeds on empty input,
    this parser will not terminate.

    """
    @parser(f'{get_label(p)}*')
    def p_star(state: ParseState) -> ParseResult[list[A]]:
        results = []
        state1 = state
        while True:
            parsed = p(state1)
            match parsed:
                case Success(res, next_state):
                    results.append(res)
                    state1 = next_state
                case _:  # Failure
                    break
        return Success(results, state1)
    return p_star

def some[A](p: Parser[A]) -> Parser[list[A]]:
    """Parser that runs given parser one or more times, returning list of results.

    This fails unless the given parser succeeds at least once.

    """
    @parser(f'{get_label(p)}+')
    def p_plus(state: ParseState) -> ParseResult[list[A]]:
        parsed = p(state)

        if failed(parsed):
            return parsed

        assert isinstance(parsed, Success)   # grrr Python typing...
        results = [parsed.result]
        state1 = parsed.state
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

MANY_REPS = 1 << 32  # Effectively infinite

def repeated[A](p: Parser[A], minimum: int = 0, maximum: int = MANY_REPS) -> Parser[list[A]]:
    """Parser that runs given parser an inclusive range of times.

    The parser succeeds if the given parser succeeds at least `minimum` times in a row.
    Here, `minimum` and `maximum` must be non-negative with the latter at least as
    large as the former. `maximum` defaults to a large number (2**32).

    """
    if minimum < 0 or minimum > maximum or maximum < 0:
        raise ValueError('repeated parser requires non-negative minimum <= maximum')

    @parser(f'{get_label(p)}{{{minimum},{maximum}}}')
    def p_rep(state: ParseState) -> ParseResult[list[A]]:
        state1 = state
        reps = 0
        results = []
        while reps < maximum:
            match p(state1):
                case Success(res, next_state):
                    results.append(res)
                    reps += 1
                    state1 = next_state
                case _:  # Failure
                    if reps < minimum:
                        return Failure(f'repeated({get_label(p)}) parsed fewer than minimum ({minimum}) items',
                                       state.point)
                    break
        return Success(results, state1)

    return p_rep

def interleave[A](
        item: Parser[A],
        sep: Parser[Any],
        *,
        end: Parser[Any] | None = None,
        start: Parser[Any] | None = None,
        allow_empty=False
) -> Parser[list[A]]:
    """Parser that interleaves items with separators and optional start/end delimiters.

    Returns a list of results from the `item` parser. The results of
    the `sep`, `start`, and `end` parsers are ignored. Note that when `end`
    is supplied, a match of `sep` is NOT required between the last item
    and the end.

    If `allow_empty` is True, then an empty list of items is allowed. This is
    most useful if `start` or `end` is supplied.

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

def peek[A](p: Parser[A]) -> Parser[A]:
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
# Basic Parsers and Parser Factories
#

@parser('eof')
def eof(state: ParseState) -> ParseResult[bool]:
    "Parser that only succeeds at the end of the input."
    _, more = state.require(1)
    if more:
        return Failure('Expected end of input', state.point)
    return Success(True, state)

@parser('any_char')
def any_char(state: ParseState) -> ParseResult[str]:
    "Parser that succeeds on any single character."
    token, enough = state.require(1)
    if enough:
        return Success(token, state.advance(1))
    return Failure("Expected a character", state.point)

@parser('whitespace')
def space(state: ParseState) -> ParseResult[str]:
    "Parser that succeeds on any sequence of consecutive whitespace characters."
    m = re.match(r'\s+', state.view())
    if m:
        matched = m.group(0)
        return Success(matched, state.advance(len(matched)))
    return Failure("Expected whitespace", state.point)

@parser('horizontal-space')
def hspace(state: ParseState) -> ParseResult[str]:
    "Parser that succeeds on any sequence of consecutive horizontal whitespace characters."
    # Ideally we'd like \p{HorizontalSpace} or \h, but Python doesn't support
    # Could use the regex module as a replacement for re with extra dependency
    m = re.match(r'[^\S\n\v\f\r\u2028\u2029]+', state.view())
    if m:
        matched = m.group(0)
        return Success(matched, state.advance(len(matched)))
    return Failure("Expected horizontal space", state.point)

@parser('vertical-space')
def vspace(state: ParseState) -> ParseResult[str]:
    "Parser that succeeds on any sequence of consecutive vertical whitespace characters."
    m = re.match(r'[\n\v\f\r\u2028\u2029]+', state.view())
    if m:
        matched = m.group(0)
        return Success(matched, state.advance(len(matched)))
    return Failure("Expected vertical space", state.point)

def char(c) -> Parser[str]:
    "Parser that matches a specific character."
    @parser(f'char({c})')
    def this_char(state: ParseState) -> ParseResult[str]:
        token, enough = state.require(1)
        if enough and c == token:
            return Success(c, state.advance(1))
        return Failure(f"Expected character {c}", state.point, {'expected': c})
    return this_char

def char_in(chars: str | list[str]) -> Parser[str]:
    "Parser that matches a character in a given set."
    @parser(f'char_in({chars})')
    def this_char(state: ParseState) -> ParseResult[str]:
        token, enough = state.require(1)
        if enough and token in chars:
            return Success(token, state.advance(1))
        return Failure(f"Expected character in [{chars}]", state.point, {'expected': chars})
    return this_char

def char_not_in(chars: str | list[str]) -> Parser[str]:
    "Parser that matches a character NOT in a given set."
    @parser(f'char_not_in({chars})')
    def char_not(state: ParseState) -> ParseResult[str]:
        token, enough = state.require(1)
        if enough and token[0] not in chars:
            return Success(token, state.advance(1))
        return Failure(f"Expected character not in [{chars}]", state.point, {'not expected': chars})
    return char_not

def char_satisfies(pred, description='predicate') -> Parser[str]:
    "Parser that matches a character satisfying a given predicate."
    @parser(f'char_satisfies({description})')
    def good_char(state: ParseState) -> ParseResult[str]:
        token, enough = state.require(1)
        if enough and pred(token):
            return Success(token, state.advance(1))
        return Failure(f"Expected character satisfying {description}", state.point)
    return good_char

def string(s: str, transform: Callable[[str], str] = identity) -> Parser[str]:
    """Parser that matches a specific string.

    If transform is supplied, it should be a function str -> str.
    The transform is applied to the input before comparing with the
    given string. Ex: transform=str.lower with a lowercase string
    gives case insensitive comparison.

    """
    n = len(s)

    @parser(f'string({s}, {transform.__name__})')
    def this_str(state: ParseState) -> ParseResult[str]:
        tokens, enough = state.require(n)
        if enough and s == transform(tokens):
            return Success(tokens, state.advance(n))
        return Failure(f"Expected string {s}", state.point)

    return this_str

def istring(s: str) -> Parser[str]:
    "Parser like `string` but with case-insensitive comparison"
    return parser(string(s.lower(), str.lower), f'istring({s})')

def symbol(s: str, spacep: Parser[str] = space, transform: Callable[[str], str] = identity) -> Parser[str]:
    """Parser that matches a given sting followed by some notion of 'space'.

    The space is determined by the supplied parser `spacep` which parses
    the input after the string. The results of this parser are ignored.

    The `transform` argument is passed directly to string() and allows
    an optional transformation of the input string. See string().

    This is a convenience method for defining lexical components that
    account for whitespace.

    """
    return followedBy(string(s, transform), spacep)

def string_in(choices: Iterable[str]) -> Parser[str]:
    "Parser that matches any string in a fixed set."
    strs = list(choices)
    sorted_strs = sorted(strs, key=len, reverse=True)  # longest first
    joined = "|".join(map(re.escape, sorted_strs))

    @parser(f'string_in({", ".join(strs)})')
    def words(state: ParseState) -> ParseResult[str]:
        tokens = state.view()
        m = re.match(joined, tokens)
        if m:
            matched = m.group(0)
            return Success(matched, state.advance(len(matched)))
        return Failure(f'Expected one of {", ".join(strs)}', state.point, {'expected': strs})

    return words

def strings(*choices: str) -> Parser[str]:
    "Parser like `string_in` but accepts distinct string arguments."
    return parser(string_in(choices), f'strings({", ".join(choices)})')

def sjoin(*ps: Parser[str], sep="") -> Parser[str]:
    """Runs string parsers in succession returning string joined by `sep`.

    This is equivalent to fmap(chain(*ps), lambda xs: sep.join(xs)).

    """
    @parser(f'sjoin({", ".join(map(get_label, ps))})')
    def sjoinP(state: ParseState) -> ParseResult[str]:
        state1 = state
        concat = []
        for p in ps:
            parsed = p(state1)
            match parsed:
                case Success(res, next_state):
                    concat.append(res)
                    state1 = next_state
                case _:  # Failure
                    return Failure(f'In sjoin, {get_label(p)} failed: {parsed.message}',
                                   parsed.pos, parsed.data)
        joined = sep.join(concat)
        return Success(joined, state1)  # equiv state.advance(len(joined))

    return sjoinP

def regex(re_in: str, flags: re.RegexFlag = re.NOFLAG, group=0) -> Parser[str]:
    """Parser that succeeds if given regex matches at current point.

    The parser returns the matched string, or the capture group specfified
    by number in the `group` argument. The input regular expression need not
    (and should not) start with '^'.

    `flags` specifies option on regex matching; it is a RegexFlag value
        as defined in the re module of the standard library.

    Note that this combinator is a convenience; it could be simulated
    with the other combinators.

    """
    pattern = re_in[1] if re_in.startswith('^') else re_in

    @parser(f'regex(/{pattern}/{flags}[{group}])')
    def regexP(state: ParseState) -> ParseResult[str]:
        tokens = state.view()
        m = re.match(pattern, tokens, flags)
        if m:
            return Success(m.group(group), state.advance(len(m.group(0))))
        return Failure(f'Expected match of regex /{pattern}/ with flags {flags}', state.point,
                       {'pattern': pattern, 'flags': flags, 'group': group})

    return regexP

# Common lexical parsers
newline = parser(regex(r'\r?\n'), 'newline')
letter = char_satisfies(str.isalpha)
letters = some(letter)
digit = char_satisfies(str.isdigit)
digits = some(digit)
natural_number = fmap(regex(r'(?:[1-9][0-9]*|0)'), int)
integer = fmap(regex(r'(?:-?[1-9][0-9]*|0)'), int)
boolean = fmap(regex(r'true|false|yes|no|0|1', re.IGNORECASE),
               lambda s: s[0].lower() in ['t', 'y', '1'])

def enum(enum_cls: type[E.Enum]) -> Parser[E.Enum]:
    "Parses the string repr of a value in a specified enum class"
    e_vals = {str(e.value): e for e in enum_cls}
    enum_val = fmap(string_in(list(e_vals.keys())), lambda s: e_vals[s])
    return parser(enum_val, f'enum({enum_cls})')

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
        tokens = state.view()
        point = state.point
        n = len(tokens)
        len_open = len(opening)
        len_close = len(closing)

        if n < (len_close if seen_opening else len_close + len_open):
            return Failure(f'Expected balanced delimiters {opening}..{closing}: insufficient input.', point)
        if not seen_opening and not tokens.startswith(opening):
            return Failure(f'Expected balanced delimiters {opening}..{closing}: missing {opening}.', point)

        index = 0 if seen_opening else len_open
        count = 1
        positions = [] if seen_opening else [0]

        while count > 0 and point + index < n:
            if tokens[index:].startswith(opening):
                count += 1
                positions.append(index)
                index += len_open
            elif tokens[index:].startswith(closing):
                count -= 1
                positions.append(-index)
                index += len_close
            else:
                index += 1

        if count != 0:
            return Failure(f'Expected balanced delimiters {opening}..{closing}', point)

        return Success((tokens[:index], positions), state.advance(index))

    return balancedP


#
# Convenient Entry Point
#

def parse[A](tokens: str, p: Parser[A], start=0) -> ParseResult[A]:
    """Parses an input string with a given parser and optional start position.

    """
    return p(ParseState(tokens, start))


#
# Do-notation for convenient expression and recursive parsers
#

def do(fn, label=""):
    """Constructs a lazy parser from a generator function.

    This provides a syntax similar to do-notation that is often more
    convenient than `pipe` for contingent sequences of parsers. It
    can also handle recursive definitions, as shown in the example
    below.

    fn :: If `fn` is a function, it should be a generator function
        with at least one yield statement. This function is wrapped
        to convert it to a parser.

        The function should yield parsers; values received from the
        yield are the parses of the corresponding parser. (Values
        can be ignored if desired.) A return statement ends the
        parsing, returning a final value from the parser of any
        desired type. (If a parser is returned, that parser will be
        immediately run to produced a value.)

        If `fn` is a string, it acts in place of the `label` argument.
        This is the case where do() acts as a decorator with argument.

    label :: A string assigned as label for the parser, defaults to
        the empty string.

    When applied to a function, returns a parser; when applied
    with a single string argument, acts as a decorator to wrap
    a definition and convert it to a parser.

    Example:
        @do
        def triple():
            a = yield natural_number
            yield whitespace
            b = yield integer
            yield whitespace
            c = yield boolean
            return (a, b, c)

        parse('10 -20 True', triple) == (10, -20, True)

        @do
        def sexp_list():
            return (yield interleave(sexp, whitespace,
                                     start=char('('), end=char(')')))

        sexp = alt(alt(ident, integer), sexp_list)
        parse('(a b (c d 3 (e 10 g (h (i (j))))))', sexp) ==
            ['a', 'b', ['c', 'd', 3, ['e', 10, 'g', ['h', ['i', ['j']]]]]]

    """
    if isinstance(fn, str):
        return lambda f: do(f, fn)

    @wraps(fn)
    def lazily(state: ParseState) -> ParseResult:
        generator = fn()

        state1 = state
        result = None

        try:
            while True:
                p = generator.send(result)
                match p(state1):
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
    return parser(lazily, f'do({label})')


#
# Fixed-point Combinator for Recursive parsers
#
# Example:
#  ident = regex(r'[A-Za-z_][-A-Za-z_0-9?!]*')
#  opar=char('(')
#  cpar=char(')')
#
#  # With a decorator
#  @fix
#  def sexp(sexp):
#      return alt(ident, interleave(sexp, whitespace, start=opar, end=cpar))
#
#  # Or directly with a lambda
#  sexp = fix(lambda sexp: alt(ident, interleave(sexp, whitespace, start=opar, end=cpar)))
#
#  parse('(a b (c r g) ((d)) (e (f (g))))', sexp)  #=> succeeds
#  parse('(a b (c r g) (($)) (e (f (g))))', sexp)  #=> fails at the correct point

def fix(f):
    "The Z-combinator for finding fixed points in an eager language."
    def z(u):
        return f(lambda x: u(u)(x))
    return z(z)

def fix_rec(f):
    "The Z-combinator converted to a recursive function."
    return lambda x: f(fix_rec(f))(x)
