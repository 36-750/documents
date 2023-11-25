#
# A quick implementation of parser combinators
#

library(stringr)
library(purrr)
library(rlang)
library(rlist)


#
# Parse State
#

setGeneric("view", function(object, ...) standardGeneric("view"))
setGeneric("require", function(object, ...) standardGeneric("require"))
setGeneric("advance", function(object, ...) standardGeneric("advance"))

# EXERCISE. ParseState takes source to be type character. Adjust the implementation
#     to handle types text and binary data so that binary files can be parsed.
#     What needs to change? What is coupled here? Note that this does not
#     require that you change string parsers below to handle both, just that
#     you can parse sources that are binary or text.

setClass("ParseState", slots = c(source = "character", point = "numeric", start = "numeric"))

setValidity("ParseState",
            function(object) {
                n <- str_length(object@source)
                point_ok <- object@point > 0 && object@point <=  n + 1
                start_ok <- object@start > 0 && object@start <= object@point
                
                if ( point_ok && start_ok ) {
                    return( TRUE )
                } else if ( point_ok ) {
                    return( "ParseState@start is out of range" )
                }
                return( "ParseState@point is out of range" )
            })

setMethod("initialize", "ParseState",
          function(.Object, source, point = 1, start = point, ...) {
              .Object <- callNextMethod(.Object, ... )
              n <- str_length(source)
              if ( point <= 0 ) {
                  .Object@point <- max(n + 1 + point, 1)
              } else {
                  .Object@point <- min(point, n + 1)
              }
              .Object@start <- max(min(start, .Object@point), 1)
              .Object@source <- source
              validObject(.Object)
              .Object
          })

setMethod("view", c("ParseState"), function(object, maxlen = -1) {
              n <- str_length(object@source)
              if ( maxlen < 0 ) {
                  end <- n
              } else {
                  end <- min(object@point + maxlen - 1, n)
              }
              return( str_sub(object@source, object@point, end) )
          })

setMethod("require", c("ParseState"), function(object, size) {
              n <- str_length(object@source)
              if ( object@point + size > n + 1 ) {
                  return( list(mesg = str_glue("Required {size} characters but only {n - object@point + 1} remain."),
                               enough = FALSE) )
              }
              return( list(input = view(object, size), enough = TRUE) )
          })

setMethod("advance", c("ParseState"), function(object, by = 0) {
              if ( by == 0 ) {
                  return( object )
              }
              return( ParseState(object@source, object@point + by, object@start) )
          })


ParseState <- function(source, point = 1, start = point) {
    return( new("ParseState", source, point, start) )
}


#
# ParseResult and its substypes
#

setClass("ParseResult", slots = c(type = "character"))
setClass("Success", slots = c(result = "ANY", state = "ParseState"), contains = "ParseResult")
setClass("Failure", slots = c(message = "character", pos = "numeric", data = "list"), contains = "ParseResult")

SUCCESS <- "Success"
FAILURE <- "Failure"

Success <- function(result, state) {
    return( new("Success", type = SUCCESS, result = result, state = state) )
}

Failure <- function(mesg, pos, data = list()) {
    return( new("Failure", type = FAILURE, message = mesg, pos = pos, data = data) )
}


#
# Infrastructure
#

# failed : ParseResult a -> Boolean tests if a parse has failed
#
failed <- function(parsed) {
    return( parsed@type == FAILURE )
}

# succeeded : ParseResult a -> Boolean tests if a parse has succeeded
#
succeeded <- function(parsed) {
    return( parsed@type == SUCCEEDED )
}

# plabel can get and set the label associated with a parser
plabel <- function(parser) {
    label <- attr(parser, "parser-label")
    if ( is.null(label) ) return( "?" )
    return( label )
}

`plabel<-` <- function(x, value) {
    attr(x, "parser-label") <- value
    return( x )
}


#
# Parser Creation
#

.wrap.parser <- function(f, label) {
    plabel(f) <- label
    return( f )
}

# Creates a parser from a parsing function
# 
# At the moment, this just associates a label to
# a parsing function and returns the function.
#
parser <- function(f, label = "?" ) {
    return( .wrap.parser(f, label) )
}

# Defines (and assigns) a parser from a name and code block.
#
# `name` is a symbol (unevaluated identifier)
# `code` is either a code block or an expression `sym -> {code}`.
#     Both define a function from ParseState to ParseResult.
#     In the former case, the parse state is bound to the
#     symbol `.state`. In the latter (hygenic) case, the
#     symbol sym is used as the argument to the function,
#     preventing inadvertent capture of the state variable.
# `desc` is a string used to construct the parser label;
#     it is inserted into a string of the form name(desc).
#
#  This defines the parsing function and *assigns* it to
#  the symbol specified by name. If used at the top
#  level it defines the parser in the global environment.
#  If used within an outer function, it defines the parser
#  locally using the caller's environment to interpret
#  the code. A common pattern for parser factories is
#
#      a_parser <- function(params) {
#                      desc <- "description from params"
#                      def.parser(a_parser, {
#                          ...code using .state
#                      }, desc)
#                  }
#
#  The use of the same symbol for the function and parser
#  names is a feature not a bug; it labels the parser
#  after the parser factory.
#
def.parser <- function(name, code, desc = "") {
    parser.name <- ensym(name)
    spec <- enexpr(code)
    if ( desc == "" ) {
        label <- as_string(parser.name)
    } else {
        label <- str_glue("{as_string(parser.name)}({desc})")
    }

    if ( is_call(spec, "<-") ) {
        if( is_call(spec[[2]], "{") && is_symbol(spec[[3]]) ) {
            state <- as_string(spec[[3]])
            body <- spec[[2]]
        } else {
            stop(str_glue("Improperly specified parser {spec}"))
        }
    } else {
        state <- ".state"
        body <- spec
    }

    args <- list()
    args[[state]] <- missing_arg()
    p <- .wrap.parser(new_function(args, body, caller_env()), label)
    return( eval(expr(!!parser.name <- !!p), caller_env()) )
}


#
# Helpers
#

# The Z-combinator for finding fixed points in an eager language.
# The first is the combinator itself, and the second is the
# combinator converted to a recursive function. The latter
# *might* be more efficient, but it does not work with Recall
# and so cannot be renamed.
#
# Example:
#  ident <- re(r'[A-Za-z_][-A-Za-z_0-9?!]*')
#  opar <- char('(')
#  cpar <- char(')')
#
#  sexp <- fixZ(function(sexp) alt(ident, interleave(sexp, space, start=opar, end=cpar)))
#
#  parse('(a b (c r g) ((d)) (e (f (g))))', sexp)  #=> succeeds
#  parse('(a b (c r g) (($)) (e (f (g))))', sexp)  #=> fails at the correct point
#
fixZ <- function(f) {
    z <- function(u) f(function(x) u(u)(x))
    z(z)
}

fixZrec <- function(f) {
    function(x) f(fixZrec(f))(x)
}


#
# Fundamental Parsers, Parser Factories, and Operators
#

# A Parser that always fails.
#
def.parser(void, Failure("void parser", .state@point))

# A parser that always fails with a specified reason.
#
failure <- function(reason = "void parser") {
    label <- str_glue("\"{reason}\"")
    def.parser(failure, Failure(reason, .state@point), label)
}

# pure : (x: a) -> Parser a
# A parser that immediately succeeds with the given value.
#
# This matches the empty string; source position is not advanced.
#
pure <- function(x) def.parser(pure, Success(x, .state), deparse(x))

# fmap : Parser a -> (a -> b) -> Parser b
# A parser that transforms a successful result of the given parser by a function
#
fmap <- function(p, f) {
    label <- plabel(p)
    def.parser(fmap, {
        parseA <- p(.state)
        if ( failed(parseA) ) {
            return( parseA )
        }
        Success(f(parseA@result), parseA@state)
    }, label)
}

# pipe : Parser a -> (a -> Parser b) -> Parser b
# A parser that sequences two parsers, where the second depends on the result of the first
#
pipe <- function(p, f) {
    label <- plabel(p)
    def.parser(pipe, {
        parseA <- p(.state)
        if ( failed(parseA) ) {
            return( parseA )
        }
        return( f(parseA@result)(parseA@state) )
    }, label)
}

# use: Parser a -> b -> Parser b
# A parser that yields a specified value when the given parser succeeds
use <- function(p, value) {
    label <- str_glue("use({value}, {plabel(p)})")
    parser(fmap(p, function(result_) value), label)
}


# Operators for fmap and pipe
#
`%>>%` <- function(p, f) fmap(p, f)
`%>>=%` <- function(p, f) pipe(p, f)

#
# Higher-Order Combinators
#
# EXERCISE. Implement additional parser combinators or factories that
#     are usable (and reusable) in practical situations. For instance,
#     parsing LaTeX commands, parsing R statistical model expressions,
#     combinators for expressing command line options, ....

# seq : Parser a -> Parser b -> Parser (a, b)
# A parser that runs two parsers in sequence, collecting the results.
#
pseq <- function(p, q) {
    label <- str_glue("pseq({plabel(p)}, {plabel(q)})")
    sequenced <- pipe(p, function(x) pipe(q, function(y) pure(list(x, y))))
    return( parser(sequenced, label) )
}

# followedBy : Parser a -> Parser b -> Parser a
# A parser that runs two parsers in order but yields only the result of the first
#
followedBy <- function(p, q) {
    label <- str_glue("followedBy({plabel(p)}, {plabel(q)})")
    sequenced <- pipe(p, function(x) pipe(q, function(y) pure(x)))
    return( parser(sequenced, label) )
}

# follows : Parser a -> Parser b -> Parser b
# A parser that runs two parsers in order but yields only the result of the second
#
follows <- function(p, q) {
    label <- str_glue("follows({plabel(p)}, {plabel(q)})")
    sequenced <- pipe(p, function(x) pipe(q, function(y) pure(y)))
    return( parser(sequenced, label) )
}

# between : Parser a -> Parser b -> Parser c -> Parser b
# A parser that runs three parsers in order but yields only the middle result
#
between <- function(p, q, r) {
    label <- str_glue("between({plabel(p)}, {plabel(q)}, {plabel(r)})")
    sequenced <- followedBy(follows(p, q), r)
    return( parser(sequenced, label) )
}

# Operators for seq, followedB, and follows (_ for ignored)
#
`%::%` <- function(p, q) pseq(p, q)
`%:_%` <- function(p, q) followedBy(p, q)
`%_:%` <- function(p, q) follows(p, q)

# chain : List (Parser a*) -> Parser (List a*)
# A parser that runs a list of parsers in sequence and collects the results in a list.
# This fails immediately if any component parsers fail.
#
chain <- function(...) {
    ps <- list(...)
    label <- str_c(map(ps, plabel), collapse = ", ")
    def.parser(chain, {
        results <- vector("list", length(ps))
        state <- .state
        index <- 1
        for ( p in ps ) {
            parsed <- p(state)
            if ( failed(parsed) ) {
                return( Failure(str_glue("chained parse failed: {parsed@message}"),
                                parsed@pos, parsed@data) )
            }
            results[[index]] <- parsed@result
            state <- parsed@state
            index <- index + 1
        }
        Success(results, state)
    }, label)
}

# alt : Parser a -> Parser b -> Parser (a | b)
# A parser that matches one parser, or the other if that fails.
# The parsers are tried in order with the original state.
# Fails if both p and q fail, returning original state
#
alt <- function(p, q) {
    label <- str_glue("{plabel(p)}, {plabel(q)}")
    def.parser(alt, {
        parseA <- p(.state)
        if ( failed(parseA) ) {
            parseB <- q(.state)
            if ( failed(parseB) ) {
                point <- max(parseA@pos, parseB@pos)
                mesg <- str_glue("{label} failed: [{parseA@message}] and [{parseB@message}]")
                data <- c(parseA@data, parseB@data)
                return( Failure(mesg, point, data) )
            }
            return( parseB )
        }
        return( parseA )
    }, label)
}

`%|%` <- function(p, q) alt(p, q)

# alts : List (Parser a*) -> Parser a
# Parser that matches the first of the given parsers to succeed.
#
alts <- function(...) {
    ps <- list(...)
    label <- str_c(map(ps, plabel), collapse = ", ")
    def.parser(alts, {
        results <- vector("list", length(ps))
        farthest <- .state@point
        data <- list()
        positions <- c()
        mesg <- ""
        for ( p in ps ) {
            parsed <- p(.state)
            if ( failed(parsed) ) {
                if ( parsed@pos > farthest ) {
                    farthest <- parsed@pos
                    mesg <- parsed@message
                    data <- parsed@data
                }
                positions <- list.append(positions, parsed@pos)
            } else {
                return( parsed )                
            }
        }
        m <- str_glue("All alternatives failed: {mesg}")
        data[["failure-positions"]] <- positions
        Failure(m, farthest, data)
    }, label)
}

# optional: Parser a -> Parser (a | NULL)
# A parser that matches the given parser zero or one times
# Runs the given parser, returning its result on success or
# a default value on failure. Always succeeds.
#
optional <- function(p, default = NULL) {
    parser(alt(p, pure(default)), str_glue("optional({plabel(p)}, {default})"))
}

# many: Parser a -> Parser (List a)
# A parser that matches the given parser zero or more times
#
many <- function(p)
    def.parser(many, {
        results <- list()
        state1 <- .state
        while ( TRUE ) {
            parsed <- p(state1)
            if ( failed(parsed) ) {
                break
            }
            results <- list.append(results, parsed@result)
            state1 <- parsed@state
        }
        Success(results, state1)
    }, plabel(p))

# some: Parser a -> Parser (List a)
# A parser that matches the given parser one or more times
#
some <- function(p)
    def.parser(some, {
        parsed <- p(.state)
        if ( failed(parsed) ) {
            return( parsed )
        }
        rest <- many(p)(parsed@state)
        Success(list.prepend(rest@result, parsed@result), rest@state)
    }, plabel(p))

# repeated: Parser a -> [Integer] -> [Integer] -> Parser (List a)
# A parser that matches the given parser in an inclusive range of times.
#
repeated <- function(p, minimum = 0, maximum = .Machine$integer.max) {
    if ( minimum < 0 || minimum > maximum || maximum < 0 ) {
        stop("repeated parser requires non-negative minimum <= maximum")
    }
    def.parser(repeated, {
        reps <- 0
        state1 <- .state
        results <- list()
        while ( reps < maximum ) {
            parsed <- p(state1)
            if ( failed(parsed) ) {
                if ( reps < minimum ) {
                    mesg <- str_glue("repeated({plabel(p)}) parsed fewer than minimum ({minimum}) times: {parsed@message}")
                    return( Failure(mesg, parsed@pos, parsed@data) )
                }
                break
            }
            results <- list.append(results, parsed@result)
            state1 <- parsed@state
            reps <- reps + 1
        }
        Success(results, state1)
    })
}

# interleave: Parser a -> Parser b -> [Parser c] -> [Parser d] -> [Boolean] -> Parser (List a)
# A parser that interleaves items with separators and optional start/end delimiters.
#
# Returns a list of results from the `item` parser. The results of
# the `sep`, `start`, and `end` parsers are ignored. Note that when `end`
# is supplied, a match of `sep` is NOT required between the last item
# and the end.
#
# If `allow.empty` is TRUE, then an empty list of items is allowed. This is
# most useful if `start` or `end` is supplied.
#
interleave <- function(item, sep, end, start, allow.empty = FALSE) {
    label <- str_glue("{ifelse(!missing(start), str_c(plabel(start), ' '), '')}",
                      "{plabel(item)} {plabel(sep)}",
                      "{ifelse(!missing(end), str_c(plabel(end), ' '), '')}")
    have_start <- !missing(start)
    have_end <- !missing(end)
    def.parser(interleave, {
        state1 <- .state
        if ( have_start ) {
            parsed.start <- start(state1)
            if ( failed(parsed.start) ) {
                return( parsed.start )
            }
            state1 <- parsed.start@state
        }
        results <- list()
        item.state <- NULL

        while ( TRUE ) {
            parsed.item <- item(state1)
            if ( failed(parsed.item) ) {
                if ( is.null(item.state) && !allow.empty ) {
                    mesg <- str_glue("Expected items ({plabel(item)}) in interleave: {parsed.item@message}" )
                    return( Failure(mesg, parsed.item@pos, parsed.item@data) )
                }
                break
            }
            results <- list.append(results, parsed.item@result)
            state1 <- parsed.item@state
            item.state <- state1

            parsed.sep <- sep(state1)
            if ( failed(parsed.sep) ) {
                break
            }
            state1 <- parsed.sep@state
        }

        if ( have_end ) {
            parsed.end <- end(state1)
            if ( failed(parsed.end) ) {
                return( parsed.end )
            }
            return( Success(results, parsed.end@state) )
        }
        if ( is.null(item.state) ) {
            state <- state1
        } else {
            state <- item.state
        }
        Success(results, state)
    })
}

# peek: Parser a -> Parser a
# A parser that parses ahead without advancing the state.
#
peek <- function(p)
    def.parser(peek, {
        parsed <- p(.state)
        if ( failed(parsed) ) {
            return( parsed )
        }
        Success(parsed@result, .state)
    })


#
# Basic Parsers and Parser Factories
#

# eof : Parser Boolean
# A parser that only succeeds at the end of input.
#
def.parser(eof, {
    ahead <- require(.state, 1)
    if ( ahead$enough ) {
        return( Failure("Expected end of input", .state@point) )
    }
    Success(TRUE, .state)
})

# any_char : Parser String
# A parser that matches any single character
#
def.parser(any_char, {
    ahead <- require(.state, 1)
    if ( ahead$enough ) {
        return( Success(ahead$input, advance(.state, 1)) )
    }
    Failure("Expected a character", .state@point)
})

# space : Parser String
# A parser that matches any non-empty string of whitespace
#
def.parser(space, {
    m <- str_extract(view(.state), '^\\s+')
    if ( is.na(m) ) {
        return( Failure("Expected whitespace", .state@point) )
    }
    Success(m, advance(.state, str_length(m)) )
})

# hspace : Parser String
# A parser that matches any non-empty string of horizontal whitespace
#
def.parser(hspace, {
    m <- str_extract(view(.state), '^[^\\S\n\v\f\r\u2028\u2029]+')
    if ( is.na(m) ) {
        return( Failure("Expected horizontal space", .state@point) )
    }
    Success(m, advance(.state, str_length(m)) )
})

# vspace : Parser String
# A parser that matches any non-empty string of vertical whitespace
#
def.parser(vspace, {
    m <- str_extract(view(.state), '^[\n\v\f\r\u2028\u2029]+')
    if ( is.na(m) ) {
        return( Failure("Expected vertical space", .state@point) )
    }
    Success(m, advance(.state, str_length(m)) )
})

# char : Char -> Parser String
# A parser that matches a specific character.
#
char <- function(ch)
    def.parser(char, {
        v <- require(.state, 1)
        if ( v$enough && ch == v$input ) {
            return( Success(ch, advance(.state, 1)) )
        }
        err <- str_glue("Expected character {ch}")
        Failure(err, .state@point, list(expected = ch))
    }, ch)

# char_in : Iterable Char -> Parser String
# A parser that matches a character in a specified set
#
char_in <- function(chars)
    def.parser(char_in, {
        v <- require(.state, 1)
        if ( v$enough && v$input %in% chars ) {
            return( Success(v$input, advance(.state, 1)) )
        }
        err <- str_glue("Expected character in {chars}")
        Failure(err, .state@point, list(expected = chars))
    }, str_c(chars, collapse = ""))

# char_not_in : Iterable Char -> Parser String
# A parser that matches a character NOT in a specified set
#
char_not_in <- function(chars)
    def.parser(char_not_in, {
        v <- require(.state, 1)
        if ( v$enough && !(v$input %in% chars) ) {
            return( Success(v$input, advance(.state, 1)) )
        }
        err <- str_glue("Expected character not in {chars}")
        Failure(err, .state@point, list(not.expected = chars))
    }, str_c(chars, collapse = ""))

# char_satisfies : (String -> Boolean) -> Parser String
# A parser that matches a character that satisfies a predicate.
#
char_satisfies <- function(pred, description = 'predicate')
    def.parser(char_satisfies, {
        v <- require(.state, 1)
        if ( v$enough && pred(v$input) ) {
            return( Success(v$input, advance(.state, 1)) )
        }
        err <- str_glue("Expected character satisfying {description}")
        Failure(err, .state@point)
    }, description)

# string: String -> Parser String
# A parser that matches a specific string
#
# If transform is supplied, it should be a function str -> str.
# The transform is applied to the input before comparing with the
# given string. Ex: transform=tolower with a lowercase string
# gives case insensitive comparison.
#
string <- function(s, transform=function(x) x) {
    n <- str_length(s)
    def.parser(string, {
        v <- require(.state, n)
        if ( !v$enough || transform(v$input) != s ) {
            return( Failure(str_glue("Expected string '{s}'"), .state@point) )
        }
        Success(v$input, advance(.state, n))
    })
}

# A parser like `string` but with case-insensitive comparison
#
istring <- function(s)
    parser(string(tolower(s), tolower), str_glue('istring({s})'))

# symbol: String -> Parser String -> Parser String
# Parser that matches a given sting followed by some notion of 'space'.
#
# The space is determined by the supplied parser `spacep` which parses
# the input after the string. The results of this parser are ignored.
# This defaults to capturing any sequence of whitespace.
#
# This is a convenience method for defining lexical components that
# account for whitespace.
#
symbol <- function(s, spacep = space) {
    string(s) %:_% spacep
}

# string_in: Iterable String -> Parser String
# A parser that matches a string in a specified set
#
string_in <- function(strs) {
    sorted <- order(map_int(strs, str_length), decreasing=TRUE)
    joined <- str_c(map_chr(strs[sorted], str_escape), collapse = "|" )
    def.parser(string.in, {
        input <- view(.state)
        m <- str_extract(input, regex(joined))
        if ( is.na(m) ) {
            mesg <- str_glue("Expected on of {str_c(strs[sorted], collapse=',  ')}")
            return( Failure(mesg, .state@point, list(expected = strs)) )
        }
        Success(m, advance(.state, str_length(m)))
    })
}

# strings: String* -> Parser String
# A parser like `string_in` but accepts distinct string arguments.
#
strings <- function(...) {
    choices <- list(...)
    parser(string_in(choices), str_glue("strings({str_c(choices, collapse='')})" ) )
}

# sjoin: Iterable String -> Parser String
# A parser that matches a sequence of strings in order, joining the results
#
sjoin <- function(..., sep = "") {
    pstrs <- list(...)
    def.parser(sjoin, {
        state1 <- .state
        concat <- vector("character", length(pstrs))
        index <- 1
        for ( p in pstrs ) {
            parsed <- p(state1)
            if ( failed(parsed) ) {
                mesg <- str_glue("In sjoin, {plabel(p)} failed: {parsed@message}")
                return( Failure(mesg, parsed@pos, parsed@data) )
            }
            concat[index] <- parsed@result
            state1 <- parsed@state
            index <- index + 1
        }
        joined <- str_c(concat, collapse = sep)
        Success(joined, state1)
    })
}

# re: Regex -> Parser String
# A parser that matches a string satisfying a given regular expression.
#
# pattern: a string specifying the regular expression
# group: an integer or vector of integers indicating the match groups to return.
#     If not supplied, the entire match is return. A group of 0 corresponds
#     to the whole match.
# ignore_case, multiline, comments, dotall -- boolean arguments corresponding
#     to the traditional regex flags, as in `stringr::regex`.
#
re <- function(regexp, group = NULL, ignore_case = FALSE,
               multiline = FALSE, comments = FALSE,
               dotall = FALSE) {
    pattern <- ifelse(str_starts(regexp, fixed("^")), regexp, str_c("^", regexp))
    label <- str_glue("/{pattern}/[{group}]") # Convert flags eventually
    def.parser(re, {
        input <- view(.state)
        m <- str_extract(input,
                         regex(pattern, ignore_case = ignore_case,
                               multiline = multiline, comments = comments,
                               dotall = dotall),
                         group = c(0, group))
        if ( is.na(m) ) {
            mesg <- str_glue("Expected regex match /{pattern}/")
            data <- list(pattern = pattern,
                         ignore_case = ignore_case,
                         multiline = multiline, comments = comments,
                         dotall = dotall)
            return( Failure(mesg, .state@point, data) )
        }
        match <- ifelse(is.null(group), m, m[-1])
        Success(match, advance(.state, str_length(m[1])))
    })
}

# Common Lexical Parsers
#
newline <- parser(re('\r?\n'), 'newline')
letter <- parser(char_satisfies(function(s) str_starts(s, '[:alpha:]')), 'letter')
letters <- parser(char_satisfies(function(s) str_starts(s, '[:alpha:]+')), 'letters')
digit <- parser(char_satisfies(function(s) str_starts(s, '[:digit:]')), 'digit')
digits <- parser(char_satisfies(function(s) str_starts(s, '[:digit:]+')), 'digits')

natural_number <- parser(re('(?:[1-9][0-9]*|0)') %>>% strtoi, 'natural')
integer <- parser(re('(?:-?[1-9][0-9]*|0)') %>>% strtoi, 'integer')
boolean <- parser(re('true|false|yes|no|0|1', ignore_case = TRUE) %>>% function(s)
                      ifelse(str_sub(tolower(s), 1, 1) %in% c("t", "y", "1"), TRUE, FALSE))


#
# Convenient Entrypoint
#

# Parses an input string with a given parser and optional start position.
#
parse <- function(input, p, start=1) {
    return( p(ParseState(input, start)) )
}
