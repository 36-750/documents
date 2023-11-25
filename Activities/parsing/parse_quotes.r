# A parser for a quoted string with escape sequences.

library(stringr)
source("./combinators.r")

sconcat <- function(strs, sep = "") str_c(strs, collapse = sep)
esc_seq <- function(c) switch(c, n="\n", t="\t", r="\r", a="\a", v="\v", f="\f", c)
cat_choice <- function(...) many(alts(...)) %>>% sconcat

unescapes <- some(strings(char('\\'), char('\\'))) %>>% sconcat
escaped <- follows(char("\\"), any_char) %>>% esc_seq
quote <- char('"')
non_quote <- char_not_in(c('"', '\\'))

quoted <- between(
    quote, 
    cat_choice(
        unescapes,
        escaped,
        some(non_quote) %>>% sconcat
    ),
    quote
)

parse_quoted <- function(s) {
    parsed <- parse(s, quoted)
    if ( failed(parsed) ) {
        stop(str_glue("quoted string could not be parsed (pos={parsed@pos}): {parsed@message}"))
    }
    parsed@result
}

# EXERCISE. Use this to create a simple parser for a line in a CSV file
# and then for the contents of a CSV file. Consider two extended tasks:
# 1. using pipe, make the parser fail if any line has too many/few fields,
# 2. extend the parser to take a specification in of field types and
# make the parser both sensitive to the types and return values of
# the right type.  (You can keep the types simple, like: boolean,
# natural, integer, real, string, date, hexcolor, ....)

# EXERCISE. Modify this implementation to handle the double-char escape
# style of escaping quotes in strings. For instance "" inside a string
# would escape the quotes, e.g., "abc""def" is the string with seven
# characters,  the middle of which is a quote. So, \ would not act
# as an escape character (except if you support designated escape sequences).

# EXERCISE. Modify this implementation to handle different types of quoting
# characters that act as delimiters. For instance, you can use "'q as distinct
# quoting characters, which allows for nested strings more easily. The
# delimiters must be matched, e.g., qABc"what'the'heck"etcq or the like.

# EXERCISE. Modify this implementation to support string interpolation
# within the string. Expressions within a balanced {...} expression
# within the quotes would be replaced by the string form of the
# evaluated expression. Take an environment (defaulting to the caller's
# environment) in which to evaluate the expression. This nicely uses
# R's capabilities.
