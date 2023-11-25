library(testthat)
library(stringr)
library(rlang)
library(purrr)

source("combinators.r")

#
# Helpers
#

id <- function(x) x

str_cat <- function(strs) str_c(strs, collapse = "")

run <- function(input, p, f = id) {
    parsed <- parse(input, p)
    if ( failed(parsed) ) {
        stop(str_glue("Parse failed at {parsed@pos}: {parsed@message}"))
    }
    f(parse(input, p)@result)
}

expect_all_equal <- function(object, vec) {
    act <- quasi_label(rlang::enquo(object), arg = "object")
    exp <- quasi_label(rlang::enquo(object), arg = "vec")

    n <- length(exp$val)
    act$n <- length(act$val)
    act$diffs <- act$val == exp$val
    reason <- ifelse(act$n == n,
                     str_glue(" starting in position {which.min(act$diffs)}"),
                     str_glue(" in length ({act$n} != {n})" ))
    expect(
        act$n == n && all(act$diffs),
        str_glue("{act$lab} and {exp$lab} differ{reason}" )
    )

    invisible(act$val)
}

expect_list_equal <- function(object, lst) {
    act <- quasi_label(rlang::enquo(object), arg = "object")
    exp <- quasi_label(rlang::enquo(object), arg = "lst")

    n <- length(exp$val)
    act$n <- length(act$val)
    diff <- n + 1
    for ( i in 1:min(n, act$n) ) {
        if ( act$val[[i]] !=  exp$val[[i]] ) {
            diff <- i
            break
        }
    }
    act$diff <- diff
    reason <- ifelse(act$n == n,
                     str_glue(" starting in position {act$diff}"),
                     str_glue(" in length ({act$n} != {n})" ))
    expect(
        act$n == n && act$diff > n,
        str_glue("{act$lab} and {exp$lab} differ{reason}" )
    )

    invisible(act$val)
}

as_vec <- function(ls, f) {
    return( f(ls, id) )
}

as_int_vec <- function(ls) as_vec(ls, map_int)
as_chr_vec <- function(ls) as_vec(ls, map_chr)

#
# Tests
#

test_that("basic parser tests", {
    expect_equal( run('abc', pure(4)), 4 )
    expect_equal( parse('abc', pure(4))@state@point, 1 )
    expect_equal( run('abc', use(char('a'), 10)), 10)
    expect_true( run('', eof) )
    expect_error( run('a', eof) )

    expect_equal( run('10, 20, 30', char('1')), '1' )
    expect_equal( run('10, 20, 30', re('[0-9]+')), '10' )
    expect_equal( run('10, 20, 30', re('[0-9]+') %>>% strtoi), 10 )

    expect_equal( run('xyz', char_in(c('u', 'x', 'a'))), 'x' )
    expect_equal( run('yxz', char_not_in(c('u', 'x', 'a'))), 'y' )

    expect_equal( run('A', char_satisfies(function(c) c ==  toupper(c))), 'A' )
    expect_equal( run('!', char_satisfies(function(c) c == '!')), '!' )

    expect_equal( run('abc', string('abc')), 'abc' )
    expect_equal( run('aBc', istring('abc')), 'aBc' )
    expect_equal( run('bar', strings('foo', 'bar', 'zap')), 'bar' )

    expect_equal( run('   ', hspace), '   ' )
    expect_equal( run('\n', vspace), '\n' )
    expect_error( run("\n  ", hspace) )

    expect_true( run("true", boolean) )
    expect_true( run('yes', boolean) )
    expect_false( run('no', boolean) )
    expect_false( run('FALSE', boolean) )

    expect_equal( run('100', integer), 100 )
    expect_equal( run('-100', integer), -100 )
    expect_equal( run('-100.', integer), -100 )
    expect_equal( run('1009', integer), 1009 )
    expect_equal( run('100.', natural_number), 100 )
})

test_that("sequencing combinators", {
    expect_all_equal( as_chr_vec(run('abbbbb', pseq(any_char, re('b+')))), c('a', 'bbbbb') )
    expect_equal( run('100    a', pseq(followedBy(integer, space), char('a')))[[1]], 100 )
    expect_equal( run('100    a', pseq(followedBy(integer, space), char('a')))[[2]], 'a' )
    expect_length( run('100    a', pseq(followedBy(integer, space), char('a'))), 2 )
    expect_list_equal( run('100yes-10a', chain(natural_number, boolean, integer, any_char)), list(100, True, -10, 'a') )

    expect_equal( run('[abc]', between(char('['), string('abc'), char(']'))), 'abc' )
    expect_equal( run('[abc]', between(char('['), sjoin(char('a'), char('b'), char('c')), char(']'))), 'abc' )
    expect_all_equal( as_chr_vec(run('a, b, crg', interleave(fmap(letters, str_cat), symbol(',', hspace)))), c('a', 'b', 'crg') )
    expect_all_equal( as_chr_vec(run('a, b, crg', interleave(string_in(c('a', 'x', 'b', 'bb', 'c', 'crg')), symbol(',')))), c('a', 'b', 'crg') )

    list_of_ints <- interleave(natural_number, string(', '), start=char('['), end=char(']'), allow.empty = TRUE)
    expect_all_equal( run('[10, 20, 30]', list_of_ints, as_int_vec), c(10, 20, 30) )
    expect_all_equal( run('[10]', list_of_ints, as_int_vec), c(10) )
    expect_length( run('[]', list_of_ints), 0)
})

test_that("alternation", {
    expect_equal( run('abbbbb', alt(char('a'), char('c'))), 'a' )
    expect_equal( parse('abbbbb', alt(char('a'), char('c')))@state@point, 2 )
    expect_equal( run('cbbbbb', alt(char('a'), char('c'))), 'c' )
    expect_equal( run('X', alts(letter, digit, newline)), 'X' )
    expect_equal( run('9', alts(letter, digit, newline)), '9' )
    expect_equal( run('\n', alts(letter, digit, newline)), '\n' )
    expect_error( run(' ', alts(letter, digit, newline)) )
})

test_that("repetition combinators", {
    expect_all_equal( run('aaaaa', many(char('a')), as_chr_vec), rep('a', 5) )
    expect_length( run('', many(char('a'))), 0 )
    expect_all_equal( run('aaaaa', some(char('a')), as_chr_vec), rep('a', 5) )
    expect_all_equal( run('aaaaa', repeated(char('a'), 3, 5), as_chr_vec), rep('a', 5) )
    expect_all_equal( run('aaaaa', repeated(char('a'), 5, 5), as_chr_vec), rep('a', 5) )
    expect_all_equal( run('aaaaa', repeated(char('a'), 5, 9), as_chr_vec), rep('a', 5) )
})

test_that("recursion", {
    ident <- re('[A-Za-z_][-A-Za-z_0-9?!]*')

    # First we show incomplete recursion up to a bounded depth
    sexpB <- function(p) parser(alts(ident, integer, interleave(p, space, start=char('('), end=char(')'))), "sexpB")

    sB <- parse('(a b (c r g) ((d)) efg_32)', sexpB(sexpB(sexpB(ident))))
    expect_false( failed(sB) )
    expect_equal( sB@result[[1]], "a" )
    expect_equal( sB@result[[2]], "b" )
    expect_equal( sB@result[[4]][[1]][[1]], "d" )
    expect_equal( sB@result[[3]][[1]], "c" )
    expect_equal( sB@result[[3]][[2]], "r" )
    expect_equal( sB@result[[3]][[3]], "g" )
    expect_equal( sB@result[[5]], "efg_32" )

    # Now full recursion using fix()
    sexp <- fixZ(function(sexp) { function(state) alt(ident, interleave(sexp, space, start=char('('), end=char(')')))(state) })

    s <- parse('(a b (c r g) ((d)) efg_32)', sexp)
    expect_false( failed(s) )
    expect_equal( s@result[[1]], "a" )
    expect_equal( s@result[[2]], "b" )
    expect_equal( s@result[[4]][[1]][[1]], "d" )
    expect_equal( s@result[[3]][[1]], "c" )
    expect_equal( s@result[[3]][[2]], "r" )
    expect_equal( s@result[[3]][[3]], "g" )
    expect_equal( s@result[[5]], "efg_32" )

    sf <- parse('(a b (c r g) (($)) efg_32)', sexp)
    expect_true( failed(sf) )
    expect_equal( sf@pos, 14 )
})
