#
# A simple regex parser that converts a regular expression string to a tree.
#
# Supports the regex constructs typical of R and Python. Lookaround
# assertions are not yet supported, and we do not explicitly handle
# the /x flag through 1. treating space as literal text, and 2. not
# handling comments. Extensions to handle these are straightforward.
#

import enum as E   # enum is a combinator
import typing

from collections.abc import Iterable
from typing          import cast

from combinators import (Parser, ParseResult, Success, parse, failed,
                         pure, fmap, use, pipe, fix,
                         seq, follows, followedBy, between,
                         alt, alts, some, optional,
                         char, char_in, string, sjoin, string_in, regex,
                         natural_number)


#
# Data representation of a regular expression
#
# The regexp will be stored as a tree, with each node a specific
# subclass of a base RegExp type.
#
# We have a RegExp subtype for each of the following
#
# 1.  No-ops (absorbs comments in /x)
# 2.  Literal text, including escaped metacharacters
# 3.  Dot .
# 4.  Special escape sequences (e.g., \w, \d)
# 5.  Character classes
# 6.  Zero-length assertions (e.g., ^, \Z) without arguments
# 7.  Groups (plain, capture, named [by identifiers only])
# 8.  Alternation
# 9.  Repetition (?, *, +, {}, and lazy versions)
# 10. Concatenation of regular expressions
#
# Lookaround assertions and /x spacing and comments are
# not yet supported. See EXERCISE below.
#

class RegExp:
    "Base node type, either leaf or branch."

    def __init__(self, leaf):
        self._atomic = bool(leaf)

    @property
    def is_leaf(self):
        return self._atomic

    def __repr__(self):
        cname = self.__class__.__name__
        members = [f'{k}={v}' for k, v in self.__dict__.items()]
        return f'{cname}({", ".join(members)})'

class RegExpLeaf(RegExp):
    def __init__(self):
        super().__init__(True)

class RegExpBranch(RegExp):
    def __init__(self):
        super().__init__(False)

# Atomic pattern components

class Literal(RegExpLeaf):
    "Literal text"
    def __init__(self, text: str):
        self.text = text

class NoOp(RegExpLeaf):
    "A no-op, with optional comment (e.g., with /x flag)."
    def __init__(self, comment: str | None = None):
        self.comment = comment

    @classmethod
    def is_empty(cls, obj):
        if isinstance(obj, NoOp) and obj.comment is None:
            return True
        return False

class Dot(RegExpLeaf):
    "The dot . metacharacter"
    pass

class EscapeSequence(RegExpLeaf):
    """A special escape sequence, e.g., \\w, \\d.

    This can include sequences with arguments like \\uXXXX, \\p{...}, \\N{...},
    but those are not currently supported

    For assertions like \\A and \\Z, see Assertions. Those are not included here.

    """
    VALID_ESCAPES = ["w", "W", "d", "D", "s", "S"]

    def __init__(self, text: str, arg: str | None = None):
        self.text = text
        self.arg = arg

class CharacterClass(RegExpLeaf):
    "Literal text"
    def __init__(self, chars: str, complement=None):
        if chars.startswith('^'):
            self.chars = chars[1:]
            self.complement = True  # complement ignored if ^ starts class
        else:
            self.chars = chars
            self.complement = bool(complement)

class RegexAssertion(E.StrEnum):
    BOL = "^"
    EOL = "$"
    BEG_STRING = r'\A'
    END_STRING = r'\Z'
    WORD_BOUNDARY = r'\b'
    NON_WORD_BOUNDARY = r'\B'

class Assertion(RegExpLeaf):
    "A zero-length assertion without arguments (i.e., excluding lookarounds)"
    VALID_ASSERTIONS = ["^", "$", r'\A', r'\Z', r'\b', r'\B', ]

    def __init__(self, assertion):
        if assertion not in Assertion.VALID_ASSERTIONS:
            raise ValueError(f'Unrecognized zero-length assertion {assertion}')
        self.assertion = assertion

# Aggregate pattern components

class Concat(RegExpBranch):
    "Concatenation of one or more regex's."
    def __init__(self, res: Iterable[RegExp]):
        self.children = res

    @classmethod
    def make(cls, res: list[RegExp]) -> RegExp:
        if len(res) == 1:
            return res[0]
        return Concat(res)

class RegexGroup(E.StrEnum):
    PLAIN = "NonCapturing"
    CAPTURE = "Capturing"
    NAMED = "Named"

class Group(RegExpBranch):
    "Concatenation of one or more regex's."
    def __init__(self, regex: RegExp, gtype: RegexGroup, name: str | None = None):
        self.type = gtype
        self.child = regex
        if gtype == RegexGroup.NAMED:
            self.name = name or ""

class Alternation(RegExpBranch):
    "Alternation between two or more regexes. (Alternation of a single regex should be the identity.)"
    def __init__(self, regexes: Iterable[RegExp]):
        self.children = regexes

class RegexModifier(E.StrEnum):
    OPTIONAL = "Optional"
    MANY = "Many"
    SOME = "Some"
    RANGE = "Range"

class Repetition(RegExpBranch):
    "Repetition of a regex with specified range"
    def __init__(self, regex: RegExp, mod_type: int | tuple[int, int] | str | RegexModifier, lazy=False):
        # Note: we do not check validity of range here, we leave that to interpreter
        match mod_type:
            case '?' | RegexModifier.OPTIONAL:
                self.type = RegexModifier.OPTIONAL
                self.minimum = 0
                self.maximum: int | None = 1  # None is infinity
            case '*' | RegexModifier.MANY:
                self.type = RegexModifier.MANY
                self.minimum = 0
                self.maximum = None
            case '+' | RegexModifier.SOME | RegexModifier.RANGE:  # Empty Range == Some
                self.type = RegexModifier.SOME
                self.minimum = 1
                self.maximum = None
            case int(n):
                self.type = RegexModifier.RANGE
                self.minimum = n
                self.maximum = n
            case (int(m), int(n)):
                self.type = RegexModifier.RANGE
                self.minimum = m
                self.maximum = n
            case _:
                raise ValueError(f'Unrecognized modifier type {mod_type}')
        self.child = regex
        self.lazy = lazy

class RegexLookaround(E.StrEnum):
    POS_AHEAD = "PositiveLookahead"
    NEG_AHEAD = "NegativeLookahead"
    POS_BEHIND = "PositiveLookbehind"
    NEG_BEHIND = "NegativeLookbehind"

    # Not currently supported
# EXERCISE. Add support for the four lookaround assertions, here
# and in the main parser. Suggestion: write a parser function
# lookaround(regex) similar to group() below and put it in
# the main list.
class Lookaround(RegExpBranch):
    "A zero-length lookaround assertion"
    def __init__(self, r: RegExp, atype: RegexLookaround):
        self.type = atype
        self.child = r



#
# Helpers
#

def some_str(sp: Parser[str], sep="") -> Parser[str]:
    return fmap( some(sp), lambda rs: sep.join(rs) )

def join(rs: Iterable[RegExp | typing.Literal['|']]) -> RegExp:
    """Simplifies a concatenated sequence of regular expressions.

    Steps include:
    1. Handle alternation and concatenation
    2. Filtering out empty No-Ops
    3. Reducing consecutive literals to one Literal Node

    """
    alternated: list[RegExp] = []
    concatenated: list[RegExp] = []
    last_literal: Literal | None = None
    for r in rs:
        if NoOp.is_empty(r):
            continue  # Filter this out

        # Merge consecutive Literals
        if isinstance(r, Literal):
            if last_literal is not None:
                last_literal = Literal(last_literal.text + r.text)
            else:
                last_literal = r
            continue
        elif last_literal is not None:
            concatenated.append(last_literal)
            last_literal = None

        # Handle alternation or just collect
        if r == '|' and len(concatenated) == 0:
            alternated.append(Literal(""))  # Empty string
        elif r == '|':
            alternated.append(Concat.make(concatenated))
            concatenated = []
        elif isinstance(r, Concat):
            concatenated.extend(r.children)
        else:
            concatenated.append(r)
    # Clean up pending literal
    if last_literal is not None:
        concatenated.append(last_literal)
    # Clean up pending concats
    if len(concatenated) > 0:
        alternated.append(Concat.make(concatenated))
    else:
        alternated.append(Literal(""))  # Empty string
    return Alternation(alternated) if len(alternated) > 1 else alternated[0]

#
# Regex Parser Components
#

LITERAL_CHARS = r'[^][?*+.|^$(){}\\]'
META_CHARS = r'[][?*+.|^$(){}\\]'

# Escape characters of escape characters, literal text
unescape = fmap(sjoin(char('\\'), char('\\')), Literal)
unescapes = fmap(some_str(sjoin(char('\\'), char('\\'))), Literal)

# An escaped metacharacter
escaped = fmap(follows(char("\\"), regex(META_CHARS)), Literal)

# Literal char or text
literal_char = fmap(regex(LITERAL_CHARS), Literal)
literal = fmap(regex(fr'{LITERAL_CHARS}+'), Literal)

# Special escape sequences
special = fmap( follows(char("\\"), char_in(EscapeSequence.VALID_ESCAPES)), EscapeSequence )

# Zero-length assertions without arguments
assertion = fmap( string_in(Assertion.VALID_ASSERTIONS), Assertion )

# Character classes
cclass = fmap( between(char('['), regex(r'\^?\]?[^]]+'), char(']')), CharacterClass)

egroup = char(')')
bgroup = follows(
    char('('),
    optional(
        alts(
            use( string(r'?:'), (RegexGroup.PLAIN, None) ),
            fmap( regex(r'\?P<([-A-Za-z_]+)>', group=1), lambda name: (RegexGroup.NAMED, name) )
        ),
        cast(tuple[RegexGroup, None | str], (RegexGroup.CAPTURE, None))
    )
)

def group(regexp: Parser[RegExp]) -> Parser[RegExp]:
    "Parser matching a group around another regex."
    return fmap( followedBy(seq(bgroup, regexp), egroup),
                 lambda b_r: Group(b_r[1], b_r[0][0], b_r[0][1]) )  # type: ignore

# Repetition modifiers
repeat: Parser[str | tuple[int, int]] = alts(
    char('?'),
    char('*'),
    char('+'),
    between(
        char('{'),
        pipe(natural_number, lambda m: seq(pure(m), optional(follows(char(','), natural_number), m))),
        char('}'))
)

req_modifier = seq(repeat, optional(char('?')))
opt_modifier = optional(req_modifier)

# Helpers for aggregate parsers

def alternation(regexp):
    # ATTN: Alternation reaches all the way to the enclosing group
    return fmap( follows(char('|'), regexp), lambda r: Alternation([r]) )

def repetition(p: Parser[RegExp], required=False) -> Parser[RegExp]:
    def wrap_modifier(base_repl: tuple[RegExp, tuple[str | tuple[int, int], str | None] | None]) -> RegExp:
        basic, repl = base_repl
        if repl is None:
            return basic
        rep, lazy = repl
        is_lazy = lazy is not None
        if isinstance(basic, Literal) and len(basic.text) > 1:
            # Manage last character, e.g., abc* -> Concat(ab, Repetition(c, '*'))
            head = Literal(basic.text[:-1])
            tail = Repetition(Literal(basic.text[-1]), rep, is_lazy)
            return Concat([head, tail])
        return Repetition(basic, rep, lazy=is_lazy)

    if required:
        mod: Parser[tuple[str | tuple[int, int], str | None] | None] = req_modifier  # type: ignore
    else:
        mod = opt_modifier
    return fmap( seq(p, mod), wrap_modifier )

def base(regexp):
    "Regex components that can be distinguished by their prefix."
    return alts(
        repetition(unescapes),
        repetition(special),
        assertion,
        repetition(escaped),
        repetition(char('.')),
        repetition(literal),
        repetition(cclass),
        repetition(group(regexp))
    )


#
# Main Regex Parser
#

@fix
def regexp(regexp):
    "Full regular expression parser."
    term = alt(base(regexp), char('|'))
    return fmap( some(term), join )

def parse_regexp(re_str) -> RegExp:
    """Parses a string encoding a regular expression, returning a RegExp tree on success.

    Raises an error if parsing fails.

    """
    parsed: ParseResult[RegExp] = parse(re_str, regexp)
    if failed(parsed):
        raise ValueError(f'Regex parsing failed at position {parsed.pos}: {parsed.message}')
    assert isinstance(parsed, Success)
    return parsed.result
