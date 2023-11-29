#
# A simple regex parser that converts a regular expression string to a tree.
#
# Supports the regex constructs typical of R and Python. Lookaround
# assertions are not yet supported, and we do not explicitly handle
# the /x flag through 1. treating space as literal text, and 2. not
# handling comments. Extensions to handle these are straightforward.
#

library(stringi)
library(stringr)
library(purrr)
library(rlang)
library(rlist)

source("combinators.r")

identity <- function(x) x


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

setClass("RegExp", slots = c(atomic = "logical"))
setClass("RegExpLeaf", contains = "RegExp")
setClass("RegExpBranch", contains = "RegExp")

RegExpLeaf <- function(...) new(..., atomic = TRUE)
RegExpBranch <- function(...) new(..., atomic = FALSE)

# Atomic pattern components

setClass("Literal", slots = c(text = "character"),  contains = "RegExpLeaf")
setClass("NoOp", slots = c(comment = "character"),  contains = "RegExpLeaf")
setClass("Dot", contains = "RegExpLeaf")
setClass("EscapeSequence", slots = c(text = "character", arg = "character"), contains = "RegExpLeaf")
setClass("CharacterClass", slots = c(chars = "character", complement = "logical"), contains = "RegExpLeaf")
setClass("Assertion", slots = c(assertion = "character"), contains = "RegExpLeaf")

# Atomic pattern constructors

RegexAssertion <- list(  # Enum
    BOL = "^", 
    EOL = "$", 
    BEG_STRING = '\\A', 
    END_STRING = '\\Z', 
    WORD_BOUNDARY = '\\b', 
    NON_WORD_BOUNDARY = '\\B'
)

VALID_ESCAPES = c("w", "W", "d", "D", "s", "S")
VALID_ASSERTIONS = map_chr(RegexAssertion, identity)

Literal <- function(text) RegExpLeaf("Literal", text = text)
NoOp <- function(comment = NULL) RegExpLeaf("NoOp", comment = comment)
Dot <- function() RegExpLeaf("Dot")

EscapeSequence <- function(text, arg) {
    if( !missing(arg) ) stop("Escape sequences with args not currently supported")

    if( !(text %in% VALID_ASSERTIONS) ) {
        stop(str_glue("Unrecognized assertion {text} in EscapeSequence"))
    }

    RegExpLeaf("EscapeSequence", text = text, arg = arg)
}

CharacterClass <- function(chars, complement) {
    chset <- chars
    compl <- FALSE
    if ( stri_startswith_fixed(chars, "^") ) {
        compl <- TRUE
        chset <- str_sub(chars, 2)
    } else if ( !missing(complement) && complement ) {
        compl <- TRUE
    }
    RegExpLeaf("CharacterClass", chars = chset, complement = compl)
}

Assertion <- function(assertion) {
    if( !(assertion %in% RegexAssertion) ) {
        stop(str_glue("Unrecognized zero-length assertion {assertion}"))
    }
    RegExpLeaf("Assertion", assertion = assertion)
}

# Aggregate pattern components

setClass("Concat", slots = c(children = "list"),  contains = "RegExpBranch")
setClass("Group", slots = c(regex = "RegExp", gtype = "character", name = "character"),
         contains = "RegExpBranch")
setClass("Alternation", slots = c(children = "list"),  contains = "RegExpBranch")
setClass("Repetition", slots = c(child = "RegExp", type = "character", lazy = "logical", 
                                 minimum = "numeric", maximum = "numeric"),
         contains = "RegExpBranch")
setClass("Lookaround", slots = c(child = "RegExp", type = "character"),
         contains = "RegExpBranch")

# Aggregate pattern constructors

RegexGroup <- list(  # Enum
    PLAIN = "NonCapturing",
    CAPTURE = "Capturing",
    NAMED =  "Named"
)

RegexModifier <- list(  # Enum
    OPTIONAL = "OPTIONAL",
    MANY = "MANY",
    SOME = "SOME",
    RANGE = "RANGE"
)

RegexLookaround <- list(  # Enum
    POS_AHEAD = "PositiveLookahead", 
    NEG_AHEAD = "NegativeLookahead", 
    POS_BEHIND = "PositiveLookbehind", 
    NEG_BEHIND = "NegativeLookbehind"
)

Concat <- function(regexes) {
    if ( !is.list(regexes) ) regexes <- list(regexes)  # Handle singletons
    RegExpBranch("Concat", children = regexes)
}

makeConcat <- function(regexes) {
    # Create a Concat but a single regex should stand alone
    if ( length(regexes) == 1 ) {
        return( regexes[[1]] )
    }
    Concat(regexes)
}

Group <- function(regex, gtype, name = "") {
    # if( gtype == RegexGroup$NAMED ) {
    #     name <- ifelse(!is.null(name) && !is.na(name), name, "")
    # }
    RegExpBranch("Group", regex = regex, gtype = gtype, name = name)
}

Alternation <- function(regexes) {
    if ( !is.list(regexes) ) regexes <- list(regexes)  # Handle singletons
    RegExpBranch("Alternation", children = regexes)
}

Repetition <- function(regex, modtype, lazy = FALSE) {
    if( is.list(modtype) || is.numeric(modtype) || modtype == "{" || modtype == RegexModifier$RANGE ) {
        rtype <- RegexModifier$RANGE
        minimum <- 0
        maximum <- Inf

        if ( is.list(modtype) ) {
            if ( length(modtype) == 1 ) {
                minimum <- modtype[[1]]
                maximum <- modtype[[1]]
            } else {
                minimum <- modtype[[1]]
                maximum <- modtype[[2]]
            }
        } else if ( is.numeric(modtype) && length(modtype) > 0 ) {
            if ( length(modtype) == 1 ) {
                minimum <- modtype[1]
                maximum <- modtype[1]
            } else {
                minimum <- modtype[1]
                maximum <- modtype[2]
            }
        }
    } else if( modtype == "?" || modtype == RegexModifier$OPTIONAL ) {
        rtype <- RegexModifier$OPTIONAL
        minimum <- 0
        maximum <- 1
    } else if( modtype == "*" || modtype == RegexModifier$MANY ) {
        rtype <- RegexModifier$MANY
        minimum <- 0
        maximum <- Inf
    } else if( modtype == "+" || modtype == RegexModifier$MANY ) {
        rtype <- RegexModifier$SOME
        minimum <- 1
        maximum <- Inf
    } else {
        stop(str_glue("Unrecognized repetition modifier {modtype}"))
    }
    RegExpBranch("Repetition", child = regex, lazy = lazy, type = rtype,
                 minimum = minimum, maximum = maximum )
}

    # Not currently supported
# EXERCISE. Add support for the four lookaround assertions, here
# and in the main parser. Suggestion: write a parser function
# lookaround(regex) similar to group() below and put it in
# the main list.
Lookaround <- function(regex, atype) RegExpBranch("Lookaround", child = regex, type = atype)


#
# Helpers
#

some_str <- function(sp, sep = "") some(sp) %>>% function(rs) stri_join(map_chr(rs, identity), collapse = sep) 

join <- function(rs) {
    alternated <- list()
    concatenated <- list()
    last_literal <- NULL

    for( r in rs ) {
        if ( is(r, "NoOp") ) next

        # Merge consecutive Literals
        if ( is(r, "Literal") ) {
            if ( !is.null(last_literal) ) {
                combined <- stri_join(last_literal@text, r@text, collapse = "")
                last_literal <- Literal(combined)
            } else {
                last_literal <- r
            }
            next
        } else if ( !is.null(last_literal) ) {
            concatenated <- list.append(concatenated, last_literal)
            last_literal <- NULL
        }

        # Handle alternation or just collect
        if ( is.character(r) && r == "|" && length(concatenated) == 0 ) {
            alternated <- list.append(alternated, Literal(""))
        } else if ( is.character(r) && r == "|" ) {
            alternated <- list.append(alternated, makeConcat(concatenated))
            concatenated <- list()
        } else if ( length(concatenated) == 0 && is(r, "Concat") ) {
            # ATTN: In general, can splice r@children into concatenated when len > 0 too
            concatenated <- r@children
        } else {
            concatenated <- list.append(concatenated, r)
        }
    }

    # Clean up pending literal
    if ( !is.null(last_literal) ) {
        concatenated <- list.append(concatenated, last_literal)
    }
    # Clean up pending concats
    if ( length(concatenated) > 0 ) {
        alternated <- list.append(alternated, makeConcat(concatenated))
    } else {
        alternated <- list.append(alternated, Literal(""))
    }
    # No alternation if just one regex
    if( length(alternated) == 1 ) {
        return( alternated[[1]] )
    }
    Alternation(alternated)
}


#
# Regex Parser Components
#

LITERAL_CHARS <- "[^\\]\\[?*+.|^$(){}\\\\]"
META_CHARS <- "[\\]\\[?*+.|^$(){}\\\\]"

# Escape characters of escape characters, literal text
unescape <- sjoin(char("\\"), char("\\")) %>>% Literal
unescapes <- some_str(sjoin(char("\\"), char("\\"))) %>>% Literal

# An escaped metacharacter
escaped <- follows(char("\\"), re(META_CHARS)) %>>% Literal

# Literal char or text
literal_char <- re(LITERAL_CHARS) %>>% Literal
literal <- re(str_glue("{LITERAL_CHARS}+")) %>>% Literal

# Special escape sequences
special <- follows(char("\\"), char_in(VALID_ESCAPES)) %>>% EscapeSequence

# Zero-length assertions without arguments
assertion <- string_in(VALID_ASSERTIONS) %>>% Assertion

# Character classes
cclass <- between(char("["), re("\\^?\\]?[^\\]]+"), char("]")) %>>% CharacterClass

egroup <- char(")")
bgroup <- follows(
    char("("),
    optional(
        alts(
            use( string("?:"), c(RegexGroup$PLAIN, "") ),
            re("\\?P<([-A-Za-z_]+)>", group=1) %>>% function(name) c(RegexGroup$NAMED, name)
        ),
        c(RegexGroup$CAPTURE, "")
    )
)

group <- function(regexp) {
    # Parser matching a group around another regex.
    followedBy(pseq(bgroup, regexp), egroup) %>>% 
                 function(b_r) Group(b_r[[2]], b_r[[1]][[1]], b_r[[1]][[2]])
}

# Repetition modifiers
repeats <- alts(
    char("?"),
    char("*"),
    char("+"),
    between(
        char("{"),
        natural_number %>>=% function(m) pseq(pure(m),
                                              optional(follows(char(","), natural_number), m)),
        char("}"))
)

req_modifier <- pseq(repeats, optional(char("?")))
opt_modifier <- optional(req_modifier)

# Helpers for aggregate parsers

alternation <- function(regexp) {
    # Note: Alternation reaches all the way to the enclosing group
    follows(char("|"), regexp) %>>% Alternation
}

repetition <- function(p) {
    wrap_modifier <- function(base_repl) {
        basic <- base_repl[[1]]
        repl <- base_repl[[2]]
        if ( identical(repl, NA) ) {
            return( basic )
        }
        # Have a modifier, interpret it
        rep <- repl[[1]]
        lazy <- repl[[2]]
        is_lazy = !identical(lazy, NA)
        if ( is(basic, "Literal") && str_length(basic@text) > 1 ) {
            # Manage last character, e.g., abc* -> Concat(ab, Repetition(c, '*'))
            head = Literal(stri_sub(basic@text, 1, -2))
            tail = Repetition(Literal(stri_sub(basic@text, -1, -1)), rep, is_lazy)
            return( Concat(list(head, tail)) )
        }
        Repetition(basic, rep, lazy=is_lazy)
    }
    pseq(p, opt_modifier) %>>% wrap_modifier
}

base <- function(regexp) {
    # Regex components that can be distinguished by their prefix.
    alts(
        repetition(unescapes),
        repetition(special),
        assertion,
        repetition(escaped),
        repetition(char(".")),
        repetition(literal),
        repetition(cclass),
        repetition(group(regexp))
    )
}

#
# Main Regex Parser
#

regexp <- function(regexp) {
    # Full regular expression parser.
    term = alt(base(regexp), char("|"))
    some(term) %>>% join
}
regexp <- fixZ(regexp)

parse_regexp <- function(re_str) {
    # Parses a string encoding a regular expression, returning a RegExp tree on success.
    #  
    # Raises an error if parsing fails.
    #
    parsed <- parse(re_str, regexp)
    if ( failed(parsed) ) {
        stop(str_glue("Regex parsing failed at position {parsed@pos}: {parsed@message}"))
    }
    parsed@result
}
